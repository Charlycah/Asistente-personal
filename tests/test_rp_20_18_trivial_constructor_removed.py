from pathlib import Path


def test_create_desktop_app_constructor_is_removed():
    source = Path("app/desktop_ui.py").read_text(encoding="utf-8")
    assert "def create_desktop_app(" not in source


def test_desktop_ui_keeps_canonical_types():
    source = Path("app/desktop_ui.py").read_text(encoding="utf-8")
    assert "class ROBYDesktopApp" in source
    assert "class DesktopROBYAdapter" in source


def test_registered_desktop_builder_remains_available():
    source = Path("app/desktop_bootstrap.py").read_text(encoding="utf-8")
    assert "def build_desktop_app(" in source
    assert "def build_unified_desktop_app(" in source
