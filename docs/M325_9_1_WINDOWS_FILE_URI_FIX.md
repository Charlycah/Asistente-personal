# M325.9.1 — Windows File URI Fix

`Path.as_uri()` produce correctamente URIs de Windows con esta forma:

```text
file:///C:/Users/.../map.html
```

El helper original de pruebas hacía:

```python
Path(urlparse(uri).path)
```

En Windows, `urlparse(uri).path` conserva `/C:/...`; al pasarlo directamente a
`Path`, se obtiene una ruta inválida cuya representación comienza con
`WindowsPath('/C:/...')`.

La corrección usa la función estándar dependiente de plataforma:

```python
Path(url2pathname(urlparse(uri).path))
```

En Windows convierte `/C:/...` a una ruta de unidad válida. En POSIX conserva
la semántica normal de las rutas locales.
