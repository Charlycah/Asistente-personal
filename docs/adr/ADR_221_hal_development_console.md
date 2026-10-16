# ADR 221 — ROBY Development Console

## Estado

Accepted

## Contexto

El runtime local oficial ya existía, pero requería conocimiento previo de variables internas y no ofrecía diagnóstico ni una ruta clara para un usuario nuevo.

## Decisión

Introducir una consola de desarrollo fina alrededor del runtime oficial. `main.py` carga configuración local, valida requisitos mediante `--doctor`, explica errores de inicio y delega toda conversación a `LocalConversationConsole`.

## Consecuencias

- La experiencia inicial se vuelve reproducible y documentada.
- No se añade autoridad cognitiva ni operacional.
- La fábrica del runtime continúa siendo explícita.
- Los secretos y datos locales permanecen fuera del código y de los ZIP oficiales.
