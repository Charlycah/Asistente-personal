# M26 — Voice Input

## Objetivo

Introducir entrada de voz como una capa adaptadora externa a ROBY.

ROBY sigue recibiendo texto. La conversión de voz a texto ocurre antes de llamar al
`ROBYUIAdapter`, manteniendo el núcleo independiente de micrófono, audio, modelos STT
o dependencias de sistema.

## Arquitectura

```text
Micrófono / comando local
        ↓
VoiceInput
        ↓
VoiceRequestTranscriber
        ↓
DesktopConversationController.submit()
        ↓
ROBYUIAdapter.submit_text()
        ↓
ROBY.process()
```

## Componentes

- `VoiceInput`: contrato de transcripción.
- `VoiceInputProfile`: política de entrada local/offline.
- `NullVoiceInput`: implementación segura por defecto.
- `SafeVoiceInput`: mantiene STT como capacidad no crítica.
- `LocalCommandVoiceInput`: adaptador para motores locales/offline por comando.
- `VoiceRequestTranscriber`: normaliza texto transcripto antes de enviarlo a ROBY.

## Contrato

- ROBY no conoce voz ni audio.
- La UI puede enviar texto escrito o texto transcripto.
- Una falla de STT no debe romper la conversación.
- Una transcripción vacía no debe llamar a ROBY.
- El motor STT concreto queda reemplazable.

## Estado

Completo.
