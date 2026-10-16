$ErrorActionPreference = "Stop"

$adapterSource = Get-Content "app/cognitive_runtime_sources.py" -Raw
if ($adapterSource -match "class CognitiveSourceAdapter") {
    throw "RP.20.17 not applied: CognitiveSourceAdapter still exists."
}

$rootSource = Get-Content "app/runtime_root_factory.py" -Raw
if ($rootSource -match "CognitiveSourceAdapter") {
    throw "RP.20.17 not applied: runtime root still references CognitiveSourceAdapter."
}

ruff check .
pytest -q
