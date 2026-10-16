> HISTORICAL / SUPERSEDED — This guide documents the retired M223 one-shot migration path. The referenced `--import-legacy-config` CLI is not part of the current ROBY runtime.

# Migrating an older HAL configuration

Place the old `config.json` somewhere outside the repository or in a temporary
folder, then run:

```powershell
python main.py --import-legacy-config .\config\config.json
python main.py --doctor
```

HAL imports these non-secret values:

- default city;
- Ollama model;
- voice provider and gTTS regional domain;
- Wikipedia language;
- Gmail address.

HAL deliberately skips passwords and API keys. Rotate any credential that was
stored in the old JSON and enter the new value directly in `.env`.

The old `credentials.json` and `token.pickle` are not copied. Configure their
paths with `GOOGLE_CLIENT_SECRET_FILE` and `GOOGLE_TOKEN_FILE` after obtaining
fresh OAuth material.

An existing `.env` is backed up as `.env.bak1`, `.env.bak2`, and so on.

The historical `leer_correos` and `enviar_correos` phrase lists are not needed:
modern HAL resolves intent semantically and applies tool permissions before
reading or sending mail.
