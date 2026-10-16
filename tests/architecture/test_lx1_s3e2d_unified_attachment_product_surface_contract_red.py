from __future__ import annotations

import inspect

from app.desktop_ui import ROBYDesktopApp


def test_lx1_s3e2d_desktop_reuses_existing_attachment_authorities():
    parameters = inspect.signature(ROBYDesktopApp.__init__).parameters

    assert "document_inbox" in parameters
    assert "governed_visual_collection_runtime" in parameters


def test_lx1_s3e2d_desktop_exposes_one_unified_attach_control():
    source = inspect.getsource(ROBYDesktopApp)

    assert 'text="Adjuntar"' in source
    assert "askopenfilename" in source
    assert source.count('text="Adjuntar"') == 1


def test_lx1_s3e2d_attachment_admission_reuses_existing_boundaries():
    source = inspect.getsource(ROBYDesktopApp)

    assert "document_inbox" in source
    assert "governed_visual_collection_runtime" in source
    assert "FileImageRepository(" not in source
    assert "SQLiteDocumentRepository(" not in source


def test_lx1_s3e2d_document_selection_reenters_existing_turn_transport():
    source = inspect.getsource(ROBYDesktopApp)

    assert "explicit_document_ids=" in source
    assert "self.controller.submit_with_visual_companion(" in source
    assert source.count("self.controller.submit_with_visual_companion(") == 1


def test_lx1_s3e2d_zip_is_never_implicitly_extracted_by_desktop_surface():
    source = inspect.getsource(ROBYDesktopApp)

    assert "extractall(" not in source
    assert ".extract(" not in source
    assert "ZipFile(" not in source


def test_lx1_s3e2d_desktop_surface_does_not_own_reasoning_authority():
    source = inspect.getsource(ROBYDesktopApp)

    assert "GovernedReasoning" not in source
    assert "CognitiveRuntimeOrchestrator" not in source
    assert "OfficialVisionCore(" not in source
