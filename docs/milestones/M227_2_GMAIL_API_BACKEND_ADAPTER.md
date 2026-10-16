# ROBY M227.2 — Gmail API Backend Adapter

M227.2 adds the concrete provider backend for Gmail API while preserving the
M226 governance, transport, retry, and runtime boundaries.

## Supported operations

| Canonical operation | Gmail API resource |
| --- | --- |
| `list_recent` | `users.messages.list` |
| `search` | `users.messages.list(q=...)` |
| `read` | `users.messages.get(format="full")` |
| `create_draft` | `users.drafts.create` |
| `send` | `users.messages.send` |

Draft and send operations generate a standards-based MIME message with the Python
standard library and encode it using URL-safe base64 as required by Gmail. An
optional `thread_id` is preserved for reply threading.

## Deployment boundary

`GoogleApiClientFactory` imports `googleapiclient.discovery.build` lazily and
receives credentials through a deployment-owned callable. No token, client
secret, credential path, message content, or provider exception text is published
through adapter status.

The repository does not require the Google SDK to run ordinary ROBY workflows.
A live deployment may install the Google client libraries separately and connect
them through the existing OAuth deployment adapter.

## Certification

- Ruff: All checks passed
- Focused cumulative Gmail tests: 132 passed
- New focused tests: 12 passed
- Full suite: 5832 passed
- Regression delta: zero
- Network calls in tests: none
- Credential files packaged: none
