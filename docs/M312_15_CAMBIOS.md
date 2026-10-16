# M312.15 — Auditoría estructural del Brain

## Alcance

Se incorpora un mapa estructural de solo lectura para el Brain compuesto. La
inspección enumera componentes, dependencias, puntos de entrada y operaciones
con capacidad de escritura.

## Garantías

- No ejecuta consultas de memoria.
- No escribe ni modifica repositorios.
- No se conecta a `main.py` ni al runtime visible.
- No cambia respuestas ni decisiones conversacionales.
- El informe es determinista y serializable.

## Hallazgo principal

El pipeline compuesto mantiene separados los lectores externos, la resolución
de identidad, el contexto personal seguro, la preparación conversacional y su
diagnóstico. Las únicas operaciones de escritura declaradas pertenecen a
`BrainService`.
