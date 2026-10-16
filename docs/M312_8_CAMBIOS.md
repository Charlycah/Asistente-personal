# M312.8 — Adaptador de identidad y perfil personal

## Objetivo

Incorporar al BRAIN una vista de solo lectura sobre la identidad local y los
perfiles personales existentes, sin activar el BRAIN en el diálogo normal.

## Fuentes

- `.roby/profile.toml`
- `.roby/identity/profiles.json`

## Identidades reconocidas

- Carlos
- Cristina
- Perfil compartido del hogar: Carlos y Cristina

## Garantías

- No hay migraciones.
- No hay escrituras desde el adaptador.
- No se modifica `main.py` ni `runtime_root_factory.py`.
- Las preferencias futuras pueden conservar propietario individual.
- El perfil compartido no mezcla automáticamente preferencias privadas.
