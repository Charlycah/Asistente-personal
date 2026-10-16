from __future__ import annotations

import ctypes
import os
from ctypes import wintypes


def process_exists(process_id: int) -> bool:
    """Check process liveness without applying POSIX semantics on Windows."""

    if process_id <= 0:
        return False
    if process_id == os.getpid():
        return True
    if os.name == "nt":
        return _windows_process_exists(process_id)
    try:
        os.kill(process_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _windows_process_exists(process_id: int) -> bool:
    process_query_limited_information = 0x1000
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    open_process = kernel32.OpenProcess
    open_process.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    open_process.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL

    handle = open_process(process_query_limited_information, False, process_id)
    if handle:
        close_handle(handle)
        return True
    # ERROR_ACCESS_DENIED means the process exists but cannot be inspected.
    return ctypes.get_last_error() == 5
