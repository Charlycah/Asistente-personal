# M94 — Conversational Opportunity Detection

## Objective

Detect genuine conversational opportunities from governed signals while
keeping detection strictly separate from intervention, timing and language
generation.

## Architecture

```text
Conversation / Memory / Reflection / Routine / Context signals
                              |
                              v
             M94 Conversational Opportunity Detector
                |-- validation and freshness
                |-- privacy and sensitivity filters
                |-- deterministic deduplication and ranking
                |-- bounded candidate conversion
                `-- immutable auditable detection record
                              |
                              v
                  M93 Living Conversation Manager
                   decides intervene / defer / review / silence
```

## Public contracts

- `ConversationSignalKind`
- `ConversationSignalSensitivity`
- `ConversationSignal`
- `OpportunityDetectionPolicy`
- `OpportunityDetectionRecord`
- `OpportunityDetectionRepository`
- `InMemoryOpportunityDetectionRepository`
- `ConversationalOpportunityDetector`

## Signal families

M94 recognizes signals for:

- explicit user turns;
- unfinished topics;
- memory connections;
- completed reflections;
- new knowledge;
- routine transitions;
- shared interests;
- context changes;
- external events.

## Governance boundary

M94 does not:

- authorize or execute an intervention;
- determine conversational timing;
- generate conversational language;
- call an LLM or tool;
- schedule deferred candidates;
- mutate memory, relationship state or mental models;
- bypass M93 privacy, review or silence decisions.

## Core invariants

- Detection never implies permission to speak.
- Every accepted opportunity preserves source provenance.
- Inputs are immutable and records are reproducible for equal inputs and time.
- Signals must satisfy minimum relevance, novelty and confidence.
- Stale and future signals are rejected.
- Guest contexts accept public signals only.
- Sensitive signals remain review-bound and cannot pass through sensitive
  contexts automatically.
- Duplicate sources and capacity overflow are explicitly audited.
- M93 remains compatible and unchanged.

## Acceptance criteria

- All supported signal kinds map deterministically to M93 opportunity kinds.
- Accepted candidates preserve content hints, confidence, provenance and review
  state.
- Rejected candidates expose explicit machine-readable reasons.
- Explicit user turns rank ahead of unsolicited candidates.
- Candidate count is policy-bounded.
- Empty input produces an auditable empty record.
- M94 output can be evaluated directly by M93.
- Ruff passes and the complete test suite has no regressions.
