$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Validando simplificación arquitectónica RP.20.11 en: $root"

$obsoleteSymbols = @(
    @{ Path = "core/governed_reasoning/explanations.py"; Symbol = "class ReasoningExplanationManager" },
    @{ Path = "application/reminders/use_cases.py"; Symbol = "class ListPendingRemindersUseCase" }
)

foreach ($entry in $obsoleteSymbols) {
    if (Select-String -Path $entry.Path -Pattern $entry.Symbol -SimpleMatch -Quiet) {
        throw "Persistió el símbolo obsoleto '$($entry.Symbol)' en $($entry.Path). Extraiga primero todo el paquete RP.20.11 sobre ROBY."
    }
}

ruff check .
pytest -q

Write-Host "RP.20.11 aplicada correctamente."
