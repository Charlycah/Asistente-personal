"""Registro temporal de excepciones en el borde de la interfaz."""
from datetime import datetime
from pathlib import Path
from threading import Lock
import sys
import traceback

_LOCK = Lock()
_LOG = Path(__file__).resolve().parents[1] / ".roby/diagnostico_error_documentos.log"


def record_failure(origin, response=None):
    error_type, error, stack = sys.exc_info()
    if error_type is not None:
        detail = "".join(traceback.format_exception(error_type, error, stack))
    else:
        detail = "Fallo recibido como respuesta, sin excepcion activa.\n"
        detail += repr(response) + "\n"
    entry = f"\n[{datetime.now().astimezone().isoformat()}] {origin}\n{detail}"
    try:
        with _LOCK:
            _LOG.parent.mkdir(parents=True, exist_ok=True)
            with _LOG.open("a", encoding="utf-8") as stream:
                stream.write(entry)
    except OSError:
        pass
    try:
        if sys.stderr is not None:
            sys.stderr.write(entry)
    except (OSError, ValueError):
        pass
