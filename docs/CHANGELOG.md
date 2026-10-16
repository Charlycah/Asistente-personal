## RF-E — Explicit Case Evidence → Governed Context Claim Projection v1

- Added deterministic projection from certified case grounding into contextual proposed claims.
- Reused `ContextualRuleInstantiationSpec` predicates/values and case-grounding bindings without semantic re-encoding.
- Preserved `HYPOTHESIS` / `HUMAN` / `PROPOSED` epistemology; no projected claim establishes truth.
- Kept unknown, ambiguous, unsupported, scope-mismatched, and provenance-mismatched cases fail-closed with zero partial claims.
- Added no repository, persistence, Memory/Learning, provider, retrieval, registry, admission, inference invocation, or authority gain.

## M226.1 — Gmail Governed Integration

- Added a Gmail-specific governed composition boundary over the existing M66/M67 adapters.
- Enforced local per-action policy before mandatory Tool Gateway routing and consent.
- Added normalized account fingerprinting and bounded secret-free audit records.
- Kept send disabled by default and introduced no OAuth, Google API, runtime-root, or network-test changes.
- Added ADR 226.1, milestone documentation, manifest, and 12 focused tests.

## M197 — Conversational Repair and Clarification Intelligence

- Added deterministic detection of missing references, underspecified requests, uncertain intent, corrections, and abrupt topic shifts.
- Added bounded repair actions for proceeding, targeted clarification, correction confirmation, and topic-shift acknowledgement.
- Integrated M197 immediately after M196 in the official cognitive runtime.
- Preserved advisory-only behavior with no blocking, provider, tool, memory, planning, or mutation authority.
- Added focused classification, traceability, composition-order, and request-preservation tests.


## M177 — Governed Operational Conversation Pipeline

- Added the first official operational conversation pipeline for non-greeting turns.
- Added immutable request, preparation, result, configuration, status, and append-only repository contracts.
- Added an injected preparation port so M177 contains no intent classification, policy, routing, or retrieval-planning logic.
- Integrated exact M173 local execution, optional M171 retrieval execution, and M175 response assembly lineage.
- Added direct compatibility with the operational pipeline contract consumed by M176.
- Contained failures as governed non-deliverable responses and prohibited platform mutation.
- Added ADR-179 and 27 focused M177 tests; 4971 total tests pass.

## M167 — Local-First Provider Policy

- Added a declarative local-first policy downstream from M166.
- Added local-preferred, remote-fallback, no-provider-required, withheld, and not-applicable outcomes.
- Added capability-aware eligibility for local and remote providers.
- Preferred local providers for ordinary and sensitive workloads.
- Required explicit remote handling for current-information workloads.
- Kept provider selection, inference, routing, network access, and platform mutation outside M167.
- Added ADR-169 and 29 focused M167 tests.

## M161 — Unified Companion Integration

- Added the terminal declarative integration boundary downstream from M160.
- Added ready, degraded, hold, blocked, and not-applicable unified companion outcomes.
- Consolidated exact M160 → M159 → M158 → M157 → M156 → M155 → M150 lineage into seven ordered stage references.
- Added conservative propagation for mixed or negative experience, degraded or unavailable reliability, consent, continuity, timing, and confidence conditions.
- Added deterministic immutable integration results and an append-only repository contract.
- Kept activation, conversation start, device/channel selection, context transfer, scheduling, prompt/response generation, provider calls, automation, and platform mutation outside M161.
- Added ADR-163 and 34 focused M161 tests.

## M160 — Long-Term Experience Evaluation

- Added a declarative longitudinal experience boundary downstream from M159.
- Added explicit experience observations linked to immutable reliability results.
- Added positive, mixed, negative, insufficient, review-required, blocked, and not-applicable classifications.
- Added governed evaluation of horizon, sample count, temporal span, source confidence, explicit feedback, exclusions, score, and negative-outcome ratio.
- Preserved exact representative M159 → M158 → M157 → M156 → M155 → M150 lineage.
- Kept memory mutation, learning, personality changes, policy changes, knowledge evolution, conversation activation, scheduling, provider calls, automation, and platform mutation outside M160.
- Added ADR-162 and 46 focused M160 tests.

## M141 — Presence Context Integration

- Added governed integration of M140 presence situations with declared device, conversation, spatial, and temporal context.
- Added complete/partial integration classification, lineage and freshness controls, deterministic immutable results, repository contract, ADR-143, and 55 focused tests.
- Preserved strict prohibitions on identity, activity, tracking, decisions, behavior adaptation, sensor access, and automation.

# Changelog

## M133 — Visual Context Integration

- Added the terminal governed integration boundary for M128–M132.
- Added immutable `IntegratedVisualContext` outputs with exact lineage validation.
- Added ready, partial, review-required, blocked and not-applicable outcomes.
- Preserved available upstream capabilities without recalculating visual evidence.
- Kept pixel access, camera control, detection, tracking, OCR, product search, place recognition and biometrics outside M133.
- Added ADR-135, milestone documentation and 62 focused M133 tests.

## M120 — Driving Conversation Adaptation

- Added a declarative adaptation boundary after M119.
- Added standard, concise, essential, acknowledgement-only and emergency styles.
- Added governed word and sentence budgets, question permission, confirmation, chunking and resumable remainder handling.
- Preserved M119 as the authority for interaction permissions and mode.
- Kept text generation, voice execution, turn management, navigation and sensor access outside M120.
- Added ADR-122, milestone documentation and 47 focused M120 tests.

## M108 — Cross-Device Context Transfer

- Added governed context fragment descriptors and transfer manifests.
- Integrated M106 continuity decisions with M107 capability matches.
- Added sensitivity, expiry, capability and fragment-limit governance.
- Added deterministic manifest integrity and auditable repository storage.
- Preserved strict separation from transport, synchronization and device arbitration.
- Added ADR-110 and 38 focused M108 tests.

## M107 — Device Capability Registry

- Added immutable device capability descriptors, registrations and requirements.
- Added governed evaluation for state, access, freshness, confidence, versions and features.
- Preserved M106 as the authority for device identity and session continuity.
- Added repository, ADR, milestone documentation and focused tests.

## M106 — Device Identity and Session Continuity

- Added stable device identity, trust, capabilities, and endpoint observation contracts.
- Added immutable companion session and continuity decision models.
- Added governed cross-device eligibility evaluation and deterministic opaque resume cursor.
- Added repository, ADR, milestone documentation, and 37 tests.

## M105 — Living Conversation Integration

- Added the final governed integration boundary for Phase X.
- Added immutable cycle status, next-move recommendation, activation eligibility,
  user-floor preservation, ordered stage references, and deterministic identity.
- Validated owner continuity across the complete nested M93–M104 chain.
- Propagated review, closure, silence, and non-applicable states conservatively.
- Preserved strict non-execution boundaries: no delivery, scheduling, tools,
  memory mutation, automatic learning, or upstream rewriting.
- Added ADR 107, milestone documentation, verification evidence, and 39 tests.

## M104 — Intellectual Curiosity Engine

- Added governed curiosity proposals derived from M103 shared interests.
- Added question, connection, counterpoint, exploration, and revisit kinds.
- Added immutable policies, requests, plans, repositories, source traceability,
  review propagation, exclusions, limits, and deterministic identifiers.
- Added ADR 106, milestone documentation, verification evidence, and 40 tests.
- Validation: Ruff clean; 1560 tests passing.

## M103 — Shared Intellectual Interests

- Added typed, immutable evidence for shared intellectual interests.
- Added conservative topic aggregation, confidence scoring and strength levels.
- Added explicit review, insufficient and not-applicable outcomes.
- Preserved source traceability and M102 rhythm context.
- Prevented automatic persistence to memory, learning or personality.
- Added ADR-105 and 35 focused M103 tests.

## M102 — Conversational Rhythm Regulation

