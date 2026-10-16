$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Validando limpieza de compatibilidad RP.20.12 en: $root"

$obsolete = "InternalKnowledgeNeedPort"
$matches = Get-ChildItem app,domain,application,core,infrastructure,m5 -Recurse -Filter *.py -ErrorAction SilentlyContinue |
    Select-String -Pattern $obsolete -SimpleMatch
if ($matches) {
    $matches | ForEach-Object { Write-Host $_.Path ":" $_.LineNumber $_.Line }
    throw "El alias historico InternalKnowledgeNeedPort sigue presente."
}

ruff check .
pytest -q
Write-Host "RP.20.12 aplicada correctamente."
