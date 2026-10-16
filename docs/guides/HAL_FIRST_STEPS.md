# HAL XI.2 — Primeros pasos

## Inicio normal

```powershell
python main.py
```

HAL carga `.hal/config.json` y abre la interfaz de escritorio. `.env` ya no forma parte del arranque.

## Diagnóstico

```powershell
python main.py --doctor
```

El diagnóstico valida Python, `.hal/config.json`, la fábrica oficial, el endpoint y modelo local, y el directorio de estado.

## Crear configuración doméstica

Si `.hal/config.json` no existe, HAL lo crea automáticamente. También puede prepararse explícitamente:

```powershell
python main.py --setup
python main.py --setup --model llama3:latest
```

## Consola histórica

La consola interactiva está en retiro controlado y ya no forma parte del flujo
recomendado. El inicio personal normal y toda conversación nueva deben realizarse
desde la interfaz Desktop mediante `python main.py`.

La opción histórica se conserva temporalmente sólo para compatibilidad y para
migrar sus diagnósticos certificados antes de retirarla definitivamente.

## Configuración

La configuración persistente vive en:

```text
.hal/config.json
```

El proveedor local predeterminado es Ollama:

```json
{
  "providers": {
    "local": {
      "endpoint": "http://127.0.0.1:11434/v1",
      "model": "llama3:latest"
    }
  }
}
```

Las integraciones remotas son opcionales. No deben guardarse API keys, contraseñas ni tokens en este archivo. Gmail debe usar OAuth. Las claves de OpenWeather, Gemini y Mistral deben almacenarse mediante el gestor seguro de credenciales del sistema cuando se habilite su pantalla de conexión.

## Comprobación de Ollama

```powershell
ollama list
ollama serve
python main.py --doctor
python main.py
```

Si el modelo configurado no aparece en `ollama list`, cambie `providers.local.model` o instálelo con Ollama.