- Added governed brisk, steady, measured, paused, and closing rhythms.
- Added advisory cadence intervals and maximum consecutive ROBY-turn limits.
- Added follow-up permission and explicit user-floor preservation.
- Added interruption, silence, long-response, and observed-cadence inputs.
- Preserved strict boundaries: no waiting, scheduling, delivery, rewriting, memory mutation, or automatic learning.
- Added ADR-104 and 33 focused M102 tests.

## M101 — Conversational Feedback Loop

- Added governed post-presence feedback assessment.
- Added explicit, implicit, and system feedback signals.
- Added advisory conversational adjustments without automatic learning or mutation.
- Added immutable repository-backed assessments and 32 focused tests.

# Changelog

## M100 — Conversational Presence Engine

- Added a governed conversational-presence envelope after M99.
- Added responsive, attentive, companionable, reflective and restrained stances.
- Added direct-reply, follow-up, continuation and spontaneous-entry turn relations.
- Added bounded intensity, prior-turn acknowledgement and controlled follow-up openness.
- Preserved M99 text and sources without rewriting or delivery.
- Kept M100 explicitly separate from M51 cognitive presence.
- Added ADR-102 and 32 focused M100 tests.

## M99 — Conversational Realization Layer

- Added deterministic realization of approved M98 contributions into channel-neutral utterances.
- Added answer, question, observation, connection and continuation conversational acts.
- Added concise, natural and deliberate registers with bounded ordered segments.
- Added optional owner address and title inclusion with normalized punctuation.
- Preserved M98 status, owner identity and source provenance.
- Added character and segment limits, question integrity and fail-closed abstention.
- Added immutable repository contracts, ADR-101 and 32 focused M99 tests.
- Explicitly excluded delivery, channel selection, voice, scheduling, tools and memory mutation.

## M98 — Intellectual Companion Layer

- Added deterministic assembly of governed reflections into intellectual contributions.
- Added literature, music, science, history, philosophy, culture, personal-project and general domains.
- Added response, question, connection, context and continuation contribution kinds.
- Added depth scoring, source requirements, bounded concept enrichment and review/abstention outcomes.
- Preserved M93 governance, M95 timing and M96 reflection identity as mandatory upstream authorities.
- Added immutable repository contracts, ADR-100 and 37 focused M98 tests.
- Explicitly excluded delivery, LLM calls, retrieval, scheduling, tools and memory mutation.

## M97 — Longitudinal Conversation Continuity

- Added immutable, sourced conversation episodes and longitudinal topic threads.
- Added open, dormant, resolved and closed thread lifecycle states.
- Added governed resume, hold, review, closure and already-proposed assessments.
- Added minimum/maximum resume gaps and bounded resume budgets.
- Prevented duplicate episodes, repeated latest content and duplicate resume proposals.
- Produced provenance-preserving M93 `resume` opportunities without speaking or scheduling.
- Added ADR-099 and 36 focused M97 tests.

## M96 — Reflection Generation

- Added governed, deterministic reflection draft generation.
- Added generated, abstained and review-required outcomes.
- Added response, question, observation, connection and continuation forms.
- Preserved M93 governance and M95 timing as mandatory upstream authorities.
- Required content hints and source traceability for spontaneous reflections.
- Added immutable records, repository contract, ADR-098 and 28 focused tests.
- Explicitly excluded LLM calls, delivery, scheduling, tools and memory mutation.

## M95 — Conversation Timing Engine

- Added governed temporal recommendations for valid conversation opportunities.
- Added activity, cognitive-load, quiet-hour, cooldown and interruption-budget controls.
- Added privacy, guest, sensitive-context and review precedence.
- Added immutable timing decisions with earliest windows, expiry and repository contract.
- Preserved the non-execution boundary: M95 does not speak, schedule or generate content.
- Added ADR-097 and 26 focused M95 tests.
- Quality gate: Ruff clean and 1255 tests passing.

## M94 — Conversational Opportunity Detection

- Added immutable typed signals for conversational, memory, reflection, routine, context and external-event sources.
- Added deterministic freshness, relevance, novelty, confidence and sensitivity validation.
- Added source deduplication, explicit rejection reasons and bounded candidate ranking.
- Converted accepted signals into provenance-preserving M93 conversation opportunities.
- Preserved M93 as the exclusive intervention decision boundary.
- Added ADR-096 and 29 focused M94 tests.

## M93 — Living Conversation Foundation

- Opened Phase X with the governed `core.living_conversation` package.
- Added explicit conversation opportunities, contexts, policies and dispositions.
- Made intervention, deferral, review and silence immutable auditable decisions.
- Protected do-not-disturb, sensitive contexts and guest privacy by construction.
- Kept message generation, scheduling, tools and memory mutation outside M93.
- Added ADR-095 and 24 focused M93 tests.

# Changelog

## M92 — Adaptive Cognition Integration

- Added a single governed integration boundary for M85–M91.
- Added immutable adaptive-cognition cycles with per-stage status and references.
- Centralized the safe M84 → M85 → M87 → M88 automatic flow.
- Preserved explicit invocation for knowledge evolution, planning and coordination.
- Added capability readiness reporting and optional CognitivePipeline integration.
- Closed Phase IX with ADR-094 and 20 focused M92 tests.

## M91 — Executive Coordination

- Added governed executive coordination for approved M90 plans.
- Added immutable subsystem directives, dependencies and revisions.
- Preserved the boundary between coordination and execution.
- Added optional CognitivePipeline integration and 20 tests.

## M90 — Executive Planning

- Added immutable, revisioned executive plans for strategic multi-horizon work.
- Added explicit objectives, success criteria, priorities, milestones and dependencies.
- Preserved references to reflections, mental models and knowledge proposals.
- Added governed lifecycle transitions without scheduling or execution authority.
- Required review for long-horizon and critical plans.
- Integrated M90 optionally with Cognitive Pipeline.
- Added ADR-092 and 20 focused M90 tests.

## M89 — Knowledge Evolution

- Added immutable knowledge-evolution proposals and explicit decisions.
- Added create, reinforce, supersede and retire proposal actions.
- Preserved reflection, mental-model and PKB provenance without mutation.
- Prohibited automatic approval and separated approval from application.
- Blocked high-risk approval attempts and escalated low-confidence proposals.
- Integrated M89 optionally with Cognitive Pipeline.
- Added ADR-091 and 20 focused M89 tests.

## M88 — Reflection Engine

- Added immutable longitudinal reflection records and observations.
- Detected score trends, recurring issues, recommendations and review frequency.
- Preserved M85, M86 and M87 inputs as immutable references.
- Kept all recommendations advisory for future governed knowledge evolution.
- Integrated M88 optionally with Cognitive Pipeline.
- Added ADR-090 and 20 focused M88 tests.

## M87 — Meta-Reasoning

- Added immutable meta-reasoning assessments and findings.
- Evaluated evidence sufficiency, conflicts, uncertainty, scope and explanations.
- Added advisory recommendations without automatic re-execution or action.
- Integrated M87 optionally with Cognitive Pipeline.
- Added ADR-089 and focused M87 tests.

## M86 — Mental Model Framework

- Added governed, immutable and revisioned mental models.
- Added assertion provenance, confidence and lifecycle states.
- Added explicit episode-derived update proposals and review policy.
- Added conflict preservation, deterministic query and pipeline guidance.
- Added ADR-088, milestone documentation and 20 focused tests.

## M85 — Episodic Memory

- Opened Phase IX with the `core.adaptive_cognition` package.
- Added immutable episodes, events, references and stable fingerprints.
- Added append-only contiguous revision history and repository contracts.
- Added governed deterministic recall by owner, domain, status, sensitivity, tags and time.
- Captured M84 results with context, decision and explanation traceability.
- Preserved the separation between experience, facts, learning, knowledge and action.
- Added optional Cognitive Pipeline integration, ADR-087 and 19 focused tests.
- Quality gate: 1036 tests passing; Ruff unavailable in the delivery environment.

## M84 — Governed Reasoning Orchestrator

