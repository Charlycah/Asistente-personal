"""Conversacion visual redondeada de ROBY XI.2."""
import tkinter as tk
from tkinter import font as tkfont

from app.desktop_rounded_components import round_rect


class ChatBubbles(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#FFFFFF")

        self.canvas = tk.Canvas(
            self,
            bg="#FFFFFF",
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.messages = []
        self.canvas.bind("<Configure>", self._render)
        self.canvas.bind("<MouseWheel>", self._wheel)

        self._context_index = None
        self._context_menu = tk.Menu(
            self,
            tearoff=0,
        )
        self._context_menu.add_command(
            label="Copiar mensaje",
            command=self._copy_message,
        )
        self._context_menu.add_command(
            label="Copiar conversacion completa",
            command=self._copy_conversation,
        )
        self.canvas.bind(
            "<Button-3>",
            self._show_context_menu,
        )

    def _wheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(
                -int(event.delta / 120), "units"
            )

    def append(self, text, sender="Roby"):
        self.messages.append((str(sender), str(text)))
        self.after_idle(self._render)

    def _render(self, event=None):
        c = self.canvas
        if not c.winfo_exists():
            return

        c.delete("bubble")
        width = max(200, c.winfo_width())
        body = tkfont.Font(family="Segoe UI", size=10)

        y = 8
        max_width = min(width - 24, 650)
        text_limit = max(100, max_width - 28)

        for message_index, (sender, content) in enumerate(self.messages):
            is_user = sender.casefold() in {
                "vos", "usuario", "user"
            }

            words = content.split()
            lines = []
            line = ""

            for word in words:
                candidate = (line + " " + word).strip()
                if body.measure(candidate) <= text_limit or not line:
                    line = candidate
                else:
                    lines.append(line)
                    line = word

            if line:
                lines.append(line)
            if not lines:
                lines = [""]

            bubble_width = min(
                max_width,
                max(
                    125,
                    max(body.measure(t) for t in lines) + 28,
                ),
            )
            bubble_height = 18 + len(lines) * 21

            x = (
                width - bubble_width - 8
                if is_user else 8
            )

            round_rect(
                c,
                x, y,
                x + bubble_width,
                y + bubble_height,
                12,
                "#E7F3EF" if is_user else "#EAF4FF",
                tag=("bubble", f"msg_{message_index}"),
            )

            for index, line_text in enumerate(lines):
                c.create_text(
                    x + 13,
                    y + 10 + index * 21,
                    text=line_text,
                    anchor="nw",
                    fill="#24564B" if is_user else "#233C57",
                    font=("Segoe UI", 10),
                    tags=("bubble", f"msg_{message_index}"),
                )

            y += bubble_height + 12

        c.configure(
            scrollregion=(0, 0, width, max(y, c.winfo_height()))
        )
        c.yview_moveto(1.0)

    def _show_context_menu(self, event):
        self._context_index = None

        canvas = self.canvas
        item = canvas.find_closest(
            canvas.canvasx(event.x),
            canvas.canvasy(event.y),
        )

        if not item:
            return

        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        bounds = canvas.bbox(item[0])
        if bounds is None:
            return
        x1, y1, x2, y2 = bounds
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return

        tags = canvas.gettags(item[0])

        for tag in tags:
            if tag.startswith("msg_"):
                try:
                    index = int(tag[4:])
                except ValueError:
                    return

                if 0 <= index < len(self.messages):
                    self._context_index = index
                break

        if self._context_index is None:
            return

        try:
            self._context_menu.tk_popup(
                event.x_root,
                event.y_root,
            )
        finally:
            self._context_menu.grab_release()

    def _put_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()

    def _copy_message(self):
        index = self._context_index
        if index is None:
            return
        if not 0 <= index < len(self.messages):
            return

        sender, content = self.messages[index]
        self._put_clipboard(content)

    def _copy_conversation(self):
        if not self.messages:
            return

        parts = []
        for sender, content in self.messages:
            prefix = f"{sender}:"
            clean = content.strip()
            if clean.casefold().startswith(prefix.casefold()):
                parts.append(clean)
            else:
                parts.append(f"{sender}: {clean}")

        self._put_clipboard("\n\n".join(parts))
