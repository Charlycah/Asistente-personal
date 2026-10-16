# ROBY M301 — RMS de audio con NumPy

Esta versión reemplaza el módulo obsoleto `audioop` por NumPy para calcular el nivel RMS de audio PCM de 16 bits.

## Cambios

- Eliminado `import audioop`.
- Cálculo RMS mediante `numpy.frombuffer`, `numpy.square`, `numpy.mean` y `numpy.sqrt`.
- Manejo seguro de buffers vacíos o con un byte incompleto.
- NumPy agregado a `requirements-audio-engine.txt`.
- Pruebas de regresión para una señal conocida y entradas incompletas.

## Instalación del backend de audio

```powershell
pip install -r requirements-audio-engine.txt
```
