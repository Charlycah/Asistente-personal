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
        self._vic_units: dict[tuple[int, ...], tuple[Any, Any]] = {}
        self._vic_secondary_errors: list[tuple[tuple[int, ...], str]] = []
        self._canvas: Any | None = None
        self._scrollbar: Any | None = None
        self._content: Any | None = None
        self._canvas_item: Any | None = None
        self._gallery_columns = 3
        self._gallery_background = "#14243A"
        self._gallery_card = "#243B58"
        self._gallery_foreground = "#E7EFFB"

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
        canvas = self._toolkit.Canvas(
            window, highlightthickness=0, bg=self._gallery_background,
        )
        scrollbar = self._toolkit.Scrollbar(
            window,
            orient="vertical",
            command=canvas.yview,
        )
        content = self._toolkit.Frame(canvas, bg=self._gallery_background)
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
            window.title("ROBY XI.2 - Galería visual")
            if callable(getattr(window, "configure", None)):
                window.configure(bg=self._gallery_background)
            window.resizable(True, True)
            # Respetar pantallas más pequeñas y no exceder su área útil.
            if callable(getattr(window, "geometry", None)):
                screen_w = getattr(window, "winfo_screenwidth", lambda: 1200)()
                screen_h = getattr(window, "winfo_screenheight", lambda: 850)()
                if type(screen_w) is not int or screen_w <= 0:
                    screen_w = 1200
                if type(screen_h) is not int or screen_h <= 0:
                    screen_h = 850
                window.geometry(f"{min(1100, max(480, screen_w - 100))}x"
                                f"{min(750, max(360, screen_h - 130))}")
            window.protocol("WM_DELETE_WINDOW", self.close)
            self._window = window
            if self._supports_scrolling():
                self._create_scrollable_content(window)

        # Destruir unidades anteriores sin perder referencias
        # cuando una destruccion falle.
        survivors = []
        survivor_images = []
        cleanup_error = None

        for widget, image in zip(
            self._preview_widgets,
            self._preview_images,
        ):
            try:
                widget.destroy()
            except Exception as exc:
                survivors.append(widget)
                survivor_images.append(image)
                if cleanup_error is None:
                    cleanup_error = exc

        self._preview_widgets = survivors
        self._preview_images = survivor_images
        self._reconcile_vic_units()

        # No admitir una presentacion nueva con residuos visibles.
        if cleanup_error is not None:
            raise cleanup_error

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

    def _place_gallery_widget(self, widget: Any, ordinal: int) -> None:
        """Distribuir miniaturas sin alterar el contrato de identidad VIC."""
        parent = self._content if self._content is not None else self._window
        if callable(getattr(widget, "grid", None)) and callable(
            getattr(parent, "grid_columnconfigure", None)
        ):
            for column in range(self._gallery_columns):
                parent.grid_columnconfigure(column, weight=1)
            index = max(0, ordinal - 1)
            widget.grid(
                row=index // self._gallery_columns,
                column=index % self._gallery_columns,
                padx=12, pady=12, sticky="n",
            )
        else:
            # Compatibilidad con dobles de prueba y toolkits limitados.
            widget.pack()

    def _save_received_png(self, payload: bytes, ordinal: int) -> None:
        """Guardar por elección explícita los bytes PNG recibidos, no la miniatura."""
        self._require_ui_thread()
        if self._window is None or not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            return
        from tkinter import filedialog, messagebox

        filename = filedialog.asksaveasfilename(
            parent=self._window,
            title="Guardar imagen recibida como…",
            initialfile=f"roby_imagen_{ordinal:02d}.png",
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png")],
        )
        if not filename:
            return
        try:
            with open(filename, "wb") as output:
                output.write(payload)
        except OSError as exc:
            messagebox.showerror(
                "ROBY - No se pudo guardar",
                f"No fue posible guardar la imagen: {exc}",
                parent=self._window,
            )

    def _show_image_info(self, artifact: object, payload: bytes, ordinal: int) -> None:
        """Mostrar solo información efectivamente disponible en el artefacto."""
        self._require_ui_thread()
        from tkinter import messagebox

        title = getattr(artifact, "title", None)
        source_id = getattr(artifact, "source_id", None)
        try:
            with Image.open(BytesIO(payload)) as image:
                dimensions = f"{image.width} × {image.height} píxeles"
        except (OSError, ValueError, UnidentifiedImageError):
            dimensions = "No disponibles"
        lines = [f"Imagen {ordinal}", f"Dimensiones: {dimensions}"]
        if isinstance(title, str) and title.strip():
            lines.append(f"Título: {title.strip()}")
        if isinstance(source_id, str) and source_id.strip():
            lines.append(f"Fuente: {source_id.strip()}")
        lines.append("Archivo disponible: PNG recibido por ROBY (no original verificado)")
        messagebox.showinfo("ROBY - Información de imagen", "\n".join(lines), parent=self._window)

    def _show_context_menu(
        self, event: Any, artifact: object, payload: bytes, ordinal: int
    ) -> None:
        self._require_ui_thread()
        if self._window is None:
            return
        menu_type = getattr(self._toolkit, "Menu", None)
        if not callable(menu_type):
            return
        menu = menu_type(self._window, tearoff=0)
        menu.add_command(
            label="Ampliar imagen",
            command=lambda: self._show_zoom(payload, ordinal),
        )
        menu.add_command(
            label="Guardar imagen como…",
            command=lambda: self._save_received_png(payload, ordinal),
        )
        menu.add_separator()
        menu.add_command(
            label="Información de la imagen",
            command=lambda: self._show_image_info(artifact, payload, ordinal),
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _bind_context_menu(
        self, widget: Any, artifact: object, payload: bytes, ordinal: int
    ) -> None:
        if callable(getattr(widget, "bind", None)):
            widget.bind(
                "<Button-3>",
                lambda event, item=artifact, data=payload, number=ordinal:
                    self._show_context_menu(event, item, data, number),
            )

    def _bind_zoom(self, widget: Any, payload: bytes, ordinal: int) -> None:
        """Ampliación a demanda; nunca modifica el artefacto admitido."""
        if not callable(getattr(widget, "bind", None)):
            return
        widget.bind(
            "<Button-1>",
            lambda event, data=payload, number=ordinal: self._show_zoom(data, number),
        )

    def _show_zoom(self, payload: bytes, ordinal: int) -> None:
        self._require_ui_thread()
        if self._window is None:
            return
        try:
            with Image.open(BytesIO(payload)) as source:
                if source.format != "PNG":
                    return
                image = source.copy()
                image.thumbnail((1000, 680), Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, format="PNG")
            popup = self._toolkit.Toplevel(self._window)
            popup.title(f"ROBY - Imagen {ordinal}")
            popup.resizable(True, True)
            photo = self._toolkit.PhotoImage(data=output.getvalue(), format="png")
            label = self._toolkit.Label(popup, image=photo)
            label.image = photo  # Referencia necesaria para Tkinter.
            label.pack(fill="both", expand=True)
            popup.bind("<Escape>", lambda event: popup.destroy())
        except (OSError, RuntimeError, ValueError, TypeError, UnidentifiedImageError):
            return

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
            widget = self._toolkit.Label(
                parent, image=image, bg=self._gallery_card,
                padx=7, pady=7, relief="flat", cursor="hand2",
            )
            self._place_gallery_widget(widget, len(self._preview_widgets) + 1)
            self._bind_zoom(widget, payload, len(self._preview_widgets) + 1)
            self._bind_context_menu(
                widget, artifact, payload, len(self._preview_widgets) + 1
            )
        except (OSError, RuntimeError, ValueError, TypeError):
            return False

        self._preview_images.append(image)
        self._preview_widgets.append(widget)
        if self._canvas is not None:
            widget.bind("<MouseWheel>", self._scroll_wheel)
        self._update_scroll_region()
        return True

    def render_preview_vic(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
        *,
        visible_ordinal: int,
    ) -> bool:
        return self._render_preview_vic_core(
            artifact, payload, content_type,
            visible_ordinal=visible_ordinal,
            unit_key=None,
        )

    def render_preview_vic_identified(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
        *,
        visible_ordinal: int,
        unit_key: tuple[int, ...],
    ) -> bool:
        self._require_ui_thread()

        if (
            type(unit_key) is not tuple
            or len(unit_key) != 6
            or any(type(value) is not int for value in unit_key)
        ):
            return False

        if unit_key in self._vic_units:
            return False

        # artifact_id es una identidad contractual del coordinador,
        # no la direccion de memoria del objeto Python.
        if unit_key[3] != visible_ordinal:
            return False

        return self._render_preview_vic_core(
            artifact, payload, content_type,
            visible_ordinal=visible_ordinal,
            unit_key=unit_key,
        )

    def _render_preview_vic_core(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
        *,
        visible_ordinal: int,
        unit_key: tuple[int, ...] | None,
    ) -> bool:
        """Commit an admitted PNG and its canonical ordinal as one UI unit."""
        self._require_ui_thread()

        if self._window is None:
            return False
        if not any(item is artifact for item in self.artifacts):
            return False
        if type(visible_ordinal) is not int or visible_ordinal < 1:
            return False
        if not isinstance(content_type, str):
            return False
        if content_type.casefold() != "image/png":
            return False
        if not isinstance(payload, bytes):
            return False
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            return False

        widget = None
        try:
            image = self._toolkit.PhotoImage(
                data=self._bounded_png(payload),
                format="png",
            )
            parent = self._content if self._content is not None else self._window
            widget = self._toolkit.Label(
                parent,
                image=image,
                text=str(visible_ordinal),
                compound="top",
                bg=self._gallery_card, fg=self._gallery_foreground,
                font=("Segoe UI", 10, "bold"),
                padx=7, pady=7, relief="flat", cursor="hand2",
            )
            if self._canvas is not None:
                widget.bind("<MouseWheel>", self._scroll_wheel)
            self._place_gallery_widget(widget, visible_ordinal)
            self._bind_zoom(widget, payload, visible_ordinal)
            self._bind_context_menu(widget, artifact, payload, visible_ordinal)
            self._update_scroll_region()
        except Exception:
            if widget is not None:
                try:
                    widget.destroy()
                except Exception:
                    # Preserve ownership of an incompletely cleaned UI unit.
                    self._preview_widgets.append(widget)
                    self._preview_images.append(image)
            return False

        self._preview_images.append(image)
        self._preview_widgets.append(widget)
        if unit_key is not None:
            self._vic_units[unit_key] = (widget, image)
        return True

    def discard_preview_vic(
        self,
        unit_key: tuple[int, ...],
    ) -> bool:
        self._require_ui_thread()

        unit = self._vic_units.get(unit_key)
        if unit is None:
            return False

        widget, image = unit

        try:
            widget.destroy()
        except Exception:
            return False

        self._vic_units.pop(unit_key, None)

        for index, current in enumerate(self._preview_widgets):
            if current is widget:
                del self._preview_widgets[index]
                del self._preview_images[index]
                break

        try:
            self._update_scroll_region()
        except Exception as exc:
            # Fallo secundario: el descarte VIC ya concluy?.
            self._vic_secondary_errors.append(
                (unit_key, type(exc).__name__)
            )
            if len(self._vic_secondary_errors) > 32:
                del self._vic_secondary_errors[:-32]
        return True

    def _reconcile_vic_units(self) -> None:
        self._require_ui_thread()
        active_ids = {id(widget) for widget in self._preview_widgets}

        for key, (widget, image) in tuple(self._vic_units.items()):
            if id(widget) not in active_ids:
                self._vic_units.pop(key, None)


    def close(self) -> None:
        self._require_ui_thread()

        if self._window is not None:
            window = self._window

            try:
                if self._on_close is not None:
                    self._on_close()
            finally:
                # No perder la referencia antes de confirmar destroy.
                window.destroy()

            self._window = None

        self._canvas = None
        self._scrollbar = None
        self._content = None
        self._canvas_item = None
        self._preview_widgets.clear()
        self._preview_images.clear()
        self._vic_units.clear()
        self.artifacts = ()
