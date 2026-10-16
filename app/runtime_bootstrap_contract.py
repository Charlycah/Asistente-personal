from __future__ import annotations

"""Stable identifiers for ROBY's canonical runtime bootstrap surfaces.

This module contains names only. It must not import runtime construction,
configuration, adapters, providers, or lifecycle implementations.
"""

OFFICIAL_RUNTIME_FACTORY = "app.runtime_root_factory:build_runtime_root"
OFFICIAL_COMPOSITION_ROOT = "core.runtime_composition_root:RuntimeCompositionRoot"
