# ADR 222 — ROBY Setup Assistant

## Estado

Accepted

## Contexto

M221 hizo posible iniciar ROBY desde una consola de desarrollo, pero la primera configuración todavía exigía copiar archivos, crear directorios y conocer valores operativos antes de ejecutar el diagnóstico.

## Decisión

Añadir un asistente fino de instalación local accesible mediante `python main.py --setup`. El asistente crea `.env` desde `.env`, preserva configuraciones previas con backups, prepara la estructura `.roby`, detecta modelos de Ollama cuando están disponibles y deja pendientes explícitos para los valores que no puede inferir de forma segura.

También se ofrece un modo reproducible sin preguntas mediante `--non-interactive`, `--factory` y `--model`.

## Consecuencias

- Una persona nueva dispone de una ruta única de configuración.
- Los secretos continúan vacíos y nunca se inventan.
- Un `.env` existente nunca se pierde silenciosamente.
- La detección de Ollama es opcional, acotada y tolerante a fallos.
- M222 no instala modelos, no descarga dependencias, no despliega y no muta el runtime certificado.
