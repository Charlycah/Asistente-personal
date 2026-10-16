$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "Validando RP.20.13 en: $Root"

$ObsoleteBuilders = @(
    "build_official_conversation_gateway",
    "build_runtime_health_readiness",
    "build_runtime_operational_snapshot",
    "build_runtime_recovery_plan",
    "build_unified_runtime_observability_snapshot"
)

foreach ($Symbol in $ObsoleteBuilders) {
    $Matches = Get-ChildItem app -Recurse -Filter *.py | Select-String -Pattern "^def $Symbol\(" -CaseSensitive
    if ($Matches) {
        throw "Builder obsoleto todavía declarado: $Symbol"
    }
}

ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "RP.20.13 aplicada correctamente."
