$ErrorActionPreference = "Stop"

Write-Host "Validando RP.20.15 en: $(Get-Location)"

$m4 = Get-Content ".\m4\__init__.py" -Raw
$m5 = Get-Content ".\m5\handlers\__init__.py" -Raw

if ($m4 -match "from\s+\." -or $m4 -match "__all__") {
    throw "m4/__init__.py todavia agrega simbolos internos."
}
if ($m5 -match "ReminderExecutionHandler" -or $m5 -match "__all__") {
    throw "m5/handlers/__init__.py todavia reexporta ReminderExecutionHandler."
}

ruff check .
pytest -q

Write-Host "RP.20.15 aplicada correctamente."
