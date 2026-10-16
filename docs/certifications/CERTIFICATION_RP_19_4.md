# Certificación RP.19.4

Hito: Planificación cognitiva deliberativa.

Criterios certificados:

- cola deliberativa única dentro de `CognitiveAgendaManager`;
- ponderación explicable de valor y costo;
- exclusión temporal de dependencias no satisfechas;
- agrupación por afinidad contextual;
- persistencia y migración SQLite compatible;
- consumo del primer foco planificado por el ciclo cognitivo oficial;
- ausencia de schedulers, residentes, runtimes, memorias o lifecycles paralelos;
- seis pruebas nuevas específicas;
- Ruff limpio y suite completa aprobada.

Resultado final: `ruff check .` limpio; `pytest -q`: 6507 pruebas aprobadas.