- Added a single governed orchestration boundary for M79–M83.
- Added immutable governed reasoning policies, statuses, results and snapshots.
- Recorded completed, abstained, blocked and review-required executions.
- Integrated Decision Records and Explainable Answers for every run.
- Added optional backward-compatible Cognitive Pipeline integration.
- Preserved the separation between reasoning, permissions and external action.
- Added ADR-086, 15 focused M84 tests and the formal Phase VIII closure.

## M83 — Explainable Answers

- Added deterministic concise, standard and audit explanations from M82 Decision Records.
- Added immutable explanation sections, traceable citations and stable answer identities.
- Separated factual basis from versioned rule-derived inference.
- Rendered conclusions, abstentions, blocked outcomes and human-review requirements explicitly.
- Exposed confidence bands, conflicts, limitations, assumptions and review history.
- Added structured and plain-text public renderings without unrestricted chain-of-thought.
- Added ADR-085 and 29 focused M83 tests.

## M82 — Decision Records

- Added immutable Decision Records with stable audit identities.
- Added explicit decision status, public outcome and human-review state.
- Linked evidence fingerprints, claim revisions, rule versions and conflicts.
- Preserved confidence, Scope Guard status, limitations and assumptions.
- Added repository contracts and deterministic in-memory persistence.
- Added review approval and rejection through superseding records.
- Added ADR-084 and 23 focused M82 tests.

## M81 — Conflict & Uncertainty

- Added immutable conflict, resolution and uncertainty domain models.
- Added deterministic detection of incompatible active claims.
- Excluded stale and superseded claims from active conflict analysis.
- Added policy-driven precedence and mandatory review for high-severity conflicts.
- Added confidence factors, conflict penalties and unresolved-conflict caps.
- Added optional analysis of M80 applied inference claims.
- Added ADR-083 and 21 focused M81 tests.

## M80 — Governed Inference

- Added deterministic, single-pass inference over M79 reasoning contexts.
- Added immutable and versioned declarative inference rules.
- Added equality, membership and query-time temporal claim conditions.
- Added governed inference statuses, policies, results and reproducible runs.
- Produced only explicit rule-result claims with rule provenance.
- Bounded output confidence by rule and input confidence.
- Preserved Scope Guard domains, review propagation and abstention.
- Added ADR-082 and 28 focused M80 tests.

## M79 — Context Assembly

- Added governed, deterministic context assembly over M77 evidence and M78 claims.
- Added normalized reasoning queries with owner, domain, topic, explicit-reference and as-of boundaries.
- Added explicit selection policies, inclusion/exclusion decisions and reproducible context fingerprints.
- Applied Scope Guard before context retrieval and propagated blocked or review-required outcomes.
- Added owner, lifecycle, validity, relevance and capacity filters.
- Excluded derived Daily Briefing evidence by default while allowing explicit policy opt-in.
- Added ADR-081 and 26 focused M79 tests.

## M78 — Claim Registry

- Added immutable, typed claims separated from normalized evidence.
- Added explicit claim origins, statuses and evidence-link roles.
- Added factual, observational, hypothetical, assumption, rule-result, absence-of-evidence and conflict claim types.
- Added semantic fingerprints, duplicate protection and deterministic listing.
- Added repository contracts with immutable revision history and supersession.
- Added evidence-backed registration with support, corroboration and review-required propagation.
- Added ADR-080 and 23 focused M78 tests.

## M77 — Evidence Model

- Added the `core.governed_reasoning` package for FASE VIII.
- Added immutable evidence references with stable provenance-derived identifiers.
- Added deterministic evidence bundles and adapter contracts.
- Normalized Household Memory, documents, personal knowledge, tasks and Daily Briefing.
- Preserved source status, ownership, validity, fingerprints and conservative sensitivity.
- Integrated evidence normalization with Scope Guard without modifying source records.
- Added ADR-079 and 21 focused M77 tests.
- Quality gate in delivery environment: 852 tests passing; Ruff unavailable locally.

## M76 — Daily Briefing

- Added deterministic morning, evening and on-demand briefings.
- Aggregated tasks, Household Memory, documents and personal knowledge.
- Added urgency levels, owner filtering and source traceability.
- Integrated Daily Briefing with Scope Guard and Cognitive Pipeline.
- Added ADR-078 and focused M76 tests.

## M75 — Task Intelligence

- Added governed task candidates and structured personal tasks.
- Added deterministic prioritization using urgency, importance and deadlines.
- Added acyclic task dependencies and ready-task detection.
- Added human review for autonomous suggestions and low-confidence candidates.
- Integrated Household Memory, Document Inbox and Personal Knowledge Base.
- Integrated task context with the Cognitive Pipeline and M46 Planning.
- Added ADR-077 and 18 focused tests.
- Quality gate: Ruff clean and 816 tests passing.

Los cambios relevantes del proyecto ROBY se documentan en este archivo.

## M74 — Personal Knowledge Base

- Nuevo subsistema de conocimiento personal trazable y gobernado.
- Candidatos, aprobación humana, fuentes, confianza y estados de ciclo de vida.
- Relaciones, deduplicación, reemplazo, archivado e integración documental.
- Integración con Scope Guard y Cognitive Pipeline.
- Ruff limpio y 798 tests aprobados.

## M73 — Document Inbox

- Nuevo subsistema documental gobernado por Scope Guard.
- Clasificación, búsqueda, deduplicación SHA-256 y archivado.
- Integración opcional con Household Memory y Cognitive Pipeline.
- Ruff limpio y 782 tests aprobados.

## M109 — Active Device Arbitration

- Added governed active-device arbitration over M106–M108 contracts.
- Added deterministic candidate scoring and conservative switch margins.
- Added explicit stay, switch, confirm and none decisions.
- Added immutable repository-backed decisions and 34 focused tests.

## M110 — Mobile Companion Foundation

- Added governed mobile operating modes and runtime eligibility assessment.
- Integrated M109 device arbitration and M107 capability compatibility.
- Added policy controls for freshness, battery, network, presence, background, and hands-free modes.
- Preserved strict non-execution boundaries for mobile I/O and session mutation.

## M111 — Mobile Conversation Runtime

- Added an immutable mobile conversation state machine over M110 foundations.
- Added explicit idle, running, waiting-user, background, suspended, and terminated states.
- Added governed start, resume, wait, background, suspend, stop, and none decisions.
- Preserved strict non-I/O boundaries for audio, notifications, sensors, transport, and session mutation.
- Added ADR-113 and 40 focused M111 tests.

## M112 — Mobile Presence Lifecycle

- Added an immutable mobile presence lifecycle over M111 runtime decisions.
- Added inactive, activating, active, background, dormant, suspending, and terminated presence states.
- Added governed activate, maintain, background, dormant, suspend, terminate, and none actions.
- Added conservative handling of device availability, connectivity, user presence, and signal freshness.
- Preserved strict non-I/O boundaries for notifications, audio, sensors, transport, and operating-system lifecycle mutation.
- Added ADR-114 and 42 focused M112 tests.

## M113 — Notification Intelligence

- Added governed mobile notification evaluation over M112 presence decisions.
- Added urgency, sensitivity, relevance, freshness, expiry, quiet-hours, and duplicate controls.
- Added explicit surface, defer, suppress, confirm, and none recommendations.
- Added deterministic interruption scoring and immutable repository-backed decisions.
- Preserved strict non-delivery boundaries for operating-system notifications and mobile I/O.
- Added ADR-115 and 50 focused M113 tests.

## M114 — Background Conversation Continuity
- Added governed mobile background checkpoint and resume decisions.
- Added immutable models, repository, policy, engine, ADR, milestone documentation, and tests.

## M115 — Mobile Context Awareness
- Added governed declarative mobile context assembly over M112 presence and M114 continuity.
- Added activity, attention, connectivity, power, orientation, lock, presence, confidence, and freshness modeling.
- Added explicit ready, review-required, blocked, and not-applicable outcomes.
- Added deterministic immutable snapshots and an in-memory repository.
- Preserved strict non-sensor and non-I/O boundaries for GPS, Bluetooth, audio, camera, motion sensors, notifications, and platform mutation.
- Added ADR-117 and 44 focused M115 tests.

