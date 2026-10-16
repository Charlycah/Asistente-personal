# M221 — ROBY Development Console

M221 añade una entrada de desarrollo utilizable sin modificar las autoridades cognitivas certificadas en M220.

## Entregables

- `main.py` con argumentos `--doctor`, `--observe`, `--no-lifecycle` y `--env`.
- Carga local y no destructiva de `.env` sin dependencias externas.
- Diagnóstico de Python, configuración, proveedor, modelo y almacenamiento.
- Banner y mensajes de incorporación accionables.
- Guía completa `docs/guides/ROBY_FIRST_STEPS.md`.
- Ayuda contextual desde `/help`.

## Límites

M221 no compone capacidades de forma implícita, no inventa proveedores, no despliega, no reinicia servicios y no muta el runtime. La consola llama al runtime oficial configurado y permanece como adaptador de entrada/salida.
