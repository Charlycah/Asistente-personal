from __future__ import annotations

import inspect

from app.desktop_bootstrap import build_unified_desktop_app
from app.desktop_ui import ROBYDesktopApp


def test_lx1_s3e2i_bootstrap_reenters_existing_attachment_authorities():
    source = inspect.getsource(build_unified_desktop_app)

    assert "root.dependencies.document_inbox" in source
    assert "root.dependencies.governed_visual_collection_runtime" in source
    assert "document_inbox=document_inbox" in source
    assert "governed_visual_collection_runtime=" in source


def test_lx1_s3e2i_desktop_keeps_document_admission_subordinate():
    source = inspect.getsource(ROBYDesktopApp)

    assert "self.controller.document_reading.read_text(" in source
    assert "self.document_inbox.ingest_text(" in source
    assert "explicit_document_ids=" in source
    assert "DocumentReadingService()" not in source


def test_lx1_s3e2i_one_attach_surface_routes_without_parallel_storage():
    source = inspect.getsource(ROBYDesktopApp)

    assert source.count('text="Adjuntar"') == 1
    assert "governed_visual_collection_runtime" in source
    assert "FileImageRepository(" not in source
    assert "SQLiteDocumentRepository(" not in source
    assert ".repository.save(" not in source


def test_lx1_s3e2i_generic_zip_is_rejected_without_extraction():
    source = inspect.getsource(ROBYDesktopApp)

    assert '".zip"' in source or "'.zip'" in source
    assert "extractall(" not in source
    assert ".extract(" not in source
    assert "ZipFile(" not in source
