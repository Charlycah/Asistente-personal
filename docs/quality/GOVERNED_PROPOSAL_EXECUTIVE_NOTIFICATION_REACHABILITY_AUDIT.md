# Governed Proposal → Executive Notification Reachability Audit

Status: **SURGERY IMPLEMENTED / PENDING OWNER CERTIFICATION**  
Certified input baseline: **12,355 PASS · 0 FAIL · Ruff clean**.

## Question

Can the existing governed proposal path reach Carlos/Cristina through the existing
Executive Notification spine without introducing a second initiative, proposal,
presentation, notification, or execution authority?

## Audit result

Yes. The pre-surgery repository already contained both mature ends of the path:

1. `OfficialConversationGateway` owns the existing governed proposal composition:
   `GovernedInitiativeEngine` → `GovernedProposalInbox` →
   `GovernedProposalPresentationPolicy` → `GovernedProposalLifecycle`.
2. `RuntimeExecutiveIntegration` owns the existing productive notification spine:
   `ExecutiveCoordinator` → `ExecutiveNotificationBroker` → presentation queue →
   Desktop `drain_notifications()`.

The missing seam was productive reachability between presentation-eligible governed
proposals and that existing executive spine.

## Controlled surgery

`app/governed_proposal_executive_notification_runtime.py` is a productive adapter,
not a new capability authority. It:

- asks `OfficialConversationGateway.next_presentable_governed_proposal()` for an
  already-authorized presentation candidate;
- projects that proposal into a `GenericTextEvent` with its canonical effective
  priority, expiry, and `proposal_id` correlation identity;
- publishes only through the existing `RuntimeExecutiveIntegration.publish()` path;
- subscribes to the existing `ExecutiveNotificationBroker` dispatch boundary;
- transitions `PENDING → OFFERED` through the existing gateway lifecycle only after
  the broker dispatches the event;
- owns no inbox, proposal model, relevance policy, attention policy, broker, store,
  persistence, execution permission, or self-improvement authority.

The official Desktop composition wires this adapter as a resident beside the existing
personal residents. `RuntimeExecutiveIntegration` is still constructed exactly once.

## Productive chain after surgery

```text
GovernedInitiativeEngine
  → GovernedProposalInbox (PENDING)
  → GovernedProposalPresentationPolicy
  → GovernedProposalExecutiveNotificationRuntime [adapter only]
  → RuntimeExecutiveIntegration.publish
  → ExecutiveCoordinator
  → ExecutiveNotificationBroker
  → presentation queue
  → Desktop drain_notifications()
  → Carlos / Cristina
  → GovernedProposalLifecycle (OFFERED after broker dispatch)
```

## Boundaries preserved

- No second `ExecutiveNotificationBroker`.
- No second `GovernedProposalInbox`.
- No new initiative or proposal authority.
- No direct autonomous execution.
- No new persistence.
- No `.roby` packaging.
- No modification to the Runtime Composition Root.
- Existing Executive attention/defer/silence policy remains authoritative for actual
  interruption/delivery.

## Validation in assistant environment

Focused regression collection:

- governed proposal model/inbox/initiative/query/lifecycle/presentation tests;
- Executive Notification Broker tests;
- Runtime Executive Integration tests;
- new end-to-end reachability tests.

Result: **56 passed**.

Owner certification remains the only closure gate:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
