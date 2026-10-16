# M308 — Speech Backend Abstraction

M308 separates microphone capture and utterance segmentation from speech recognition.

## Stable default

Vosk remains the default offline backend. Existing configuration, model location,
continuous listening, diagnostics and public lifecycle methods remain compatible.

## New contract

`app.speech_backend.SpeechRecognitionBackend` creates recognition sessions that
consume PCM16 audio and return partial and final text. Alternative recognizers can
now be introduced without modifying the microphone stream or desktop UI.

## Compatibility

`VoskAudioEngine` keeps its public name for backward compatibility. It now accepts
an optional backend and creates `VoskSpeechRecognitionBackend` when none is supplied.
