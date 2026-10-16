from __future__ import annotations

import html
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from uuid import uuid4

from core.map_display import (
    MapDisplayRequest,
    MapDisplayTarget,
    MapDocument,
    MapDocumentRenderer,
)


class FoliumMapRendererError(RuntimeError):
    """Base error raised while creating a Folium map document."""


class FoliumUnavailableError(FoliumMapRendererError):
    """Raised when the optional Folium dependency is unavailable."""


class FoliumRenderError(FoliumMapRendererError):
    """Raised when Folium cannot produce a usable HTML document."""


@dataclass(frozen=True)
class FoliumMapRendererConfig:
    output_directory: Path | str | None = None
    filename_prefix: str = "roby_map"
    tiles: str = "OpenStreetMap"
    width: str = "100%"
    height: str = "100%"

    def __post_init__(self) -> None:
        directory = self.output_directory
        if directory is not None:
            directory = Path(directory).expanduser().resolve()
        prefix = "_".join(self.filename_prefix.strip().split())
        tiles = " ".join(self.tiles.strip().split())
        width = self.width.strip()
        height = self.height.strip()
        if not prefix:
            raise ValueError("folium filename prefix must not be blank")
        if any(character in prefix for character in "\\/\0"):
            raise ValueError("folium filename prefix must not contain path separators")
        if not tiles:
            raise ValueError("folium tiles must not be blank")
        if not width or not height:
            raise ValueError("folium map dimensions must not be blank")
        object.__setattr__(self, "output_directory", directory)
        object.__setattr__(self, "filename_prefix", prefix)
        object.__setattr__(self, "tiles", tiles)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)


class FoliumMapRenderer:
    def __init__(
        self,
        config: FoliumMapRendererConfig | None = None,
        *,
        token_factory: Callable[[], str] | None = None,
    ) -> None:
        self._config = config or FoliumMapRendererConfig()
        self._token_factory = token_factory or (lambda: uuid4().hex)

    def render(
        self, request: MapDisplayRequest, target: MapDisplayTarget
    ) -> MapDocument:
        try:
            import folium
        except ImportError as exc:
            raise FoliumUnavailableError(
                "Folium is required to render map documents"
            ) from exc

        output_directory = self._prepare_output_directory()
        output_path = output_directory / self._build_filename(request)
        popup = html.escape(target.label, quote=True)
        try:
            map_view = folium.Map(
                location=[target.point.latitude, target.point.longitude],
                zoom_start=request.zoom,
                tiles=self._config.tiles,
                width=self._config.width,
                height=self._config.height,
                control_scale=True,
            )
            folium.Marker(
                [target.point.latitude, target.point.longitude],
                tooltip=popup,
                popup=folium.Popup(popup, max_width=350),
            ).add_to(map_view)
            map_view.save(str(output_path))
        except Exception as exc:
            self._remove_partial_file(output_path)
            raise FoliumRenderError(f"unable to render Folium map: {exc}") from exc

        if not output_path.is_file() or output_path.stat().st_size == 0:
            self._remove_partial_file(output_path)
            raise FoliumRenderError("Folium did not create a usable HTML document")

        return MapDocument(
            uri=output_path.as_uri(),
            media_type="text/html",
            title=f"Mapa de {target.label}",
            temporary=True,
        )

    def _prepare_output_directory(self) -> Path:
        configured = self._config.output_directory
        try:
            if configured is None:
                return Path(tempfile.mkdtemp(prefix="roby_maps_"))
            configured.mkdir(parents=True, exist_ok=True)
            if not configured.is_dir():
                raise NotADirectoryError(str(configured))
            return configured
        except OSError as exc:
            raise FoliumRenderError(
                f"unable to prepare map output directory: {exc}"
            ) from exc

    def _build_filename(self, request: MapDisplayRequest) -> str:
        token = self._token_factory().strip()
        if not token or any(character in token for character in "\\/\0"):
            raise FoliumRenderError("map document token is invalid")
        request_fragment = request.request_id[:12]
        return f"{self._config.filename_prefix}_{request_fragment}_{token}.html"

    @staticmethod
    def _remove_partial_file(path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


assert isinstance(FoliumMapRenderer(), MapDocumentRenderer)
