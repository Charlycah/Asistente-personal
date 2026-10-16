"""R-CONV-VOICE-SALUTE-S1: RED contractual dirigido, sin código productivo.

Destino previsto (tras revisión del Owner): tests/architecture/
No instalar ni aplicar automáticamente. Ejecutar desde la raíz de HAL:
    python -m pytest -q tests/architecture/test_r_conv_voice_salute_s1_red.py
"""
from pathlib import Path

from app.desktop_ui import DesktopUIConfig


EXPECTED_GREETING = "¿Qué tal, cómo estás?"


def test_s1_default_greeting_is_natural_and_not_identity_interrogation():
    greeting = DesktopUIConfig().greeting
    assert greeting == EXPECTED_GREETING
    assert "con quien estoy conversando" not in greeting.casefold()
    assert "con quién estoy conversando" not in greeting.casefold()


def test_s1_desktop_startup_renders_and_speaks_same_greeting_once():
    """RED de alcance: exige un único camino explícito visible + voz.

    No se invoca Tk en CI; se comprueba que el tramo de arranque
    reutiliza el voice_reader oficial para el saludo de DesktopUIConfig.
    El GREEN deberá sustituir esta prueba de fuente por una prueba de
    comportamiento con un seam ya existente, si el inventario lo permite.
    """
    source = (Path(__file__).resolve().parents[2] / "app" / "desktop_ui.py").read_text(
        encoding="utf-8"
    )
    startup = source.split("if self.config.greeting.strip():", 1)[1]
    startup = startup.split("if self.recovery_message:", 1)[0]
    assert "voice_output.speak(" in startup
    assert startup.count("voice_output.speak(") == 1


def test_s1_existing_announcer_keeps_safe_voice_failure_behavior():
    """Contrato preservado: falla de TTS no debe borrar texto.

    Este test complementa, no reemplaza, los tests existentes de M24.
    """
    import subprocess
    from app.desktop_ui import ROBYDesktopApp, DesktopMessage

    class Adapter:
        def submit_text(self, text, session_id=None):
            raise AssertionError("El saludo no debe enviar un turno al modelo")

    class BrokenVoice:
        def speak(self, text):
            raise subprocess.CalledProcessError(1, ["tts", text])

    app = ROBYDesktopApp(
        adapter=Adapter(),
        voice_output=BrokenVoice(),
        startup_announcer=lambda: "Anuncio informativo.",
    )
    assert app.startup_messages() == [DesktopMessage("Roby", "Anuncio informativo.")]
