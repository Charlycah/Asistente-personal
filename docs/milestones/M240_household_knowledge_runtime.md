# M240 — Household Knowledge Runtime

M240 connects ROBY's existing M72 structured household-memory domain to the official
runtime composition root.

## Operational contract

ROBY can explicitly store household facts through conversation, recall them later,
and archive obsolete entries. The data is shared by the `Familia` identity and is
persisted in SQLite.

Examples:

- `Guardá como conocimiento la garantía del lavarropas vence en diciembre`
- `Anotá como dato del hogar el teléfono del médico es 555-1234`
- `Qué sabés del hogar sobre lavarropas`
- `Archivá el dato lavarropas`

M240 does not replace M237 cognitive memory. Cognitive memory remains responsible
for governed learning from ordinary conversation; household knowledge stores only
facts explicitly requested by the household.

## Configuration

```env
ROBY_HOUSEHOLD_KNOWLEDGE_ENABLED=true
ROBY_HOUSEHOLD_KNOWLEDGE_DB_PATH=.roby/household_knowledge.db
```
