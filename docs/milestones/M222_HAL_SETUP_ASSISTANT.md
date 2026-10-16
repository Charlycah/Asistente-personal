# M222 — ROBY Setup Assistant

M222 convierte el onboarding documentado de M221 en un flujo ejecutable y seguro.

## Comandos

Configuración guiada:

```powershell
python main.py --setup
```

Configuración reproducible sin preguntas:

```powershell
python main.py --setup --non-interactive `
  --factory paquete.modulo:build_runtime_root `
  --model qwen2.5:7b
```

Diagnóstico posterior:

```powershell
python main.py --doctor
```

Inicio:

```powershell
python main.py
```

## Comportamiento

- Genera `.env` a partir de `.env`.
- Si `.env` ya existe, crea `.env.bak1`, `.env.bak2`, etc.
- Crea carpetas locales bajo `.roby/`.
- Consulta `ollama list` solo cuando el comando está disponible.
- Selecciona automáticamente el modelo únicamente cuando existe uno solo.
- No completa claves API, contraseñas ni secretos.
- Informa toda configuración obligatoria pendiente.

## Límites

M222 no instala Python, Ollama o modelos; no modifica el runtime; no despliega; no ejecuta herramientas cognitivas y no altera la certificación ROBY v1 de M220.
