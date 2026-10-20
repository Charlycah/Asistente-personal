"""Minimal nonmodal Tkinter window for governed visual artifacts."""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from threading import get_ident
from typing import Any

from PIL import Image, UnidentifiedImageError


class DesktopGovernedFloatingImageViewer:
    """Own a reusable child window on its creating UI thread."""

    def __init__(
        self,
        *,
        root: object,
        toolkit: Any,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        self._root = root
        self._toolkit = toolkit
        self._on_close = on_close
        self._owner_thread = get_ident()
        self._window: Any | None = None
        self.artifacts: tuple[object, ...] = ()
        self._preview_images: list[Any] = []
        self._preview_widgets: list[Any] = []
        self._canvas: Any | None = None
        self._scrollbar: Any | None = None
        self._content: Any | None = None
        self._canvas_item: Any | None = None

    def _require_ui_thread(self) -> None:
        if get_ident() != self._owner_thread:
            raise RuntimeError("Floating image viewer accessed outside its UI thread")

    def _supports_scrolling(self) -> bool:
        return all(
            callable(getattr(self._toolkit, name, None))
            for name in ("Canvas", "Scrollbar", "Frame")
        )

    def _update_scroll_region(self, event: Any = None) -> None:
        if self._canvas is None:
            return
        bounds = self._canvas.bbox("all")
        if bounds is not None:
            self._canvas.configure(scrollregion=bounds)

    def _resize_content(self, event: Any) -> None:
        if self._canvas is None or self._canvas_item is None:
            return
        width = getattr(event, "width", None)
        if isinstance(width, int) and width > 0:
            self._canvas.itemconfigure(self._canvas_item, width=width)
        self._update_scroll_region()

    def _scroll_wheel(self, event: Any) -> None:
        if self._canvas is None:
            return
        delta = getattr(event, "delta", 0)
        if delta:
            steps = -1 if delta > 0 else 1
            self._canvas.yview_scroll(steps, "units")

    def _create_scrollable_content(self, window: Any) -> None:
        canvas = self._toolkit.Canvas(window, highlightthickness=0)
        scrollbar = self._toolkit.Scrollbar(
            window,
            orient="vertical",
            command=canvas.yview,
        )
        content = self._toolkit.Frame(canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.yview)
        canvas_item = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw",
        )
        self._canvas = canvas
        self._scrollbar = scrollbar
        self._content = content
        self._canvas_item = canvas_item
        content.bind("<Configure>", self._update_scroll_region)
        canvas.bind("<Configure>", self._resize_content)
        canvas.bind("<MouseWheel>", self._scroll_wheel)
        content.bind("<MouseWheel>", self._scroll_wheel)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def open(self, artifacts: tuple[object, ...]) -> None:
        self._require_ui_thread()
        admitted = tuple(artifacts)
        if self._window is None:
            window = self._toolkit.Toplevel(self._root)
            window.title("ROBY - Galeria visual")
            window.resizable(True, True)
            window.protocol("WM_DELETE_WINDOW", self.close)
            self._window = window
            if self._supports_scrolling():
                self._create_scrollable_content(window)

        for widget in self._preview_widgets:
            widget.destroy()
        self._preview_widgets.clear()
        self._preview_images.clear()
        self.artifacts = admitted
        self._update_scroll_region()
        if self._canvas is not None:
            self._canvas.yview_moveto(0)

    @staticmethod
    def _bounded_png(payload: bytes) -> bytes:
        """Bound the displayed PNG; never change the admitted artifact."""
        try:
            with Image.open(BytesIO(payload)) as image:
                if image.format != "PNG":
                    return payload
                if image.width <= 400 and image.height <= 300:
                    return payload
                image.thumbnail((400, 300), Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, format="PNG")
                return output.getvalue()
        except (
            OSError,
            ValueError,
            SyntaxError,
            UnidentifiedImageError,
            Image.DecompressionBombError,
        ):
            return payload

    def render_preview(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
    ) -> bool:
        """Render an admitted bounded PNG in the floating window."""
        self._require_ui_thread()
        if self._window is None:
            return False
        if not any(item is artifact for item in self.artifacts):
            return False
        if content_type.casefold() != "image/png":
            return False
        if not isinstance(payload, bytes):
            return False
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            return False

        try:
            image = self._toolkit.PhotoImage(
                data=self._bounded_png(payload),
                format="png",
            )
            parent = self._content if self._content is not None else self._window
            widget = self._toolkit.Label(parent, image=image)
            widget.pack()
        except (OSError, RuntimeError, ValueError, TypeError):
            return False

        self._preview_images.append(image)
        self._preview_widgets.append(widget)
        if self._canvas is not None:
            widget.bind("<MouseWheel>", self._scroll_wheel)
        self._update_scroll_region()
        return True

    def close(self) -> None:
        self._require_ui_thread()
        if self._window is not None:
            window = self._window
            self._window = None
            try:
                if self._on_close is not None:
                    self._on_close()
            finally:
                window.destroy()
        self._canvas = None
        self._scrollbar = None
        self._content = None
        self._canvas_item = None
        self._preview_widgets.clear()
        self._preview_images.clear()
        self.artifacts = ()
