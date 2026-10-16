$ErrorActionPreference = "Stop"
Write-Host "Validando RP.20.18..."
ruff check .
pytest -q
Write-Host "RP.20.18 aplicada correctamente."
