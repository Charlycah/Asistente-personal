# Capacidades y guía de uso de ROBY XI.2

## Qué puede hacer

ROBY puede interpretar conversaciones, mantener contexto, planificar respuestas,
consultar memoria, explicar decisiones, registrar trazas y detectar anomalías.
También dispone de contratos para recordatorios, calendario, correo, archivos,
web, clima, voz, escritorio y dispositivos. La disponibilidad efectiva depende
de los adaptadores instalados, permisos y credenciales del equipo.

## Perfil personal

El perfil local no es una API key. Guarda datos de presentación del hogar sin
conceder acceso a servicios externos.

Archivo inicial incluido:

```toml
schema_version = 1

[people]
owner_name = "CARLOS"
partner_name = "CRISTI"
```

Para usar una ubicación privada en Windows:

```powershell
$env:ROBY_PROFILE_PATH = "$env:APPDATA\\ROBY\\profile.toml"
```

La clase `LocalIdentityProfileStore` permite cargar, guardar y borrar el perfil.
Las escrituras son atómicas para evitar archivos parcialmente escritos.

## Uso responsable

- Confirmar acciones que escriban, envíen, eliminen o controlen dispositivos.
- No introducir API keys en el perfil personal.
- Guardar secretos mediante variables de entorno o un almacén de credenciales.
- Revisar trazas y diagnósticos antes de habilitar automatizaciones sensibles.
