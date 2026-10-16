# M367.2 — User Profile Model

## Objetivo

Declarar una representación gobernada del usuario dentro de `internal_world_model`, reutilizando las autoridades existentes de identidad, conocimiento personal, preferencias, relaciones y sesiones.

## Autoridad

`user_profile_model` es la única autoridad descriptiva del perfil. No reemplaza ni duplica los almacenes especializados.

## Autoridades reutilizadas

- `PersonalIdentityProfile`: identidad personal explícita y alcance privado o compartido.
- `LocalIdentityProfile`: nombres humanos locales, separados de credenciales.
- `PersonalKnowledgeBase`: conocimiento personal curado y revisable.
- `RelationshipMemoryManager`: preferencias y relaciones supervisadas, con confianza y procedencia.
- `PersonalIdentityRegistry`: vinculación explícita de sesión y perfil.
- `ScopeGuard`: límites de acceso, exposición y uso.

## Límites

M367.2 no infiere identidad, no completa campos ausentes, no actualiza automáticamente el perfil, no expone datos sensibles, no crea persistencia y no modifica el runtime.

Las preferencias repetidas pueden seguir siendo candidatas supervisadas, pero no se convierten silenciosamente en rasgos permanentes. Los datos personales permanecen privados, trazables y revisables.
