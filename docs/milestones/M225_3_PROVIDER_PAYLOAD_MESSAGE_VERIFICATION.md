# M225.3 — Provider Payload Message Verification

M225.3 makes structured transport unmistakable in the development console.

Acceptance evidence:

- `provider_payload ... transport=messages endpoint=/chat/completions`
- `provider_message_roles=user,assistant,user`
- a final `provider_messages_begin` / `provider_messages_end` block
- terminal marker `provider_transport_verified`

The full message content remains visible only under automatic `--observe` output.
