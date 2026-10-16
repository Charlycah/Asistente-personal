$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "Validando RP.20.14 en: $Root"

$forbidden = @(
    @{ Path = "m5/__init__.py"; Symbol = "ExecutionRegistry" },
    @{ Path = "m5/__init__.py"; Symbol = "EngineNotRegisteredError" },
    @{ Path = "m4/runtime/__init__.py"; Symbol = "CognitiveRuntime" }
)

foreach ($entry in $forbidden) {
    $content = Get-Content $entry.Path -Raw
    if ($content -match [regex]::Escape($entry.Symbol)) {
        throw "Forwarding obsoleto detectado: $($entry.Symbol) en $($entry.Path)"
    }
}

ruff check .
pytest -q
Write-Host "RP.20.14 aplicada correctamente."
