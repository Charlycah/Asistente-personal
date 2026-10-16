# M362 — Governed Vision Gateway

**Estado:** Vigente  
**Predecesor canónico:** M361 — Quality Baseline  
**Tipo de cambio:** consolidación arquitectónica incremental

## 1. Objetivo

M362 establece `GovernedVisionGateway` como la frontera oficial de aplicación
para capacidades visuales y retención voluntaria de imágenes. No reemplaza
`OfficialVisionCore`: lo conserva como motor interno ya probado y evita crear
un segundo sistema de visión.

## 2. Autoridades

- `GovernedVisionGateway`: único punto de entrada nuevo para consumidores de aplicación.
- `OfficialVisionCore`: captura, análisis y gobernanza visual existente.
- `IntelligentVisionService`: política, consentimiento y eventos de observación.
- `ImageRepository`: contrato de persistencia visual.
- `FileImageRepository`: adaptador local privado para imágenes expresamente guardadas.

El runtime, los planners y las interfaces no deben llamar directamente a un
proveedor de cámara, OCR, detector o repositorio cuando adopten M362.

## 3. Capacidades preservadas

M362 conserva las capacidades existentes de captura, escena, objetos, personas,
rostros sin identidad, OCR, códigos visuales e inteligencia documental. La
fachada inicial delega captura y habilita la evolución posterior de las demás
operaciones sin modificar sus implementaciones estables.

## 4. Repositorio gobernado de imágenes

ROBY puede conservar JPEG, PNG y WebP proporcionados o seleccionados por el
usuario. Cada registro incluye identificador, propietario, etiqueta, categoría,
etiquetas, tipo MIME, tamaño, hash SHA-256 y fecha con zona horaria.

Casos admitidos:

- referencias visuales de personas;
- mascotas;
- documentos;
- objetos;
- imágenes generales.

Una referencia de persona es una imagen etiquetada, no una plantilla biométrica.
M362 no crea embeddings faciales, no identifica personas y no explora galerías
automáticamente.

## 5. Consentimiento y privacidad

Toda persistencia exige simultáneamente:

1. solicitud explícita del usuario;
2. consentimiento explícito para almacenar;
3. propietario y etiqueta no vacíos;
4. contenido de imagen no vacío;
5. formato permitido.

La captura transitoria continúa descartando los bytes crudos. Guardar una imagen
es una operación separada, deliberada y auditable. El repositorio puede omitirse;
en ese caso el gateway rechaza cualquier operación de retención.

## 6. Ciclo de vida

El adaptador local permite almacenar, consultar metadatos, listar por propietario
y eliminar. La eliminación borra tanto el archivo visual como su metadato. Los
identificadores se validan para impedir rutas arbitrarias.

La ubicación definitiva de datos privados deberá resolverse desde la
configuración canónica de `.roby/`; M362 no fija una ruta global ni agrega datos
personales al repositorio fuente.

## 7. Límites explícitos

M362 no incorpora:

- reconocimiento o identificación facial;
- inferencia de atributos sensibles;
- almacenamiento automático de capturas;
- vigilancia continua;
- nuevos modelos o proveedores externos;
- migraciones de imágenes existentes;
- cambios en precisión o rendimiento visual.

## 8. Quality gates

- Ruff limpio.
- Suite completa en verde.
- Sin `except:` desnudos nuevos.
- Persistencia denegada sin solicitud y consentimiento.
- Ningún resultado de captura expone bytes crudos.
- Ningún modelo de imagen contiene embeddings o plantillas biométricas.
- Snapshot M361 regenerado mediante su generador canónico.

## 9. Resultado

M362 convierte la visión existente en una capacidad con frontera única y añade
retención visual privada, explícita y reversible. Prepara futuras integraciones
de cámara y análisis sin debilitar el gobierno establecido desde M348.9.
