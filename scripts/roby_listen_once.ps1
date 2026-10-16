param(
    [string]$Language = "es-AR",
    [int]$TimeoutSeconds = 8
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$recognizers = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers()
$selected = $recognizers | Where-Object { $_.Culture.Name -eq $Language } | Select-Object -First 1
if (-not $selected) {
    $prefix = $Language.Split('-')[0]
    $selected = $recognizers | Where-Object { $_.Culture.TwoLetterISOLanguageName -eq $prefix } | Select-Object -First 1
}
if (-not $selected) { exit 0 }
$engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine($selected)
try {
    $engine.SetInputToDefaultAudioDevice()
    $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
    $result = $engine.Recognize([TimeSpan]::FromSeconds([Math]::Max(2, $TimeoutSeconds)))
    if ($result -and $result.Confidence -ge 0.48) { [Console]::Out.Write($result.Text) }
} finally {
    $engine.Dispose()
}
