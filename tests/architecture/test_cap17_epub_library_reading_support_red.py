from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from app.document_reading import DocumentReadingService
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.handoff import (
    GovernedLibrarySelection,
    GovernedLocalDocumentRetrievalRequest,
    GovernedLocalDocumentRetrieverV1,
)
from core.knowledge_retrieval_execution import KnowledgeRetrievalArtifact
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind


def _write_epub(
    path: Path,
    *,
    chapters: tuple[tuple[str, str], ...] = (
        ("chapter-1.xhtml", "<h1>Uno</h1><p>Primero</p>"),
        ("chapter-2.xhtml", "<h1>Dos</h1><p>Segundo</p>"),
    ),
    spine_order: tuple[str, ...] = ("chapter-1", "chapter-2"),
    extra_members: tuple[tuple[str, bytes], ...] = (),
    rootfile: str = "OEBPS/content.opf",
    include_spine: bool = True,
) -> None:
    manifest = "".join(
        f'<item id="{Path(name).stem}" href="{name}" '
        'media-type="application/xhtml+xml"/>'
        for name, _ in chapters
    )
    spine = "".join(f'<itemref idref="{item}"/>' for item in spine_order)
    container = (
        '<?xml version="1.0"?>'
        '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles>'
        f'<rootfile full-path="{rootfile}" '
        'media-type="application/oebps-package+xml"/>'
        '</rootfiles></container>'
    )
    opf = (
        '<?xml version="1.0"?>'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
        f'<manifest>{manifest}</manifest>'
        + (f'<spine>{spine}</spine>' if include_spine else '')
        + '</package>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml", container)
        archive.writestr(rootfile, opf)
        base = Path(rootfile).parent
        for name, content in chapters:
            archive.writestr((base / name).as_posix(), content)
        for name, content in extra_members:
            archive.writestr(name, content)


def _epub_library(root: Path) -> GovernedLocalLibraryCatalogueV1:
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=root, max_catalogue_entries=100)
    )


def _epub_artifact(root: Path, query: str) -> KnowledgeRetrievalArtifact:
    library = _epub_library(root)
    result = library.search(query, max_results=10)
    entry = result.matches[0]
    selection = GovernedLibrarySelection(
        query=result.query,
        entry_id=entry.entry_id,
        source_reference=entry.source_reference,
        catalogue_fingerprint=result.catalogue_fingerprint,
    )
    step = KnowledgeRetrievalStep(
        source=KnowledgeSourceKind.LOCAL_DOCUMENTS,
        priority=1,
        required=True,
        query=query,
    )
    request = GovernedLocalDocumentRetrievalRequest(step=step, selection=selection)
    return GovernedLocalDocumentRetrieverV1(
        library=library,
        document_reader=DocumentReadingService(),
    ).retrieve_selected(request)


def test_cap17_epub_is_in_default_governed_library_suffixes(tmp_path: Path) -> None:
    config = GovernedLocalLibraryConfig(root=tmp_path)

    assert ".epub" in config.allowed_suffixes


def test_cap17_minimal_epub_is_read_by_existing_document_reader(
    tmp_path: Path,
) -> None:
    book = tmp_path / "book.epub"
    _write_epub(book)

    text = DocumentReadingService().read_text(book)

    assert "Uno" in text
    assert "Primero" in text
    assert "Dos" in text
    assert "Segundo" in text


def test_cap17_epub_follows_opf_spine_not_zip_member_order(tmp_path: Path) -> None:
    book = tmp_path / "order.epub"
    _write_epub(book, spine_order=("chapter-2", "chapter-1"))

    text = DocumentReadingService().read_text(book)

    assert text.index("Dos") < text.index("Uno")


def test_cap17_epub_xhtml_becomes_plain_readable_text(tmp_path: Path) -> None:
    book = tmp_path / "markup.epub"
    _write_epub(
        book,
        chapters=(("chapter-1.xhtml", "<p>A &amp; B <strong>legible</strong></p>"),),
        spine_order=("chapter-1",),
    )

    text = DocumentReadingService().read_text(book)

    assert "A & B legible" in text
    assert "<strong>" not in text


