# S4-D7-C.8: single-file, append-only documentary reconciliation.
# Run from the ROBY XI.2 repository root. Does not change other files.
$ErrorActionPreference = 'Stop'
$target = Join-Path (Get-Location) 'ROBY_XI_2_CURRENT_TRUTH.md'
if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw 'STOP: CURRENT_TRUTH not found in working directory' }
$bytes = [System.IO.File]::ReadAllBytes($target)
$utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
$utf8Out = New-Object System.Text.UTF8Encoding($false)
$hasBom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
$offset = if ($hasBom) { 3 } else { 0 }
$text = $utf8Strict.GetString($bytes, $offset, $bytes.Length - $offset)
$heading = '## R-CAP17-S4-D7 — Governed Local Library Conversational Operations'
if ($text.Contains($heading)) { throw 'STOP: S4-D7 documentary section already exists; no changes made' }
if (-not $text.Contains('R-UI-CONV-01: DIRECTED INTEGRATION CERTIFIED.')) { throw 'STOP: expected current-truth baseline marker absent; no changes made' }
if (-not $text.Contains('STOP_PRODUCTIVE: ACTIVE.')) { throw 'STOP: governance marker absent; no changes made' }
$newline = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
$section = @'
## R-CAP17-S4-D7 — Governed Local Library Conversational Operations

Classification: bounded documentary reconciliation of the existing CAP-17
conversational contract; no new capability or productive authorization.

Existing capability: `knowledge.local_library.read`. Canonical authority
and ownership remain as recorded in
`docs/ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md` (CAP-17).

- LOCALIZAR: `GovernedLocalLibraryConversationV1.locate_admitted_request()`
  reuses the existing governed catalogue and conversational selector. A
  location-only request does not authorize document reading, content
  retrieval, or an additional unified retrieval evaluation.
- Explicit LEER: admitted reading requests use the existing governed
  document-reading and unified retrieval path. Combined location-and-reading
  requests are not treated as location-only requests.
- Selection and coverage: multiple matches require disambiguation. A bounded
  or incomplete catalogue search must not be presented as proof that a
  document does not exist.
- Compatibility: `GovernedLocalLibraryConversationInterceptionPort.intercept()`
  delegates location to the canonical conversation operation, without
  accessing its private catalogue or selector internals. If that operation
  is unavailable, location-only handling fails closed instead of reading.

Contractual evidence: `tests/architecture/test_r_cap17_s4_d7_c2_compatibility_red.py`
and `tests/architecture/test_r_cap17_catalogue_coverage_s4_document_operations_red.py`,
within the eleven-file focal CAP-17 regression.

Local certification: 123 PASS (focal CAP-17 regression); global Ruff PASS;
`git diff --check` without whitespace errors (LF/CRLF warnings only).
These results do not certify the full suite, all intent classes, or complete
Windows end-to-end production behavior. Historical certifications remain
historical and are not superseded.

No new catalogue, conversation gateway, retrieval, Reasoning, Planning,
Episode, or execution authority. No Memory/Learning side effects authorized.
M377 HOLD; MODEL_ACQUISITION UNMAPPED / DENY / NO-GO;
STOP_PRODUCTIVE ACTIVE. No new RED/GREEN productive horizon is authorized.
'@
$section = $section.Replace("`r`n", "`n").Replace("`n", $newline)
$prefix = if ($text.EndsWith($newline + $newline)) { '' } elseif ($text.EndsWith($newline)) { $newline } else { $newline + $newline }
$updated = $text + $prefix + $section + $newline
$outBody = $utf8Out.GetBytes($updated)
if ($hasBom) {
    $out = New-Object byte[] ($outBody.Length + 3)
    [Array]::Copy($bytes, 0, $out, 0, 3)
    [Array]::Copy($outBody, 0, $out, 3, $outBody.Length)
} else { $out = $outBody }
[System.IO.File]::WriteAllBytes($target, $out)
Write-Host 'S4_D7_C8_DOCUMENTARY_GREEN_APPLIED: ROBY_XI_2_CURRENT_TRUTH.md'
Write-Host 'NEXT: git --no-pager diff -- ROBY_XI_2_CURRENT_TRUTH.md; git diff --check'
