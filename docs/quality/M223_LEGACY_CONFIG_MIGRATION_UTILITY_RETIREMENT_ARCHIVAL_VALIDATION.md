# M223 Legacy Config Migration Utility Retirement + Historical Archival — Validation

## Status

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Input certified baseline:

**13.924 PASS · 0 FAIL · Ruff clean**

Expected owner baseline after this surgery:

**13.912 PASS · 0 FAIL · Ruff clean**

## Retired

- `app/legacy_config_migration.py`
- `tests/test_m223_legacy_configuration_migration.py` as a historical mixed suite
- twelve utility-only M223 contracts

## Preserved / reconciled

- three current config/setup contracts moved to `tests/test_roby_config_current_contract.py`
- `app.roby_config`, including its active JSON legacy migration path
- `.roby/config.json` setup and doctor behavior
- ADR-223 and CHANGELOG history
- historical manifests

## Archived

- `docs/guides/HAL_LEGACY_CONFIG_MIGRATION.md` -> `docs/history/guides/`
- `docs/guides/ROBY_LEGACY_CONFIG_MIGRATION.md` -> `docs/history/guides/`

The archived guides are explicitly marked historical/superseded because their `--import-legacy-config` command is no longer part of the current CLI.

No certification is claimed until the owner runs the official validation sequence.
