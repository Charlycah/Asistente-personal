# ROBY XI.2 M304.9

- Se elimina la carpeta `.hal/` distribuida.
- `.roby/` queda como almacenamiento canónico de configuración y credenciales.
- La compatibilidad de migración desde `.hal/` se conserva en código y tests.
- La ruta predeterminada de `.roby/config.json` ahora se resuelve de forma estable desde la raíz del proyecto, incluso si ROBY se inicia desde otro directorio.
- No se modifican Vosk, VAD, umbrales acústicos, clima, noticias ni correo.
- Se retira una prueba manual del cargador de configuración raíz obsoleto.
- La prueba general del registro deja la cámara desactivada y no depende del cargador raíz obsoleto.