## M116 — Hands-Free Interaction Foundation
- Added governed hands-free eligibility over M110, M111, M112, and M115 contracts.
- Added standby, push-to-talk, and continuous declarative modes.
- Added consent, permission, audio-route, speaker, attention, lock, transit, confidence, and freshness controls.
- Added deterministic immutable decisions and an in-memory repository.
- Preserved strict non-I/O boundaries for microphone, audio capture, STT, TTS, wake words, Bluetooth, sensors, and platform mutation.
- Added ADR-118 and 38 focused M116 tests.

## M117 — Driving Companion Foundation
- Added governed driving-companion eligibility over M115 context and M116 hands-free contracts.
- Added inactive, passenger, driver-ready, and driver-active logical modes.
- Added consent, freshness, confidence, passenger, active-driving, and hands-free policy controls.
- Added deterministic immutable decisions and an in-memory repository.
- Preserved strict non-I/O boundaries for GPS, maps, routing, vehicle sensors, Bluetooth, Android Auto, CarPlay, STT, TTS, and audio execution.
- Added ADR-119 and 39 focused M117 tests.

## M118 — Driving Context Awareness
- Added governed declarative driving-context awareness over the M117 decision.
- Added vehicle motion, maneuver demand, traffic complexity, visibility demand, attention, passenger, emergency, confidence, and freshness modeling.
- Added parked, low, elevated, high, and critical contextual-load classifications.
- Added conservative speech and proactive-interaction suitability declarations.
- Added deterministic immutable snapshots and an in-memory repository.
- Preserved strict non-I/O boundaries for GPS, maps, routing, vehicle sensors, camera, audio, Bluetooth, Android Auto, CarPlay, traffic, and weather services.
- Added ADR-120 and 39 focused M118 tests.
- Quality gate: Ruff clean and 2129 tests passing.

## M119 — Driving Interaction Policy
- Added governed driving interaction policy over M118 contextual-load snapshots.
- Added user, ROBY, and system-alert directions with routine, important, urgent, and emergency urgency.
- Added normal, brief, minimal, silent, and emergency-only interaction envelopes.
- Added explicit listening, response, proactivity, interruption, acknowledgement, deferral, and response-duration constraints.
- Added deterministic immutable decisions and an in-memory repository.
- Preserved strict non-execution boundaries for conversation realization, STT, TTS, audio, notifications, maps, navigation, sensors, vehicle systems, Android Auto, and CarPlay.
- Added ADR-121 and 47 focused M119 tests.
- Quality gate: Ruff clean and 2176 tests passing.

## M120 — Driving Conversation Adaptation
- Added governed conversational-form adaptation over M119 interaction decisions.
- Added standard, concise, essential, acknowledgement-only, silent, and emergency styles.
- Added word, sentence, question, confirmation, chunking, and resumable-deferral constraints.
- Added deterministic immutable plans and an in-memory repository.
- Preserved strict non-realization boundaries for language generation, STT, TTS, audio, turn-taking, maps, navigation, and sensors.
- Added ADR-122 and 47 focused M120 tests.
- Quality gate: Ruff clean and 2223 tests passing.

## M121 — Driving Safety Coordination
- Added the final governed safety boundary over M118 context, M119 interaction policy, and M120 conversation adaptation.
- Added strict ownership and identifier-lineage validation across the complete upstream chain.
- Added clear, guarded, restricted, critical, and emergency safety levels.
- Added declarative permissions for conversation, voice, initiative, complex dialogue, interruptions, notifications, confirmation, and deferral.
- Added an explicit policy-controlled emergency override restricted to emergency system alerts.
- Added deterministic immutable decisions and an in-memory repository.
- Preserved strict non-execution boundaries for language realization, STT, TTS, audio, notification delivery, maps, navigation, sensors, and vehicle systems.
- Added ADR-123 and 49 focused M121 tests.

## M122 — Maps Foundation
- Added a governed provider-neutral Maps domain reusable across mobile, driving, walking, travel, visual, and ambient contexts.
- Added validated declared coordinates, confidence, source, freshness, purpose, precision, scope, and consent modeling.
- Added deterministic immutable `MapContext` records and an in-memory repository.
- Explicitly prohibited route computation at the foundation layer.
- Preserved strict non-I/O boundaries for GPS, geocoding, tiles, places, traffic, routing, navigation, sensors, and platform mutation.
- Added ADR-124 and focused M122 tests.
- Quality gate: Ruff clean and 2332 tests passing.

## M123 — Location Resolution
- Added governed location-reference resolution downstream from M122 Maps Foundation.
- Added current-location, coordinate, address, place, and region reference modeling.
- Added deterministic candidate selection, confidence thresholds, ambiguity handling, ownership lineage validation, and policy controls.
- Added immutable `ResolvedLocation` records and an in-memory repository.
- Preserved strict non-I/O boundaries for GPS, geocoding, providers, places search, routing, navigation, traffic, sensors, and platform mutation.
- Added ADR-125 and focused M123 tests.
- Quality gate: Ruff clean and 2386 tests passing.

## M124 — Places Knowledge
- Added governed place knowledge downstream from M123 Location Resolution.
- Added typed category, address, description, attribute, relation, and operating-context facts.
- Added confidence filtering, external-evidence policy, deterministic duplicate handling, and explicit conflict review.
- Added immutable `PlaceKnowledgeProfile` records and an in-memory repository.
- Preserved strict non-I/O boundaries for providers, places search, geocoding, recommendations, routing, navigation, traffic, rendering, sensors, and platform mutation.
- Added ADR-126 and focused M124 tests.
- Quality gate: Ruff clean and 2447 tests passing.

## M125 — Route Intent Modeling
- Added governed route-intent modeling downstream from M123 Location Resolution and optional M124 Places Knowledge.
- Added driving, walking, cycling, transit, and mixed travel modes with fastest, shortest, simplest, accessible, and safest priorities.
- Added declared constraints, purpose, time windows, waypoint limits, confidence governance, deterministic duplicate handling, and explicit conflict review.
- Added immutable `RouteIntent` records and an in-memory repository.
- Explicitly limited ready output to declaring that future route computation is required.
- Preserved strict non-I/O boundaries for geocoding, providers, distance and duration calculation, route optimization, traffic, navigation, rendering, sensors, and platform mutation.
- Added ADR-127 and focused M125 tests.
- Quality gate: Ruff clean and 2515 tests passing.

## M126 — Navigation Coordination
- Added governed navigation coordination downstream from M125 Route Intent Modeling.
- Added ownership-lineage validation, explicit authorization, provider readiness, optional surface readiness, and background-preparation policy.
- Added immutable `NavigationCoordinationDecision` records and an in-memory repository.
- Explicitly prohibited route calculation, navigation start, live guidance, traffic, geometry, steps, and instructions.
- Preserved strict non-I/O boundaries for GPS, providers, Maps SDKs, sensors, rendering, Android Auto, CarPlay, and platform mutation.
- Added ADR-128 and 41 focused M126 tests.
- Quality gate: Ruff clean and 2556 tests passing.

## M127 — Map Context Integration
- Added the terminal governed integration boundary over M122–M126 Maps outputs.
- Added strict ownership and identifier-lineage validation across map context, locations, place profiles, route intent, and navigation coordination.
- Added ready, partial, review-required, blocked, and not-applicable integration states.
- Added immutable `IntegratedMapContext` records and an in-memory repository.
- Added declarative availability for spatial context, place knowledge, route intent, and M126 routing preparation.
- Explicitly prohibited route calculation, navigation start, live guidance, traffic, geometry, steps, and instructions.
- Preserved strict non-I/O boundaries for GPS, providers, Maps SDKs, sensors, rendering, Android Auto, CarPlay, and platform mutation.
- Added ADR-129 and 51 focused M127 tests.

