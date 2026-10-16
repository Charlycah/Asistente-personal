# Instalar y comenzar a usar HAL desde cero

## 1. Abrir el proyecto

Extraé el ZIP y abrí la carpeta raíz en VS Code. La carpeta correcta contiene `main.py`, `app/`, `tests/` y `.roby/config.json`.

## 2. Crear el entorno virtual

En PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instalá las dependencias que use tu instalación del proyecto.

## 3. Ejecutar el asistente

```powershell
python main.py --setup
```

El asistente pregunta:

1. Nombre del propietario.
2. Identificador de sesión.
3. Endpoint del servidor local.
4. Modelo local.
5. Fábrica del runtime en formato `modulo:funcion`.

Presioná Enter para aceptar un valor mostrado entre corchetes.

## 4. Qué hace automáticamente

- Crea `.roby/config.json`.
- Preserva el `.roby/config.json` anterior con un archivo `.bakN`.
- Crea `.hal/logs`, `.hal/memory`, `.hal/backups` y otras rutas locales.
- Detecta modelos de Ollama mediante `ollama list` cuando Ollama está instalado.
- Mantiene vacías todas las claves y contraseñas.

## 5. Revisar pendientes

Si aparece:

```text
[OK] HAL_RUNTIME_ROOT_FACTORY
```

editá `.roby/config.json` y reemplazá:

```json
HAL_RUNTIME_ROOT_FACTORY=app.runtime_root_factory:build_runtime_root
```

por la fábrica real del proyecto.

Si aparece:

```text
[PENDIENTE] HAL_LOCAL_PROVIDER_MODEL
```

consultá:

```powershell
ollama list
```

y copiá el nombre exacto del modelo en `.roby/config.json`.

## 6. Diagnosticar

```powershell
python main.py --doctor
```

Los requisitos obligatorios deben aparecer como `[OK]`. Los `[WARN]` describen elementos opcionales.

## 7. Iniciar HAL

```powershell
python main.py
```

Primera instrucción recomendada:

```text
Hola HAL. Presentate, indicame qué capacidades están disponibles y guiame con una primera prueba segura.
```

## 8. Comandos útiles

```text
/help
/status
/last
/trace 3
/exit
```

## 9. Modo no interactivo

Para scripts o instalaciones reproducibles:

```powershell
python main.py --setup --non-interactive --factory modulo:funcion --model modelo
```

Si se omite un valor obligatorio, el asistente genera el archivo igualmente, lo marca como pendiente y devuelve un código distinto de cero.

## 10. Seguridad

- No compartas `.roby/config.json` ni `.roby/credentials.json`.
- No escribas secretos dentro de `.roby/config.json`.
- Revisá los backups `.roby/config.json.bakN` porque pueden contener secretos anteriores.
- M222 no descarga ni instala modelos automáticamente.
