from __future__ import annotations

from pathlib import Path

import pytest

import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_console_option_is_absent_from_the_parser(capsys) -> None:
    with pytest.raises(SystemExit) as captured:
        main.build_parser().parse_args(["--console"])

    assert captured.value.code == 2
    assert "unrecognized arguments: --console" in capsys.readouterr().err


def test_main_contains_no_console_surface_or_historical_marker() -> None:
    source = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    for retired_surface in (
        "--console",
        "args.console",
        "CONSOLE_DISABLED_MESSAGE",
        "LEGACY_CONSOLE_CERTIFICATION_MARKERS",
        "LocalConversationConsole",
        "legacy_console_compatibility",
    ):
        assert retired_surface not in source


def test_rp18_8_certifies_isolation_instead_of_main_source_markers() -> None:
    source = (
        PROJECT_ROOT / "tests" / "test_rp_18_8_single_execution_certification.py"
    ).read_text(encoding="utf-8")

    assert "retired_console_composition_is_outside" in source
    assert 'assert "--console" not in main_source' in source
    assert "legacy_console_compatibility.py" in source
    assert "assert not legacy_path.exists()" in source


def test_supported_parser_surface_remains_desktop_doctor_and_setup() -> None:
    parser = main.build_parser()

    assert parser.parse_args([]).desktop is False
    assert parser.parse_args(["--desktop"]).desktop is True
    assert parser.parse_args(["--doctor"]).doctor is True
    assert parser.parse_args(["--setup"]).setup is True


def test_retirement_document_records_complete_entrypoint_removal() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M383_CONTROLLED_CONSOLE_RETIREMENT.md"
    ).read_text(encoding="utf-8")

    assert "production parser no longer defines" in document
    assert "no console" in document
    assert "option, branch, marker, import or call" in document