## M128 — Visual Understanding Foundation
- Added the provider-neutral governed Visual Understanding foundation.
- Added declarative visual observation source, media type, privacy, confidence, freshness, consent, provenance, and device identity modeling.
- Added immutable `VisualContext` records and an in-memory repository.
- Added explicit policy governance for external observations, restricted privacy, confidence, freshness, and reference limits.
- Structurally prohibited scene understanding, object recognition, OCR/text extraction, biometrics, image I/O, camera access, and provider calls.
- Added ADR-130 and focused M128 tests.
- Quality gate: Ruff clean and 2669 tests passing.

## M129 — Visual Observation Resolution
- Added governed visual representation resolution downstream from M128 Visual Understanding Foundation.
- Added original, preview, document-page, video-keyframe, and screen-region representation modeling.
- Added purpose-aware deterministic candidate selection with confidence, provenance, lineage, deduplication, and policy limits.
- Added immutable `ResolvedVisualObservation` records and an in-memory repository.
- Structurally prohibited pixel access, biometrics, image I/O, OCR, object recognition, scene inference, provider calls, and platform mutation.
- Added ADR-131 and focused M129 tests.
- Quality gate: Ruff clean and 2731 tests passing.

## M130 — Scene Understanding
- Added governed scene-level understanding downstream from M129 Visual Observation Resolution.
- Added indoor, outdoor, vehicle, workspace, retail, document, screen, natural, urban, and unknown scene-kind modeling.
- Added deterministic evidence filtering, duplicate resolution, attribute consolidation, confidence governance, and explicit ambiguity review.
- Added immutable `SceneUnderstandingResult` records and an in-memory repository.
- Structurally prohibited pixel access, object recognition, text extraction, place recognition, biometrics, provider calls, and platform mutation.
- Added ADR-132 and focused M130 tests.
- Quality gate: Ruff clean and 2792 tests passing.


## M131 — Object Knowledge
- Added governed object knowledge downstream from M130 Scene Understanding.
- Added typed object identity, category, label, attributes, count, confidence, and evidence lineage modeling.
- Added deterministic evidence filtering, duplicate resolution, object consolidation, confidence governance, and explicit ambiguity review.
- Added immutable `ObjectKnowledgeProfile` records and an in-memory repository.
- Structurally prohibited pixel access, object detection, tracking, text extraction, product search, place recognition, biometrics, provider calls, and platform mutation.
- Added ADR-133 and focused M131 tests.
- Quality gate: Ruff clean and 2856 tests passing.

## M132 — Visual Attention
- Added governed visual attention downstream from M130 Scene Understanding and M131 Object Knowledge.
- Added typed attention evidence, priorities, focus items, deterministic consolidation, confidence governance, and explicit ambiguity review.
- Added immutable `VisualAttentionPlan` records and an in-memory repository.
- Preserved exact M130→M131 lineage and restricted attention to known M131 objects.
- Structurally prohibited gaze control, image cropping, pixel access, detection, tracking, OCR, product search, place recognition, biometrics, provider calls, and platform mutation.
- Added ADR-134 and focused M132 tests.
- Quality gate: Ruff clean and 2911 tests passing.

## M133 — Visual Context Integration
- Added the terminal governed integration boundary over M128–M132 Visual Understanding outputs.
- Added strict ownership and identifier-lineage validation across visual context, observation resolution, scene understanding, object knowledge, and visual attention.
- Added ready, partial, review-required, blocked, and not-applicable integration states.
- Added immutable `IntegratedVisualContext` records and an in-memory repository.
- Structurally prohibited pixel access, camera control, detection, tracking, OCR, product search, place recognition, biometrics, provider calls, and platform mutation.
- Added ADR-135 and 62 focused M133 tests.
- Quality gate: Ruff clean and 2973 tests passing.

## M134 — Ambient Context Foundation
- Added the provider-neutral governed Ambient Context foundation.
- Added declarative ambient observation source, scope, privacy, confidence, freshness, consent, provenance, and device identity modeling.
- Added immutable `AmbientContext` records and an in-memory repository.
- Added explicit policy governance for external observations, restricted privacy, confidence, freshness, and reference limits.
- Structurally prohibited presence inference, activity inference, acoustic analysis, environmental-condition analysis, spatial inference, automation, sensor access, provider calls, and platform mutation.
- Added ADR-136 and focused M134 tests.
- Quality gate: Ruff clean and 3051 tests passing.

## M135 — Ambient Observation Resolution
- Added provider-neutral ambient observation resolution downstream from M134.
- Added typed purposes and raw-signal, snapshot, temporal-window, aggregate, and event representations.
- Added strict ownership and observation-lineage validation, confidence filtering, provenance governance, deterministic deduplication, and stable selection.
- Added immutable `ResolvedAmbientObservation` records and an in-memory repository.
- Structurally prohibited sensor access, presence or activity inference, acoustic or environmental-condition analysis, spatial inference, automation, provider calls, and platform mutation.
- Added ADR-137 and 66 focused M135 tests.
- Quality gate: Ruff clean and 3117 tests passing.

## M136 — Presence Understanding
- Added governed anonymous presence understanding downstream from M135 Ambient Observation Resolution.
- Added unoccupied, occupied, single-presence, multiple-presences, transient, and unknown state modeling.
- Added deterministic evidence filtering, duplicate resolution, attribute consolidation, confidence governance, and explicit ambiguity review.
- Added immutable `PresenceUnderstandingResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 ownership and observation lineage.
- Structurally prohibited identity inference, biometrics, precise person counting, activity inference, movement tracking, sensor access, automation, provider calls, and platform mutation.
- Added ADR-138 and focused M136 tests.

## M137 — Presence Continuity
- Added governed anonymous presence continuity downstream from M136 Presence Understanding.
- Added continuous, transition, interrupted, review-required, blocked, and not-applicable states.
- Added arrival, departure, occupancy-change, transient-change, and uncertain-change classification.
- Added deterministic temporal ordering, deduplication, freshness, gap, confidence, ownership, and ambient-context-lineage governance.
- Added immutable `PresenceContinuityResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 lineage without identity persistence semantics.
- Structurally prohibited identity inference, biometrics, precise person counting, activity inference, individual tracking, movement tracking, sensor access, automation, provider calls, and platform mutation.
- Added ADR-139 and 68 focused M137 tests.

## M138 — Presence Change Detection
- Added governed anonymous presence change detection downstream from M137 Presence Continuity.
- Added detected, no-change, review-required, blocked, and not-applicable outcomes.
- Added appearance, disappearance, occupancy-variation, transient-variation, uncertain-variation, and continuity-break change kinds.
- Added deterministic result ordering, deduplication, freshness, confidence, ownership, and ambient-context-lineage governance.
- Added explicit suppression of stable continuity without reinterpreting M136 evidence or duplicating M137 transition logic.
- Added immutable `PresenceChangeDetectionResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 → M138 lineage.
- Structurally prohibited identity inference, biometrics, precise person counting, activity inference, individual tracking, movement tracking, sensor access, automation, provider calls, and platform mutation.
- Added ADR-140 and 79 focused M138 tests.

## M139 — Presence Event Interpretation
- Added governed anonymous presence event interpretation downstream from M138 Presence Change Detection.
- Added interpreted, no-event, review-required, blocked, and not-applicable outcomes.
- Added normalized presence-observed, presence-unobserved, occupancy-shift, transient-signal, certainty-change, and continuity-loss meanings.
- Added deterministic result ordering, deduplication, freshness, confidence, ownership, and ambient-context-lineage governance.
- Added explicit suppression of M138 no-change outcomes without redetecting changes or recomputing M137 continuity.
- Added immutable `PresenceEventInterpretationResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 → M138 → M139 lineage.
- Structurally prohibited identity inference, biometrics, precise person counting, activity or intent inference, individual or movement tracking, sensor access, automation, provider calls, and platform mutation.
- Added ADR-141 and 73 focused M139 tests.

