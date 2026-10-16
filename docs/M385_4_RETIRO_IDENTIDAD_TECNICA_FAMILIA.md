# M385.4 — Retiro controlado de la identidad técnica Familia

M385.4 retira del código productivo la representación de `Familia` como persona
o propietario. ROBY reconoce a Carlos y Cristina como sus dos copropietarios y
usa `Carlos y Cristina` únicamente como principal conjunto de compatibilidad del
runtime.

## Contrato activo

- copropietarios: Carlos y Cristina;
- perfil conjunto técnico: `carlos-cristina`;
- sesión conjunta técnica: `coowners-main`;
- principal de compatibilidad: `Carlos y Cristina`;
- perfiles personales: `carlos` y `cristina`;
- no existe un propietario principal en la configuración;
- `Familia`, `family-shared` y `household-main` no aparecen en producción.

El principal conjunto no representa una tercera persona. Es una adaptación
transitoria al campo histórico singular `owner`, cuya tipificación completa se
realizará en una etapa posterior.

## Migración controlada

En el primer bootstrap:

1. se regeneran únicamente los metadatos de perfiles;
2. se conserva Carlos y se normaliza el perfil histórico de la pareja como
   Cristina;
3. se crea el ámbito conjunto `carlos-cristina`;
4. las sesiones históricas se condensan en `coowners-main`, preservando la fecha
   de creación más antigua y la actividad más reciente;
5. el estado de runtime más reciente se copia a la ruta nueva;
6. el manifiesto registra versión `M385.4` y ambos copropietarios.

La migración no abre, renombra, combina ni elimina bases de memoria,
recordatorios, salud, objetivos, proyectos, agenda o credenciales. La ruta
anterior del estado de runtime permanece físicamente recuperable.

## Configuración

La sección doméstica pasa de un único `owner` a:

```json
"owners": ["Carlos", "Cristina"]
```

Al cargar una configuración histórica, ROBY elimina el campo singular y
normaliza perfil y sesión. El valor `ROBY_RUNTIME_OWNER` se conserva
temporalmente como adaptador de compatibilidad con el texto `Carlos y Cristina`;
no declara un propietario principal.

## Límites

M385.4 no identifica todavía quién habla en cada turno y no migra propietarios
de memoria. Tampoco retira aún todos los nombres históricos `owner`, `partner`,
`spouse` o `shared` de contratos aislados. Estos límites evitan combinar datos
sin inventario y mantienen el cambio reversible.

## Certificación

Los tests M385.3 y M385.4 verifican:

- ausencia de la identidad retirada en producción;
- exactamente Carlos y Cristina como personas reconocidas;
- perfil y sesión conjuntos neutrales;
- normalización de metadatos históricos;
- copia del estado de runtime;
- configuración con dos copropietarios;
- acceso conjunto a recordatorios;
- preservación de atribución individual en salud.

