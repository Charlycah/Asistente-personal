from __future__ import annotations

import inspect

from app.desktop_ui import ROBYDesktopApp


def _desktop_source() -> str:
    return inspect.getsource(ROBYDesktopApp)


def test_lx1_s3e2g_document_attachment_reuses_existing_reader_and_inbox():
    source = _desktop_source()

    assert ".read_text(" in source
    assert ".ingest_text(" in source
    assert "document_inbox" in source


def test_lx1_s3e2g_document_admission_preserves_source_and_media_type():
    source = _desktop_source()

    assert "source_name=" in source
    assert "media_type=" in source


def test_lx1_s3e2g_document_admission_keeps_only_canonical_document_id():
    source = _desktop_source()

    assert ".document_id" in source
    assert "explicit_document_ids=" in source


def test_lx1_s3e2g_generic_zip_is_rejected_before_document_reading():
    source = _desktop_source()

    assert '".zip"' in source or "'.zip'" in source
    assert "read_text" in source
    assert "Formato" in source or "compatible" in source or "soportado" in source


def test_lx1_s3e2g_desktop_never_writes_document_repository_directly():
    source = _desktop_source()

    assert ".repository.save(" not in source
    assert "SQLiteDocumentRepository(" not in source
    assert "InMemoryDocumentRepository(" not in source


def test_lx1_s3e2g_desktop_does_not_create_another_document_reader_authority():
    source = _desktop_source()

    assert source.count("DocumentReadingService()") == 0