## M140 — Presence Situation Assessment
- Added governed anonymous presence situation assessment downstream from M139 Presence Event Interpretation.
- Added assessed, stable, review-required, blocked, and not-applicable outcomes.
- Added stable, transition, uncertain, and interrupted situation kinds with normalized situational signals.
- Added deterministic result ordering, deduplication, freshness, confidence, ownership, and ambient-context-lineage governance.
- Added explicit suppression of stable M139 no-event outcomes without reinterpreting events or recomputing prior presence stages.
- Added immutable `PresenceSituationAssessmentResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 → M138 → M139 → M140 lineage.
- Structurally prohibited identity inference, biometrics, precise person counting, activity or intent inference, individual or movement tracking, response decisions, sensor access, automation, provider calls, and platform mutation.
- Added ADR-142 and 58 focused M140 tests.

## M141 — Presence Context Integration
- Added governed anonymous presence context integration downstream from M140 Presence Situation Assessment.
- Added complete and partial integration of explicitly declared device, conversation, spatial, and temporal dimensions.
- Added deterministic result ordering, deduplication, freshness, confidence, ownership, and ambient-context-lineage governance.
- Preserved absent context dimensions without inference or synthetic completion.
- Added immutable `PresenceContextIntegrationResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 → M138 → M139 → M140 → M141 lineage.
- Structurally prohibited identity, biometric, activity or intent inference, tracking, response decisions, behavior adaptation, sensor access, automation, provider calls, and platform mutation.
- Added ADR-143 and 55 focused M141 tests.
- Quality gate: Ruff clean and 3503 tests passing.

## M142 — Presence Context Publication
- Added the canonical governed publication boundary downstream from M141 Presence Context Integration.
- Added complete and explicitly partial publication outcomes with canonical topic and schema-version metadata.
- Added deterministic payload digests without copying, rewriting, or reinterpreting the selected M141 context.
- Added deterministic ordering, deduplication, freshness, confidence, ownership, result-limit, and ambient-lineage governance.
- Added immutable `PresenceContextPublicationResult` records and an in-memory repository.
- Preserved exact M134 → M135 → M136 → M137 → M138 → M139 → M140 → M141 → M142 lineage.
- Structurally prohibited consumer invocation, identity or activity inference, tracking, response decisions, behavior adaptation, sensor access, provider calls, automation, and platform mutation.
- Added ADR-144 and 45 focused M142 tests.
- Quality gate: Ruff clean and 3548 tests passing.

## M143 — Presence Context Subscription

- Added a declarative subscription boundary for canonical M142 presence-context publications.
- Added governed topic, schema-version, completeness-filter, and lifecycle matching.
- Added immutable subscription records and repository protocol.
- Explicitly prohibited delivery, callback invocation, consumer processing, inference, behavioral decisions, provider calls, automation, and platform mutation.
- Added 53 focused tests; complete suite now contains 3601 passing tests.

## M144 — Presence Context Dispatch

- Added deterministic dispatch planning between M142 publications and M143 subscriptions.
- Added topic, schema-version, lifecycle and partial-context compatibility filtering.
- Added immutable destinations, deduplication and governed empty/review/blocked outcomes.
- Kept delivery, callbacks, routing execution, consumer processing and automation forbidden.
- Added 55 focused tests; complete suite now contains 3656 passing tests.

## M145 — Presence Context Delivery

- Added governed logical delivery materialization downstream from M144 dispatch plans.
- Added immutable per-destination delivery records for complete and partial context.
- Preserved exact dispatch, publication, subscription, topic, schema-version, and ambient lineage.
- Added deterministic delivery and delivery-item identifiers, freshness, confidence, ownership, deduplication, and result-limit governance.
- Kept transport delivery, callbacks, routing execution, consumer processing, inference, behavioral decisions, provider calls, automation, and platform mutation forbidden.
- Added 48 focused tests; complete suite now contains 3704 passing tests.

## M146 — Presence Context Consumption Gateway

- Added a governed consumer-facing gateway downstream from M145 logical deliveries.
- Added consumer, topic, schema-version, freshness, confidence, ownership, deduplication, and access-limit governance.
- Added immutable complete and partial context access records while preserving exact M145 lineage.
- Added explicit empty outcomes for valid deliveries without compatible consumer access.
- Kept consumer execution, context transformation, consumption confirmation, callbacks, transport, inference, behavioral decisions, provider calls, automation, and platform mutation forbidden.
- Added 56 focused tests; complete suite now contains 3760 passing tests.

## M147 — Living Conversation Presence Consumer

- Added the first domain consumer downstream from M146 Presence Context Consumption Gateway.
- Added immutable Living Conversation presence cues preserving exact M146 access and M140 situation lineage.
- Added complete, partial, empty, review-required, blocked, and not-applicable outcomes.
- Added owner, consumer, freshness, confidence, deduplication, and result-limit governance.
- Kept conversational decisions, activation, prompt generation, response realization, consumer execution, identity/activity/intent inference, behavioral adaptation, provider calls, automation, and platform mutation forbidden.
- Added 47 focused tests.

## M148 — Living Conversation Presence Awareness

- Added a governed Living Conversation awareness layer downstream from M147 presence cues.
- Added immutable stable, transitional, uncertain, and interrupted awareness states.
- Added complete, partial, empty, review-required, blocked, and not-applicable outcomes.
- Preserved exact M147 consumer-result and cue lineage.
- Added owner, freshness, confidence, deduplication, and result-limit governance.
- Kept conversational decisions, activation, timing selection, prompt generation, response realization, identity/activity/intent inference, behavioral adaptation, provider calls, automation, and platform mutation forbidden.
- Added 50 focused tests; complete suite now contains 3857 passing tests.

## M149 — Living Conversation Presence Policy

- Added a governed Living Conversation presence-policy layer downstream from M148 awareness.
- Added immutable eligibility evaluations for stable, transitional, uncertain, and interrupted awareness states.
- Stable awareness is eligible; transitional, uncertain, and interrupted awareness is explicitly inhibited.
- Added configurable handling of partial awareness plus owner, freshness, confidence, deduplication, and result-limit governance.
- Preserved exact M148 awareness-result and state lineage.
- Kept conversational decisions, activation, timing selection, prompt generation, response realization, identity/activity/intent inference, behavioral adaptation, provider calls, automation, and platform mutation forbidden.
- Added ADR-151 and 57 focused tests; complete suite now contains 3914 passing tests.

## M150 — Living Conversation Presence Opportunity

- Added a governed opportunity layer downstream from M149 presence policy.
- Added immutable available, partially available, and inhibited presence opportunities.
- Preserved exact M149 policy lineage with deterministic selection and identifiers.
- Added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept conversational decision, activation, timing selection, prompt generation, response realization, identity/activity/intent inference, behavioral adaptation, provider calls, automation, and platform mutation forbidden.
- Added ADR-152 and 45 focused tests; complete suite now contains 3959 passing tests.

## M151 — Living Conversation Opportunity Prioritization

- Added governed prioritization downstream from M150 presence opportunities.
- Added immutable high, medium, and deferred priority outcomes with deterministic ranking.
- Preserved exact M150 opportunity lineage and added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept conversational decision, activation, timing selection, prompt generation, response realization, inference, behavioral adaptation, provider calls, automation, and platform mutation forbidden.

## M152 — Living Conversation Opportunity Selection

- Added deterministic selection of one governed M151 opportunity candidate.
- Preserved exact M151 and M150 source objects and declarative boundaries.
- Added explicit full, partial, deferred, review, blocked, and not-applicable outcomes.
- Kept conversation decision, activation, timing, prompts, responses, providers, automation, and platform mutation forbidden.

## M153 — Living Conversation Conversation Readiness

- Added governed conversation readiness downstream from M152 opportunity selection.
- Added immutable ready, partially ready, and not-ready outcomes.
- Preserved exact M152 selection and M150 opportunity lineage.
- Added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept conversation decision, activation, timing, prompts, responses, providers, automation, and platform mutation forbidden.
- Added ADR-155 and 47 focused tests; complete suite now contains 4093 passing tests.

