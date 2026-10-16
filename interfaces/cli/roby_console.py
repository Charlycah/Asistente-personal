from __future__ import annotations


class StandardConsoleIO:
    """Terminal adapter for ROBYConsoleApplication."""

    def read(self, prompt: str) -> str | None:
        try:
            return input(prompt)
        except EOFError:
            return None

    def write(self, text: str) -> None:
        print(text)
