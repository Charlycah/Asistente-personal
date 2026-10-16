# M326.1 — Controlled Autonomy Contracts

M326.1 crea el lenguaje de dominio para que ROBY pueda decidir de forma
controlada en incrementos posteriores. Separa seis responsabilidades:

1. observar una situación;
2. proponer acciones candidatas;
3. evaluar riesgo, confianza, impacto y reversibilidad;
4. decidir bajo una política explícita;
5. observar el resultado;
6. registrar el ciclo completo.

La existencia de una disposición `authorize` no ejecuta la acción. Solo expresa
que una futura puerta de autonomía podría permitirla. M326.1 no incluye esa
puerta ni un ejecutor.

El valor predeterminado de `DecisionPolicy` es deliberadamente conservador:
recomendación, riesgo automático máximo bajo, acciones reversibles requeridas,
un solo intento y simulación activa.