## M154 — Living Conversation Conversation Eligibility Decision

- Added a governed eligibility-decision layer downstream from M153 conversation readiness.
- Added immutable eligible, partially eligible, and not-eligible outcomes.
- Preserved exact M153 readiness and M150 opportunity lineage.
- Added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept conversation start, activation, timing, prompts, responses, inference, behavioral adaptation, providers, automation, and platform mutation forbidden.
- Added ADR-156 and 47 focused tests; complete suite now contains 4140 passing tests.

## M155 — Living Conversation Conversation Candidate

- Added a governed canonical candidate layer downstream from M154 eligibility decisions.
- Added immutable complete, partial, and withheld candidate outcomes.
- Preserved exact M154 decision and M150 opportunity lineage.
- Added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept conversation authorization, start, activation, timing, prompts, responses, inference, behavioral adaptation, providers, automation, and platform mutation forbidden.
- Added ADR-157 and 50 focused tests; complete suite now contains 4190 passing tests.

## M156 — Living Conversation Conversation Timing Evaluation

- Added a governed temporal-viability evaluation layer downstream from M155 conversation candidates.
- Added immutable timely, partially timely, deferred, and not-timely outcomes.
- Added explicit timezone-aware `not_before` and `expires_at` window evaluation without selecting or scheduling a clock time.
- Preserved exact M155 candidate and M150 opportunity lineage.
- Added owner, freshness, confidence, partial-context, deduplication, and result-limit governance.
- Kept timing selection, scheduling, conversation authorization, start, activation, prompts, responses, inference, behavioral adaptation, providers, automation, and platform mutation forbidden.
- Added ADR-158 and 51 focused tests; complete suite now contains 4241 passing tests.

## M157 — Cross-Context Continuity

- Added a governed cross-context continuity layer downstream from M156 timing evaluation.
- Added explicit immutable source and target context references spanning desktop, mobile, driving, home, work, walking, travel, ambient, and physical-world contexts.
- Added continuous, partially continuous, interrupted, review-required, blocked, and not-applicable outcomes.
- Added temporal-order, maximum-gap, availability, authentication, optional shared-session, and optional shared-thread governance.
- Preserved exact M156 timing-evaluation, M155 candidate, M150 opportunity, and context-reference lineage.
- Kept device handoff, context transfer, active-device arbitration, channel selection, timing selection, scheduling, conversation authorization, activation, prompts, responses, inference, behavioral adaptation, providers, automation, and platform mutation forbidden.
- Added ADR-159 and 62 focused tests; complete suite now contains 4303 passing tests.

## M158 — Unified Permission and Consent

- Added a governed unified permission-and-consent layer downstream from M157 cross-context continuity.
- Added explicit immutable capability/scope requirements and cross-context consent grants.
- Added satisfied, partially satisfied, consent-required, denied, review-required, blocked, and not-applicable outcomes.
- Added owner, scope, context-coverage, grant-time, expiration, revocation, denial, freshness, confidence, deduplication, and input-limit governance.
- Preserved exact M157 continuity, M156 timing-evaluation, M155 candidate, and M150 opportunity lineage.
- Kept permission mutation, consent prompting, conversation authorization, activation, handoff, transfer, routing, scheduling, prompts, responses, providers, automation, and platform mutation forbidden.
- Added ADR-160 and 52 focused tests; complete suite now contains 4355 passing tests.

## M159 — Companion Reliability Model

- Added a governed companion-reliability layer downstream from M158 unified permission and consent.
- Added explicit immutable reliability observations for source/target contexts, conversation pipeline, permission service, device runtime, and network path.
- Added reliable, degraded, unavailable, review-required, blocked, and not-applicable outcomes.
- Added ownership, freshness, context coverage, availability, health, error-rate, latency, deduplication, and input-limit governance.
- Preserved exact M158 permission, M157 continuity, M156 timing, M155 candidate, and M150 opportunity lineage.
- Kept telemetry collection, recovery, failover, handoff, transfer, routing, scheduling, conversation activation, prompts, responses, providers, automation, and platform mutation forbidden.
- Added ADR-161 and 56 focused tests; complete suite now contains 4411 passing tests.

## PM1 / M162 — Runtime Readiness Gate

- Started FASE X — PUESTA EN MARCHA with a declarative runtime readiness boundary downstream from M161.
- Added immutable required/optional component checks for configuration, memory, providers, services, permissions, storage, network, capabilities, and other runtime dependencies.
- Added ready, degraded, blocked, configuration-required, provider-unavailable, and not-applicable outcomes.
- Preserved exact M161 unified companion integration lineage and conservative confidence.
- Added provider availability visibility without selecting or calling Ollama, Llama 3, Gemini, Mistral, or any external service.
- Kept startup, activation, service execution, provider calls, network access, conversation start, and platform mutation forbidden.
- Added ADR-164 and focused tests.

## M163 — Conversation Entry Point

- Added a declarative first-message classifier downstream of M162.
- Added distinct routes for greetings, questions, requests, continuations,
  comments, attention calls, farewells, and incomplete messages.
- Prevented `Hola ROBY` from entering a command acknowledgement path.
- Preserved a strict no-generation and no-side-effect boundary.

## M164 — Natural Greeting Response

- Added deterministic natural greeting realization downstream from M163.
- Replaced command acknowledgement behavior with short conversational variants.
- Added day-period awareness and recent-response avoidance.
- Preserved the no-provider, no-network, and no-platform-mutation boundary.
- Added ADR-166 and focused tests.

## M165 - ROBY Voice and Style Policy

- Added a provider-independent voice and style policy for ROBY.
- Added accent-free visible Spanish normalization.
- Added rejection of bureaucratic and command-acknowledgement phrases.
- Preserved deterministic, side-effect-free lineage from M164.

## M166 - Provider Health Evaluation

- Added immutable health observations for local and remote model providers.
- Added provider state, model, endpoint, version, capability, latency,
  configuration, and reachability visibility.
- Added healthy, degraded, unavailable, configuration-required, and
  not-applicable outcomes downstream from M162.
- Preserved a strict no-provider-call, no-network, and no-mutation boundary.
- Added ADR-168 and focused tests.

## M167 - Local-First Provider Policy

- Added capability-aware local-first provider preference downstream from M166.
- Added local-preferred, remote-fallback, no-provider-required, withheld, and
  not-applicable outcomes.
- Preserved a strict no-selection, no-inference, no-network, and no-mutation
  boundary.
- Added ADR-169 and focused tests.

## M168 - Governed Provider Routing

- Added deterministic concrete provider route selection downstream from M167.
- Added local, remote, no-provider, withheld, and not-applicable routes.
- Added configurable Ollama, Gemini, Mistral, and future-provider preferences.
- Added deterministic preference, latency, and provider-name ordering.
- Added ordered fallback routes while preserving exact M167 lineage.
- Kept provider calls, inference, network access, and platform mutation forbidden.
- Added ADR-170 and 30 focused tests; complete suite now contains 4707 tests.

## M169 - Knowledge Source Policy

- Added deterministic knowledge-source policy downstream from M168.
- Added internal, local-document, official-documentation, web, news, and API
  source classes.
- Added internal-sufficient, local-source-preferred, external-required,
  verification-required, withheld, and not-applicable outcomes.
- Added internal-confidence, freshness, explicit external request, verification,
  local-document availability, sensitivity, and preferred-source governance.
- Preserved exact M168 route lineage.
- Kept retrieval, provider calls, network access, and platform mutation forbidden.
- Added ADR-171 and 30 focused tests.

## M170 - Knowledge Retrieval Orchestrator

- Added deterministic retrieval-plan orchestration downstream from M169.
- Added direct, sequential, and parallel strategies with ordered source steps.
- Added internal, local, external, verification, withheld, and not-applicable
  outcomes.
- Preserved exact M169 source-policy lineage.
- Kept document access, retrieval, provider calls, APIs, network access, and
  platform mutation forbidden.
