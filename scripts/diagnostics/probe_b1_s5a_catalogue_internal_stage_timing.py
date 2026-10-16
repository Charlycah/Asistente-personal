from __future__ import annotations

import os
import time
from pathlib import Path

from app.roby_config import activate_roby_config, resolve_roby_config_path
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)

PROGRESS_SECONDS = 5.0
PROGRESS_DIRECTORIES = 100


class InternalStageTimingCatalogue(GovernedLocalLibraryCatalogueV1):
    """Diagnostic-only mirror of the canonical scan with cumulative timings."""

    def _scan_entries(self):
        collected = []
        scanned_count = 0
        truncated = False
        limit = self.config.max_catalogue_entries
        directories = 0
        filenames_seen = 0
        walk_seconds = 0.0
        directory_seconds = 0.0
        filename_seconds = 0.0
        entry_seconds = 0.0
        last_report = time.perf_counter()

        walker = iter(
            os.walk(
                self._root,
                followlinks=self.config.follow_symlinks,
            )
        )
        while True:
            started = time.perf_counter()
            try:
                directory, dirnames, filenames = next(walker)
            except StopIteration:
                walk_seconds += time.perf_counter() - started
                break
            walk_seconds += time.perf_counter() - started
            directories += 1
            directory_path = Path(directory)

            started = time.perf_counter()
            dirnames[:] = self._allowed_directories(directory_path, dirnames)
            directory_seconds += time.perf_counter() - started

            started = time.perf_counter()
            ordered_filenames = sorted(filenames, key=str.casefold)
            filename_seconds += time.perf_counter() - started
            for filename in ordered_filenames:
                filenames_seen += 1
                candidate = directory_path / filename
                started = time.perf_counter()
                admitted = candidate.suffix.casefold() in self.config.allowed_suffixes
                filename_seconds += time.perf_counter() - started
                if not admitted:
                    continue
                scanned_count += 1
                started = time.perf_counter()
                entry = self._entry_from_path(candidate)
                entry_seconds += time.perf_counter() - started
                if entry is None:
                    continue
                if len(collected) >= limit:
                    truncated = True
                    break
                collected.append(entry)

            now = time.perf_counter()
            if (
                directories % PROGRESS_DIRECTORIES == 0
                or now - last_report >= PROGRESS_SECONDS
            ):
                print(
                    "B1-S5A progress "
                    f"dirs={directories} files={filenames_seen} "
                    f"admitted={scanned_count} collected={len(collected)} "
                    f"walk={walk_seconds:.3f}s dirs_stage={directory_seconds:.3f}s "
                    f"filename_stage={filename_seconds:.3f}s "
                    f"entry_stage={entry_seconds:.3f}s",
                    flush=True,
                )
                last_report = now
            if truncated:
                break

        started = time.perf_counter()
        entries = tuple(
            sorted(collected, key=lambda item: item.relative_path.casefold())
        )
        sorting_seconds = time.perf_counter() - started
        print(
            "B1-S5A scan END "
            f"dirs={directories} files={filenames_seen} admitted={scanned_count} "
            f"collected={len(entries)} truncated={truncated} "
            f"walk={walk_seconds:.3f}s dirs_stage={directory_seconds:.3f}s "
            f"filename_stage={filename_seconds:.3f}s entry_stage={entry_seconds:.3f}s "
            f"sorting={sorting_seconds:.3f}s",
            flush=True,
        )
        return entries, scanned_count, truncated

    def _catalogue_fingerprint(self, entries):
        started = time.perf_counter()
        result = super()._catalogue_fingerprint(entries)
        elapsed = time.perf_counter() - started
        print(f"B1-S5A fingerprint END {elapsed:.3f}s", flush=True)
        return result


def main() -> int:
    config_path = resolve_roby_config_path()
    activate_roby_config(config_path)
    root_value = os.getenv("ROBY_LOCAL_LIBRARY_ROOT", "").strip()
    if not root_value:
        print("B1-S5A STOP: ROBY_LOCAL_LIBRARY_ROOT is not configured.")
        return 2
    root = Path(root_value).expanduser().resolve(strict=False)
    max_entries = int(os.getenv("ROBY_LOCAL_LIBRARY_MAX_CATALOGUE_ENTRIES", "10000"))
    print(f"B1-S5A config={config_path}", flush=True)
    print(f"B1-S5A root={root}", flush=True)
    print(f"B1-S5A max_catalogue_entries={max_entries}", flush=True)
    print("B1-S5A catalogue START", flush=True)
    started = time.perf_counter()
    catalogue = InternalStageTimingCatalogue(
        GovernedLocalLibraryConfig(
            root=root,
            max_catalogue_entries=max_entries,
        )
    ).catalogue()
    elapsed = time.perf_counter() - started
    print(
        f"B1-S5A catalogue END {elapsed:.3f}s entries={len(catalogue.entries)} "
        f"truncated={catalogue.truncated}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
