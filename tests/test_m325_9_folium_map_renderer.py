from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

import pytest

from core.map_display import (
    MapDisplayRequest,
    MapDisplayTarget,
    MapDocumentRenderer,
)
from core.maps_foundation import GeoPointSignal
from infrastructure.maps import (
    FoliumMapRenderer,
    FoliumMapRendererConfig,
    FoliumRenderError,
)


def request(*, query: str = "Plaza de Mayo", zoom: int = 16) -> MapDisplayRequest:
    return MapDisplayRequest(owner="Carlos", query=query, zoom=zoom)


def target(*, label: str = "Plaza de Mayo, Buenos Aires") -> MapDisplayTarget:
    return MapDisplayTarget(
        label=label,
        point=GeoPointSignal(
            latitude=-34.6083696,
            longitude=-58.3724715,
            source="nominatim",
            confidence=0.82,
        ),
        confidence=0.82,
        source="nominatim",
        external_id="123",
    )


def document_path(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        raise ValueError("map document URI must use the file scheme")
    return Path(url2pathname(parsed.path))


def test_config_normalizes_values(tmp_path: Path) -> None:
    config = FoliumMapRendererConfig(
        output_directory=tmp_path / "nested" / "maps",
        filename_prefix="  roby map  ",
        tiles=" OpenStreetMap ",
        width=" 90% ",
        height=" 500px ",
    )
    assert config.output_directory == (tmp_path / "nested" / "maps").resolve()
    assert config.filename_prefix == "roby_map"
    assert config.tiles == "OpenStreetMap"
    assert config.width == "90%"
    assert config.height == "500px"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"filename_prefix": " "}, "prefix"),
        ({"filename_prefix": "bad/name"}, "path separators"),
        ({"filename_prefix": "bad\\name"}, "path separators"),
        ({"tiles": " "}, "tiles"),
        ({"width": " "}, "dimensions"),
        ({"height": " "}, "dimensions"),
    ],
)
def test_config_rejects_invalid_values(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        FoliumMapRendererConfig(**kwargs)


def test_renderer_implements_map_document_renderer_protocol() -> None:
    assert isinstance(FoliumMapRenderer(), MapDocumentRenderer)


def test_render_creates_html_document_in_configured_directory(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "fixed",
    )
    document = renderer.render(request(), target())
    path = document_path(document.uri)

    assert path.parent == tmp_path.resolve()
    assert path.name.endswith("_fixed.html")
    assert path.is_file()
    assert document.media_type == "text/html"
    assert document.title == "Mapa de Plaza de Mayo, Buenos Aires"
    assert document.temporary is True


def test_default_render_uses_unique_temporary_directory() -> None:
    renderer = FoliumMapRenderer(token_factory=lambda: "fixed")
    document = renderer.render(request(), target())
    path = document_path(document.uri)
    try:
        assert path.parent.name.startswith("roby_maps_")
        assert path.is_file()
    finally:
        path.unlink(missing_ok=True)
        path.parent.rmdir()


def test_render_creates_missing_output_directories(tmp_path: Path) -> None:
    output = tmp_path / "one" / "two"
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=output),
        token_factory=lambda: "fixed",
    )
    document = renderer.render(request(), target())
    assert output.is_dir()
    assert document_path(document.uri).is_file()


def test_filename_contains_prefix_request_fragment_and_token(tmp_path: Path) -> None:
    map_request = request()
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(
            output_directory=tmp_path, filename_prefix="roby_location"
        ),
        token_factory=lambda: "abc123",
    )
    document = renderer.render(map_request, target())
    assert document_path(document.uri).name == (
        f"roby_location_{map_request.request_id[:12]}_abc123.html"
    )


def test_two_renders_get_distinct_documents(tmp_path: Path) -> None:
    tokens = iter(("one", "two"))
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: next(tokens),
    )
    first = renderer.render(request(), target())
    second = renderer.render(request(), target())
    assert first.uri != second.uri
    assert document_path(first.uri).is_file()
    assert document_path(second.uri).is_file()


def test_generated_html_contains_coordinates_label_and_openstreetmap(
    tmp_path: Path,
) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "fixed",
    )
    path = document_path(renderer.render(request(), target()).uri)
    html_text = path.read_text(encoding="utf-8")
    assert "-34.6083696" in html_text
    assert "-58.3724715" in html_text
    assert "Plaza de Mayo, Buenos Aires" in html_text
    assert "OpenStreetMap" in html_text


def test_generated_html_uses_requested_zoom(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "fixed",
    )
    path = document_path(renderer.render(request(zoom=11), target()).uri)
    html_text = path.read_text(encoding="utf-8")
    assert '"zoom": 11' in html_text


def test_marker_popup_escapes_untrusted_label(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "fixed",
    )
    label = '<script>alert("x")</script>'
    path = document_path(renderer.render(request(), target(label=label)).uri)
    html_text = path.read_text(encoding="utf-8")
    assert "<script>alert" not in html_text
    assert "&lt;script&gt;" in html_text


def test_invalid_document_token_is_rejected(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "bad/token",
    )
    with pytest.raises(FoliumRenderError, match="token"):
        renderer.render(request(), target())
    assert list(tmp_path.iterdir()) == []


def test_blank_document_token_is_rejected(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: " ",
    )
    with pytest.raises(FoliumRenderError, match="token"):
        renderer.render(request(), target())


def test_output_path_that_is_a_file_is_rejected(tmp_path: Path) -> None:
    output = tmp_path / "not-a-directory"
    output.write_text("occupied", encoding="utf-8")
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=output),
        token_factory=lambda: "fixed",
    )
    with pytest.raises(FoliumRenderError, match="output directory"):
        renderer.render(request(), target())


def test_dimensions_are_reflected_in_generated_html(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(
            output_directory=tmp_path,
            width="80%",
            height="420px",
        ),
        token_factory=lambda: "fixed",
    )
    path = document_path(renderer.render(request(), target()).uri)
    html_text = path.read_text(encoding="utf-8")
    assert "width: 80.0%" in html_text
    assert "height: 420.0px" in html_text


def test_custom_tiles_are_reflected_in_generated_html(tmp_path: Path) -> None:
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(
            output_directory=tmp_path,
            tiles="CartoDB positron",
        ),
        token_factory=lambda: "fixed",
    )
    path = document_path(renderer.render(request(), target()).uri)
    html_text = path.read_text(encoding="utf-8")
    assert "cartocdn" in html_text.casefold()


def test_existing_unrelated_files_are_preserved(tmp_path: Path) -> None:
    unrelated = tmp_path / "keep.txt"
    unrelated.write_text("keep", encoding="utf-8")
    renderer = FoliumMapRenderer(
        FoliumMapRendererConfig(output_directory=tmp_path),
        token_factory=lambda: "fixed",
    )
    renderer.render(request(), target())
    assert unrelated.read_text(encoding="utf-8") == "keep"
