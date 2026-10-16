# M228.3 — Gmail Diagnostic Runtime

## Objective

Make the existing Gmail degraded startup state operationally diagnosable without
adding Gmail capabilities or weakening secret governance.

## Delivered

- Immutable diagnostic state, finding, and report models.
- Environment preflight for runtime, announcement policy, account, OAuth token,
  token JSON, required scope, Client Secrets, interactive policy, google-auth,
  Google API client, and interactive OAuth dependency.
- Safe exception-chain classification for configuration, permissions, imports,
  OAuth activation/refresh, credential persistence, Secure Credential Store,
  Gmail API subject lookup, operating-system faults, and unknown failures.
- Actionable startup console output with stable component/code identifiers.
- Secret-free structured serialization.
- Incremental integration into the M228.2 startup hook.
- Focused tests covering disabled, configured, malformed, missing, permission,
  dependency, scope, secure-store, provider, and redaction cases.

## Operational examples

```text
GMAIL> DEGRADED [configuration/account_missing]: No hay una cuenta Gmail configurada. Acción: Definir ROBY_GMAIL_ACCOUNT_ADDRESS.
GMAIL> DEGRADED [token/token_missing]: El archivo de token OAuth no existe. Acción: Ejecutar la activación OAuth interactiva o corregir ROBY_GMAIL_TOKEN_PATH.
GMAIL> DEGRADED [google_auth/dependency_missing]: Falta la dependencia google-auth. Acción: Instalar google-auth en el entorno de ejecución de ROBY.
GMAIL> DEGRADED [scopes/readonly_scope_missing]: El token OAuth no declara el scope Gmail de solo lectura requerido. Acción: Reautorizar la cuenta con gmail.readonly.
```

## Security invariants

- No token or credential value is emitted.
- No account address is emitted.
- No configured filesystem path is emitted.
- No raw exception text is emitted.
- No message body or snippet is requested.
- No mailbox mutation is introduced.
- No network call is made by diagnostic preflight.