def test_cap17_epub_reads_only_manifest_items_referenced_by_spine(
    tmp_path: Path,
) -> None:
    book = tmp_path / "spine-only.epub"
    _write_epub(
        book,
        chapters=(
            ("chapter-1.xhtml", "<p>VISIBLE</p>"),
            ("orphan.xhtml", "<p>ORPHAN-MUST-NOT-APPEAR</p>"),
        ),
        spine_order=("chapter-1",),
    )

    text = DocumentReadingService().read_text(book)

    assert "VISIBLE" in text
    assert "ORPHAN-MUST-NOT-APPEAR" not in text


def test_cap17_epub_enters_existing_handoff_and_returns_canonical_artifact(
    tmp_path: Path,
) -> None:
    root = tmp_path / "library"
    root.mkdir()
    _write_epub(root / "astronomia.epub")

    artifact = _epub_artifact(root, "astronomia")

    assert type(artifact) is KnowledgeRetrievalArtifact
    assert artifact.source is KnowledgeSourceKind.LOCAL_DOCUMENTS
    assert artifact.query == "astronomia"
    assert "Primero" in artifact.content
    assert artifact.references[0].startswith("local-library:")


def test_cap17_corrupt_epub_fails_with_epub_specific_governed_error(
    tmp_path: Path,
) -> None:
    book = tmp_path / "corrupt.epub"
    book.write_bytes(b"not-a-zip")

    with pytest.raises(ValueError, match="EPUB"):
        DocumentReadingService().read_text(book)


def test_cap17_epub_without_container_fails_governedly(tmp_path: Path) -> None:
    book = tmp_path / "missing-container.epub"
    with zipfile.ZipFile(book, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")

    with pytest.raises(ValueError, match="EPUB"):
        DocumentReadingService().read_text(book)


def test_cap17_epub_rejects_rootfile_path_traversal(tmp_path: Path) -> None:
    book = tmp_path / "traversal.epub"
    _write_epub(book, rootfile="../outside/content.opf")

    with pytest.raises(ValueError, match="EPUB"):
        DocumentReadingService().read_text(book)



def test_cap17_epub_without_spine_fails_governedly(tmp_path: Path) -> None:
    book = tmp_path / "missing-spine.epub"
    _write_epub(book, include_spine=False)

    with pytest.raises(ValueError, match="EPUB"):
        DocumentReadingService().read_text(book)


def test_cap17_epub_rejects_excessive_archive_member_count(
    tmp_path: Path,
) -> None:
    book = tmp_path / "too-many-members.epub"
    extras = tuple((f"junk/{index}.bin", b"x") for index in range(520))
    _write_epub(book, extra_members=extras)

    with pytest.raises(ValueError, match="EPUB.*límite"):
        DocumentReadingService().read_text(book)


def test_cap17_epub_rejects_excessive_uncompressed_payload(
    tmp_path: Path,
) -> None:
    book = tmp_path / "expanded.epub"
    payload = "x" * 8_000_001
    _write_epub(
        book,
        chapters=(("chapter-1.xhtml", f"<p>{payload}</p>"),),
        spine_order=("chapter-1",),
    )

    with pytest.raises(ValueError, match="EPUB.*límite"):
        DocumentReadingService().read_text(book)

def test_cap17_epub_never_extracts_members_to_filesystem(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    book = tmp_path / "no-extract.epub"
    _write_epub(book)

    def forbidden_extract(*args, **kwargs):
        raise AssertionError("EPUB reading must not extract archive members")

    monkeypatch.setattr(zipfile.ZipFile, "extract", forbidden_extract)
    monkeypatch.setattr(zipfile.ZipFile, "extractall", forbidden_extract)

    text = DocumentReadingService().read_text(book)

    assert "Primero" in text
    assert sorted(item.name for item in tmp_path.iterdir()) == ["no-extract.epub"]


def test_cap17_epub_preserves_existing_final_character_bound(tmp_path: Path) -> None:
    book = tmp_path / "bounded.epub"
    payload = "x" * (DocumentReadingService._MAX_CHARS + 1_000)
    _write_epub(
        book,
        chapters=(("chapter-1.xhtml", f"<p>{payload}</p>"),),
        spine_order=("chapter-1",),
    )

    text = DocumentReadingService().read_text(book)

    assert text.endswith("[Documento truncado por límite de seguridad]")
    assert len(text) < len(payload)
