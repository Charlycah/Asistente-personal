# M227.6 — Production Readiness Certification

M227.6 closes the M227 Gmail deployment series with a secret-free go/no-go authority.

## Required evidence

- Gmail runtime state is `ready`.
- OAuth state is `ready` and usable.
- Retry attempts are positive and below the configured production ceiling.
- Provider timeout is positive and below the configured production ceiling.
- Write acceptance is disabled unless explicitly approved.
- Real-account acceptance has passed when required.

## Decisions

- `go`: every production criterion passed.
- `conditional`: the architecture and operational controls passed, but required live-account
  acceptance evidence has not yet been supplied.
- `no_go`: one or more runtime, OAuth, retry, timeout or write-policy controls failed.

The generated certificate contains only criterion names, bounded observations, the decision,
a timestamp and a deterministic SHA-256 identifier. It contains no tokens, paths, recipients,
queries, message identifiers, attachment names or payload contents.
