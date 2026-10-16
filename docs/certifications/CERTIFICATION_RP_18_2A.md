# Certificación RP.18.2A — Inventario de ejecutables y roots

RP.18.2A queda preparada para certificación local con los siguientes criterios:

- inventario inmutable de ejecutables y roots;
- un único punto de entrada canónico de proceso;
- una única fábrica oficial de runtime;
- una única raíz oficial de composición;
- todos los targets inventariados son importables;
- la composición histórica permanece identificada y sin eliminación prematura;
- no se altera ningún contrato operativo existente.

Validación requerida:

```powershell
ruff check .
pytest
```
