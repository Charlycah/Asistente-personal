# ROBY — Roadmap por capas

## Core conversacional

- M3 — Intent Parser
- M4 — Decision Engine
- M5 — Execution Engine
- M6 — Response Layer
- M7 — Conversation
- M16 — Robustez de `ROBY.process()`

## Infraestructura interna

- M17 — Internal Event Publisher — HISTORICAL / RETIRED
- M18 — Memory Abstraction
- M19 — Memory Pipeline — HISTORICAL / RETIRED
- M20 — Tool System
- M21 — Persistent Memory
- M22 — Cache — HISTORICAL / RETIRED

## Adaptadores

- M23 — UI Adapter
- M24 — Desktop UI
- M25 — Voice Output
- M26 — Voice Input


## Agent execution lineage — historical

- M27 — Agent Runtime — HISTORICAL / RETIRED
- M28 — Agent Loop — HISTORICAL / RETIRED
- M31 — LLM Service — LEGACY COMPATIBILITY / PRESERVED
- M32 — Agent LLM Integration — HISTORICAL / RETIRED AT AGENTLOOP BOUNDARY
- M40 — Cognitive Pipeline — PRESERVED; AGENTLOOP BRIDGE RETIRED

## Regla arquitectónica

ROBY debe permanecer independiente de interfaces concretas, motores de voz,
almacenamiento específico, herramientas externas y frameworks de presentación.

Las capacidades externas se conectan mediante contratos y adaptadores.


## FASE V — Convivencia

La convivencia se construye sobre M50. No reemplaza el ciclo cognitivo: lo
consume como señal para sostener presencia, relación, memoria de convivencia,
continuidad y personalidad estable.

- M51 — Presencia continua
- M52 — Memoria de convivencia
- M53 — Iniciativa Controlada
- M54 — Regulación Social
- M55 — Personalidad Estable
- M56 — Rutinas y Hábitos
- M57 — Colaboración Prolongada
- M58 — Confianza y Explicabilidad
- M59 — Evolución sin romper arquitectura M50
- M60 — Principio Arquitectónico

Con M60 se cierra formalmente la Fase V: la convivencia queda definida como
capa superior que consume M50, preserva contratos y habilita evolución futura
sin reemplazar el ciclo cognitivo.

## Pre-Fase VI — Hardening de infraestructura

Antes de iniciar Autonomía, ROBY incorpora una capa mínima de gestión segura de
credenciales. Esta etapa no agrega una capacidad cognitiva nueva: prepara el
proyecto para herramientas externas reales sin versionar secretos.

- Pre-VI — Gestión segura de credenciales

Principio: las claves y tokens viven en `.env` o variables de entorno; el
repositorio solo conserva `.env` como contrato público.

## FASE VI — Autonomía

La autonomía se construye sobre la convivencia ya cerrada. ROBY no debe llamar
herramientas externas directamente desde el pipeline: debe solicitar
capacidades a una puerta única, con permisos, auditoría y contratos claros.

- M61 — Tool Gateway
- M62 — Registro de Capacidades
- M63 — Permisos y Consentimiento
- M63B — Descriptores Semánticos de Capacidades
- M64 — Ejecución Segura de Herramientas
- M65 — Clima y Pronóstico ✅
- M66 — Correo en modo lectura ✅
- M67 — Correo en modo acción ✅
- M68 — Cámara y percepción local ✅
- M69 — Planificación autónoma limitada ✅
- M70 — Autonomía gobernada ✅

M61 inaugura la fase con una puerta única de herramientas. Todavía no integra
adapters reales: establece el contrato para que clima, correo, cámara y futuras
capacidades entren sin acoplar APIs al núcleo cognitivo.

M62 agrega el catálogo declarativo de capacidades. M63 suma la capa de permisos
M63B amplía cada capacidad con descriptores semánticos para lenguaje natural.
y consentimiento para que el uso de herramientas externas sea gobernado antes
de ejecutar adapters reales.


## M65 — Clima y Pronóstico

M65 implementa el primer adapter real de Fase VI. Weather queda registrado como capacidad, gobernado por permisos y ejecutado detrás del Tool Gateway, sin acoplar APIs externas al pipeline cognitivo.

## M66 — Correo en modo lectura

M66 incorpora `mail.read` como adapter real de solo lectura. ROBY puede listar, buscar, resumir y leer correos detrás del Tool Gateway, con permisos de lectura y sin capacidad de envío o modificación de la casilla.


## M68 — Camera Adapter

Estado: implementado.

Introduce captura de cámara local como adapter externo gobernado por Tool Gateway, Capability Registry y Permissions & Consent.


## M69 — Autonomous Action Planning

ROBY puede proponer planes de acción basados en capacidades registradas, permisos y snapshots del Tool Gateway, sin ejecutar herramientas de forma autónoma.


## M70 — Governed Autonomy

M70 cierra la Fase VI con una política común de autonomía gobernada. ROBY puede proponer planes y coordinar capacidades, pero no ejecuta acciones sensibles sin consentimiento explícito, revisión y auditoría. Ante conflicto entre reglas, prevalece la política más restrictiva.

Con M70, la Fase VI queda formalmente consolidada: herramientas reales, permisos, adapters, planificación y gobernanza operan como capas separadas sobre M50–M60 sin acoplar APIs al núcleo cognitivo.
