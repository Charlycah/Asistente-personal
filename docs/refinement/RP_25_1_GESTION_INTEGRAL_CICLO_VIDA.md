# RP.25.1 — Gestión Integral del Ciclo de Vida

## Objetivo

Unificar inicio, cierre, reinicio y recuperación de ROBY sin duplicar autoridad ni
saltar el runtime oficial.

## Canales de salida

- cierre de ventana mediante `WM_DELETE_WINDOW`;
- menú **Roby > Salir**;
- botón **Salir**;
- órdenes locales como `Roby apagate`;
- reinicio mediante **Roby > Reiniciar** o `Roby reiniciate`.

Las órdenes de ciclo de vida se interpretan localmente y nunca se envían al modelo.

## Secuencia de cierre

1. bloquear solicitudes repetidas;
2. detener la escucha continua;
3. ejecutar el cierre del runtime oficial;
4. limitar cada paso mediante timeout;
5. registrar sesión, motivo y eventos;
6. destruir la interfaz;
7. relanzar el proceso solamente si se pidió reinicio.

## Estado persistido

El archivo privado `.roby/runtime/application_lifecycle.json` conserva:

- identificador SHA-256 de sesión;
- inicio y fin;
- duración;
- versión;
- motivo de salida;
- indicador de cierre limpio;
- últimos eventos de auditoría.

Al iniciar se escribe inmediatamente una sesión abierta. Si el proceso desaparece
sin completar el cierre, la ejecución siguiente detecta el estado incompleto,
registra recuperación y muestra un aviso breve.

## Garantías

- cierre idempotente;
- un único límite para X, menú, botón y voz;
- timeout configurable, por defecto cinco segundos;
- un fallo de un paso no impide intentar los restantes;
- el reinicio usa el mismo intérprete y los mismos argumentos;
- no se agrega capacidad cognitiva ni ejecución remota.
