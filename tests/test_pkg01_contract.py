from concurrent.futures import Future
from types import SimpleNamespace
import pytest
from app.desktop_governed_image_preview_coordinator import GovernedImagePreviewCoordinator

class ManualExecutor:
    def __init__(self): self.jobs=[]
    def submit(self, fn,*args):
        f=Future();self.jobs.append((f,fn,args));return f
    def complete(self,index):
        f,fn,args=self.jobs[index]
        try:f.set_result(fn(*args))
        except Exception as e:f.set_exception(e)
    def shutdown(self,**kw): pass

class Viewer:
    def __init__(self): self.artifacts=();self.rendered=[];self.open_error=False;self.render_error=False;self.accept=True
    def open(self,arts):
        if self.open_error: raise RuntimeError('open failed')
        self.artifacts=arts
    def render_preview(self,art,payload,content_type):
        if self.render_error: raise RuntimeError('render failed')
        self.rendered.append(art);return self.accept
class Dispatcher:
    def __init__(self):self.queue=[];self.error=False
    def post(self,fn):
        if self.error:raise RuntimeError('post failed')
        self.queue.append(fn)
    def drain(self):
        while self.queue:self.queue.pop(0)()

def setup(fetcher=None):
    v=Viewer();d=Dispatcher();e=ManualExecutor()
    c=GovernedImagePreviewCoordinator(viewer=v,dispatcher=d,executor=e,fetcher=fetcher or (lambda *_:(b'png','image/png')))
    return c,v,d,e

def arts(n):return tuple(SimpleNamespace(preview_url=f'https://example.test/{i}') for i in range(n))

def test_reserve_ordinals_before_fetch_and_out_of_order():
    c,v,d,e=setup();a=arts(3);c.present(a)
    assert [r.visible_ordinal for r in c.results]==[1,2,3]
    assert [r.state for r in c.results]==['FETCH_PENDING']*3
    for i in [2,0,1]:e.complete(i)
    d.drain()
    assert [r.state for r in c.results]==['DELIVERED']*3
    assert v.rendered==[a[2],a[0],a[1]]

def test_repeated_same_object_reserves_distinct_occurrences():
    c,v,d,e=setup();a=arts(1)[0];c.present((a,a))
    assert len(c.results)==2
    assert c.results[0].slot_id!=c.results[1].slot_id
    assert c.results[0].artifact_id==c.results[1].artifact_id
    e.complete(0);e.complete(1);d.drain()
    assert len(v.rendered)==2

def test_cancel_drops_late_delivery():
    c,v,d,e=setup();c.present(arts(1));e.complete(0);c.cancel();d.drain()
    assert not v.rendered and c.results[0].state=='CANCELLED'

def test_new_presentation_drops_stale():
    c,v,d,e=setup();c.present(arts(1));c.present(arts(1))
    e.complete(0);e.complete(1);d.drain()
    assert len(v.rendered)==1 and c.results[-1].presentation_id==2 and c.results[0].state=='SUPERSEDED'

def test_retry_new_attempt():
    calls=[0]
    def fetch(*_):
        calls[0]+=1
        if calls[0]==1:raise OSError('offline')
        return b'png','image/png'
    c,v,d,e=setup(fetch);c.present(arts(1));e.complete(0)
    old=c.results[0].attempt_id
    assert c.results[0].state=='FAILED' and c.retry(1)
    assert c.results[0].attempt_id!=old
    e.complete(1);d.drain();assert c.results[0].state=='DELIVERED'
    assert not c.retry(1)

def test_render_rejection_and_exception():
    c,v,d,e=setup();v.accept=False;c.present(arts(1));e.complete(0);d.drain()
    assert c.results[0].state=='REJECTED'
    v.render_error=True;assert c.retry(1);e.complete(1);d.drain()
    assert c.results[0].state=='FAILED'

def test_dispatch_failure():
    c,v,d,e=setup();d.error=True;c.present(arts(1));e.complete(0)
    assert c.results[0].state=='FAILED' and c.results[0].reason=='dispatch_failed'

def test_open_failure_terminalizes_reserved_slots():
    c,v,d,e=setup();v.open_error=True
    with pytest.raises(RuntimeError):c.present(arts(2))
    assert all(r.state in c._TERMINAL for r in c.results)

def test_old_presentation_results_remain_auditable():
    c,v,d,e=setup();c.present(arts(1));first=c.results[0]
    c.present(arts(1))
    assert any(r.presentation_id==first.presentation_id for r in c.results)

def test_duplicate_callback_conflict_is_explicit():
    c,v,d,e=setup();c.present(arts(1));e.complete(0)
    f,_,_=e.jobs[0]
    c._schedule_result(f,1,1,c.results[0].attempt_id)
    assert c.duplicate_events and c.duplicate_events[-1][2] in ('duplicate_conflict', 'duplicate_equivalent')

def test_transport_limits_reach_fetcher():
    calls = []

    def fetcher(url, timeout, max_bytes):
        calls.append((url, timeout, max_bytes))
        return b"png", "image/png"

    c, v, d, e = setup(fetcher)
    c._timeout = 3.25
    c._max_bytes = 123456

    c.present(arts(1))
    e.complete(0)
    d.drain()

    assert calls == [
        ("https://example.test/0", 3.25, 123456)
    ]