- Added ADR-172 and focused tests.

## M171 - Knowledge Retrieval Execution Gateway

- Added the first governed execution boundary downstream from M170 retrieval
  planning.
- Added injected source-specific retrieval ports for internal, local-document,
  official-documentation, web, news, and API sources.
- Added completed, partial, failed, withheld, and not-applicable outcomes with
  deterministic per-step accounting.
- Added independent internal, local-document, and network permissions; network
  retrieval remains disabled by default.
- Added adapter failure containment, source/query lineage validation, content
  limits, sequential stop behavior, and logical parallel verification dispatch.
- Preserved exact M170 plan lineage and kept provider calls and platform mutation
  forbidden.
- Added ADR-173 and 28 focused tests; complete suite now contains 4789 passing
  tests.

## M172 - ROBY Console Application

- Added a governed console application boundary with injected terminal I/O.
- Connected the operational greeting path across M162 through M165.
- Added immutable console session and turn records with bounded loop behavior.
- Preserved unconnected routes as explicit pending outcomes without model calls.

## M173 - Local Provider Execution Adapter

- Added the first governed local inference execution boundary downstream from M168.
- Added injected local `LLMProvider` registration and deterministic route resolution.
- Added routed-model enforcement and provider/model response lineage validation.
- Added completed, rejected, failed, withheld, and not-applicable outcomes.
- Added prompt and response size governance plus provider exception containment.
- Kept remote fallback, external network authorization, and platform mutation forbidden.
- Added ADR-175 and 32 focused tests.

## M174 — External Retrieval Execution

- Added a governed external retrieval adapter for official documentation, web, news, and API sources.
- Implemented the M171 `KnowledgeRetriever` port with injected source-specific clients.
- Added strict source/query lineage, HTTPS reference, content-size, and reference-count validation.
- Preserved M171 as the explicit authority for network access.
- Added immutable audit records and contained external-client failures.

## M175 — Operational Response Assembly

- Added a side-effect-free operational response assembly boundary downstream from M171 and M173.
- Added immutable final response, evidence, limitation, lineage, and audit models.
- Preserved exact provider and retrieval execution lineage without re-executing either boundary.
- Added completed, partial, failed, withheld, and not-applicable outcomes.
- Added response and evidence limits plus explicit degraded-delivery semantics.
- Kept provider calls, retrieval, network authorization, fallback, and platform mutation outside M175.
- Added ADR-177 and 28 focused tests.

## M176 — Desktop Runtime Integration

- Added a governed desktop runtime boundary over M162, M172, and M175.
- Reused the M172 greeting path while preserving M163–M165 lineage.
- Added an injected operational pipeline for non-greeting desktop requests.
- Mapped deliverable, withheld, failed, blocked, and incomplete outcomes to the stable UI contract.
- Preserved provider and network execution flags as lineage only.
- Kept provider construction, retrieval, network authorization, response synthesis, and platform mutation outside M176.
- Added ADR-178 and 30 focused tests.

## M178 — Runtime Composition Root

- Added the single official constructor for ROBY's governed operational runtime graph.
- Wired M166-M177 through explicit turn-input ports with exact lineage.
- Added immutable, inspectable, idempotent runtime composition.
- Preserved local-first governance and side-effect-free construction.

## M179 — Local Runtime Bootstrap

- Added the official local lifecycle bootstrap over the M178 composition root.
- Added atomic lifecycle-state persistence with owner/session continuity checks.
- Added explicit environment-driven runtime-root factory loading.
- Added root `main.py` with controlled SIGINT/SIGTERM shutdown.
- Added 20 focused tests; full suite now contains 5011 passing tests.

## M180 — End-to-End Local Conversation

- Added the first real governed local conversation path over M179, M178, and M177.
- Added exact turn lineage and ordered owner/session-scoped JSONL persistence.
- Added session continuity across runtime restarts with private local journal permissions.
- Replaced the passive root process with a thin interactive local console.
- Kept memory, tools, formal tracing, observability, and platform mutation outside M180.
- Added 20 focused tests; full suite now contains 5031 passing tests.

## M181 — Operational Trace Model

- Added immutable per-turn operational trace events with deterministic identifiers.
- Added contiguous sequencing and explicit causal parent lineage validation.
- Integrated start, pipeline completion, and journal persistence events into M180.
- Preserved exact M180, M177, and M175 lineage plus governed execution flags.
- Added private local JSONL persistence and session/trace-scoped queries.
- Kept conversation text, observability UI, memory, tools, and new execution authority outside M181.
- Added 20 focused tests; full suite now contains 5051 passing tests.

## M182 — Development Console Observability

- Added immutable read-only runtime and per-turn observation projections.
- Added visibility into composed modules, activated trace modules, execution flags, terminal events, and exact lineage identifiers.
- Added `/status`, `/last`, `/trace [sequence]`, and `/help` development-console commands.
- Added optional post-turn observation rendering without changing conversational output.
- Kept prompts and responses out of technical views and preserved zero new execution authority.
- Added ADR-184 and 20 focused tests; full suite now contains 5071 passing tests.

## M183 — Memory Runtime Integration

- Connected the existing M36–M39 cognitive memory stack to the official operational runtime.
- Added governed recall before provider inference and learning evaluation after each completed pipeline turn.
- Added physically separate private SQLite stores per owner with non-identifying filenames and private permissions.
- Added optional shared-family recall, disabled by default, while keeping all M183 writes private to the current owner.
- Preserved side-effect-free composition and independent recall/learning controls.
- Added ADR-185 and 20 focused tests; full suite now contains 5091 passing tests.

## M184 — Tool Runtime Integration

- Connected the existing M61 tool gateway to the official operational runtime.
- Added explicit `/tool <capability> <json-object>` invocation with deterministic lineage.
- Reused capability registration, enablement, consent, handler isolation, and audit contracts.
- Added governed tool output as structured evidence for local provider inference.
- Blocked platform-mutating capabilities before dispatch to preserve M177 invariants.
- Contained unknown capabilities and handler failures without leaking handler error details.
- Preserved side-effect-free composition and kept autonomous tool selection outside M184.
- Added ADR-186 and 21 focused tests; full suite now contains 5112 passing tests.

## M185 — Long-Lived Runtime Lifecycle

- Added an exclusive private lease around the official M179 bootstrap.
- Added persistent heartbeats, stale detection, and process generation tracking.
- Added running, degraded, stopped, and failed lifecycle states with sanitized failures.
- Integrated graceful lifecycle ownership into the official `main.py` console path.
- Preserved one M178 composition and released the lease on normal or exceptional shutdown.
- Kept prompts, responses, memory, tool payloads, and provider output out of lifecycle metadata.
- Added ADR-187 and 20 focused tests; full suite now contains 5132 passing tests.

## M186 — Operational Runtime Consolidation

- Forward governed `/tool` commands through the official console path.
- Render the active owner in the local prompt.
- Add autonomous lifecycle heartbeat supervision without cognitive work.
- Recover only demonstrably stale leases from dead processes.
- Replace generic memory/tool dependency objects with explicit ports.
- Add reproducible delivery hygiene and 10 focused tests.

## M225.3 — Provider Payload Message Verification

- Added provider endpoint-path observation for governed local inference.
- Added exact ordered role-sequence observation for structured requests.
- Moved the explicit provider-message block to the end of `--observe` output.
- Added the unambiguous `provider_transport_verified` terminal marker.
- Preserved prompt fallback visibility and redaction outside explicit observation.

## M228.5 — Gmail Client Secrets Governed Fallback

- Added a governed local `credentials.json` fallback with environment precedence.
- Added focused compatibility and diagnostic tests.

## RP.19.8 — Cognitive Agenda Manager operativo

- Consolidated RP.19.1–RP.19.7 under the canonical cognitive agenda manager.
- Added observable operational health and invariant validation.
- Added safe in-memory degradation for repository read/write failures.
- Added six operational closure tests and final RP.19 documentation.
