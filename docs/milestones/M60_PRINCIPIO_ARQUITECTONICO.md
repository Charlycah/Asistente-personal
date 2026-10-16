# M60 — Principio Arquitectónico

## Estado

Completado como cierre formal de la Fase V — Convivencia.

## Propósito

M60 consolida el principio rector que permitió desarrollar la Fase V sin romper
la arquitectura M50:

> La convivencia no reemplaza el ciclo cognitivo M50; lo consume como ancla y
> agrega capas opcionales, auditables y compatibles hacia atrás.

## Alcance

M60 no introduce una capacidad conversacional aislada. Introduce una capa de
consolidación arquitectónica que verifica:

- presencia del ciclo cognitivo M50 como ancla;
- integración acumulativa de M51–M59;
- uso de dependencias opcionales en `CognitivePipeline`;
- preservación de contratos públicos;
- cierre explícito de la Fase V cuando todas las capas están presentes.

## Componentes

- `ArchitecturalPrincipleSignal`
- `ArchitecturalPrincipleStatus`
- `ArchitecturalPrinciplePolicy`
- `ArchitecturalPrincipleSnapshot`
- `ArchitecturalPrincipleEngine`
- `ArchitecturalPrincipleManager`

## Integración

`CognitivePipeline` acepta `architectural_principle` como dependencia opcional.
Cuando está presente, observa el turno después de M59 y agrega líneas auditables
al `system_prompt`.

No modifica el contrato obligatorio del pipeline ni sustituye módulos previos.

## Cierre de Fase V

Con M60 la Fase V queda cerrada porque el sistema ya cuenta con:

- presencia continua;
- memoria de convivencia;
- iniciativa controlada;
- regulación social;
- personalidad estable;
- rutinas y hábitos;
- colaboración prolongada;
- confianza y explicabilidad;
- protección de evolución;
- principio arquitectónico consolidado.

## Garantías

- M50 sigue siendo el ancla cognitiva.
- M51–M60 son capas superiores y opcionales.
- No se exige refactor destructivo.
- La compatibilidad hacia atrás permanece como contrato.
- El cierre de Fase V queda expresado de forma auditable.
