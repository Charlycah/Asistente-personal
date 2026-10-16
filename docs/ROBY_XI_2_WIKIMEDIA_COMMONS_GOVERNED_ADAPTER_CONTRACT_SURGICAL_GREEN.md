# ROBY XI.2 — Wikimedia Commons Governed Adapter Contract
## Surgical GREEN

### Owner-certified input
Contract RED: 13,543 PASS / 7 intentional FAIL, Ruff clean.
The user-corrected RED test is integrated byte-for-byte as the canonical test.

### Productive GREEN
Exactly one productive module is introduced:
`app/wikimedia_commons_governed_source.py`

It implements the already-authorized adapter contract only:
- canonical source `wikimedia_commons`;
- empty topics with explicit `OPEN_VISUAL_SUBJECT_QUERY`;
- existing source classification enums only;
- read-only HTTPS Commons Action API query;
- File namespace and imageinfo/extmetadata projection;
- provider hard result bound 20 and thumbnail width 640;
- user parameters cannot override provider policy;
- non-blank configured User-Agent required before network I/O;
- governed query timeout propagation;
- bounded 2 MB response read;
- image MIME and HTTPS preview filtering;
- stable page-id identity;
- bounded attribution/license metadata preservation;
- malformed provider response fail-closed.

No executor registration, source-selection authority, presentation change,
freshness ordering, retry loop, background worker, or new authority is added.

### Historical semantic migration
One historical architecture test from the prerequisite seam contained a
time-local assertion that `app.wikimedia_commons_governed_source` did not
exist. That assertion correctly protected the earlier prerequisite from
premature provider implementation, but became obsolete once this provider
adapter seam was explicitly authorized.

The migration removes only the now-obsolete provider-module prohibition.
The enduring prohibitions against parallel open-visual registry, selector,
and query executor remain unchanged.

This is semantic guard migration, not hash/guard weakening.

### Local assistant verification
- canonical corrected RED test: 8 PASS;
- relevant provider/open-visual/query contracts: 66 PASS;
- Python syntax: clean;
- adapter maximum line length: 81;
- corrected RED test maximum line length: 86;
- historical migrated test maximum line length: within project bound;
- Ruff is unavailable in the assistant environment and is not claimed.

### Delta
Relative to the delivered Contract RED ZIP:
- productive Python: exactly 1 new file;
- canonical user-corrected RED test replaces the prior test;
- exactly 1 historical architecture test receives semantic migration;
- documentation only otherwise.

### State
`SURGICAL_GREEN: COMPLETE`
`PRODUCTIVE_ADAPTER: IMPLEMENTED`
`FOCAL_CONTRACT: 8 PASS`
`RELEVANT_CONTRACTS: 66 PASS`
`EXECUTOR_REGISTRATION: ZERO`
`PRESENTATION_CHANGE: ZERO`
`FRESHNESS: ZERO`
`NEW_AUTHORITY: NONE`
`RUFF: PENDING OWNER ENVIRONMENT`
`FULL_SUITE: PENDING OWNER CERTIFICATION`


## Post-GREEN master-plan closure
Owner full-suite certification: 13,550 PASS / 0 FAIL; Ruff clean.\nAdapter internal residual: NONE.\nNext parent residual: WIKIMEDIA_COMMONS_EXISTING_EXECUTOR_REGISTRATION_AND_REACHABILITY.\n