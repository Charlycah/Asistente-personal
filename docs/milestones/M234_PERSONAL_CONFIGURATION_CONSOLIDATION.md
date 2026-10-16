# M234 — Personal Configuration Consolidation

ROBY is a personal household installation. M234 establishes `.env` as its only configuration file.

The setup assistant no longer reads a template. It preserves existing values, creates a backup before updates, changes only setup-owned runtime fields, and creates required `.roby` directories.

Historical compatibility variables remain where active consumers still exist. Duplicate keys, `.env.example`, Python bytecode, and tool caches are removed.

Certification: Ruff clean; 5991 tests passed.
