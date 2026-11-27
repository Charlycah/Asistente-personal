"""Componentes visuales redondeados de ROBY XI.2.

PKG-C01-04D-01. Sin dependencias externas.
No controla procesamiento, voz ni ciclo de vida.
"""
import tkinter as tk

BG = "#EAF0F7"
NAVY = "#19395F"
WHITE = "#FFFFFF"
BLUE = "#EAF4FF"
GREEN = "#E7F3EF"
INK = "#233C57"


def round_rect(canvas, x1, y1, x2, y2, radius,
               fill, outline="", width=1, tag=None):
    """Dibuja un rect?ngulo con esquinas redondeadas."""
    if x2 <= x1 or y2 <= y1:
        return None

    radius = max(
        0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    )
    r = radius
    points = [
        x1+r, y1, x2-r, y1, x2, y1,
        x2, y1+r, x2, y2-r, x2, y2,
        x2-r, y2, x1+r, y2, x1, y2,
        x1, y2-r, x1, y1+r, x1, y1
    ]
    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=18,
        fill=fill,
        outline=outline,
        width=width,
        tags=tag or ()
    )


class RoundedButton(tk.Canvas):
    """Bot?n redondeado con estado habilitado/deshabilitado."""

    def __init__(self, master, label, color, command,
                 width=90, height=32, enabled=True):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=WHITE,
            highlightthickness=0,
            bd=0
        )
        self.label = label
        self.color = color
        self.command = command
        self.enabled = enabled
        self.bind("<Configure>", self._paint)
        self.bind("<Button-1>", self._click)
        self._paint()

    def _paint(self, event=None):
        self.delete("all")
        w = max(self.winfo_width(), int(self.cget("width")))
        h = max(self.winfo_height(), int(self.cget("height")))
        fill = self.color if self.enabled else "#94A3B8"

        round_rect(
            self, 1, 1, w-2, h-2,
            9, fill
        )
        self.create_text(
            w / 2, h / 2,
            text=self.label,
            fill=WHITE,
            font=("Segoe UI", 9, "bold")
        )
        self.configure(
            cursor="hand2" if self.enabled else "arrow"
        )

    def _click(self, event=None):
        if self.enabled and callable(self.command):
            self.command()

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        self._paint()
