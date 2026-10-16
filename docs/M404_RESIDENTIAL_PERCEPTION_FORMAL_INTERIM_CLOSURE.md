# ROBY XI.2 — M404 Residential Perception Formal Interim Closure

**Closure baseline:** M404.2 — Local Camera Governed Acquisition Integration  
**Official validation:** M361 synchronized · Ruff clean · **11,142 tests passed** · 0 regressions  
**Closure type:** formal interim closure — architectural + minimal operational  
**Physical household deployment:** deferred certification dependency

## 1. Formal decision

**M404 — Residential Perception is CLOSED architecturally and CLOSED for the minimal local operational route demonstrated by M404.2.**

This closure does **not** claim that a residential sensor, IP camera or distributed household source has been physically deployed. Those items remain physical/source-specific certification work and are not architectural debt.

No M404.3 is authorized by milestone continuity alone.

## 2. Closed chain

### M404.1 — Residential Perception Foundation

Established the minimal read-only boundary for physical perception:

- canonical `ResidenceId` reuse from M396;
- canonical `resource_id` reuse from External Resource Registry;
- immutable `ResidentialPhysicalSourceBinding`;
- immutable `ResidentialPhysicalObservation`;
- source capability/provenance;
- fail-closed `GovernedResidentialPerceptionAdmission`;
- no source registry, device control, persistence, streaming or new visual authority.

### M404.2 — Local Camera Governed Acquisition Integration

Demonstrated one real physical one-shot acquisition through the already-existing camera path:

`CameraAdapter → one capture → safe frame metadata → ResidentialPhysicalObservation → M404 admission`

It preserves:

- existing camera ownership;
- neutral `domain.vision.CameraFrame`;
- `resource_id != camera_index`;
- `frame_id → acquisition_reference`;
- `captured_at → observed_at`;
- raw image bytes outside M404 observation payload;
- acquisition failure distinct from admission rejection.

## 3. Ownership preserved

- **M396** owns residence identity/admission/capabilities.
- **External Resource Registry** owns external resource identity, registration and authorization facts.
- **M404** owns source-to-residence perceptual binding, physical observation representation and admission only.
- **Vision Core** remains visual interpretation authority.
- **M403** remains cross-residence synchronization authority for representations when a real remote source requires it.
- Physical adapters remain subordinate acquisition mechanisms.

M404 never becomes memory, knowledge, interpretation, synchronization or device-action authority.

## 4. Permanent M404 invariants

- physical observation != cognitive truth;
- acquisition != interpretation;
- interpretation != knowledge;
- knowledge != memory;
- perception != action authorization;
- `ResidenceId` and `resource_id` remain distinct canonical identities;
- source authorization does not imply capability or truth;
- provenance is mandatory;
- admission is fail-closed;
- read-only means no device mutation;
- no implicit recording;
- no implicit persistence;
- no implicit memory/knowledge creation;
- no implicit M403 synchronization;
- cross-residence observations must reuse M403 instead of inventing another transport;
- image observation metadata and media artifacts remain distinct;
- no second Vision Core or source registry.

## 5. Completion levels

### Architectural

**CLOSED.**

Contracts, ownership, admission semantics, identity boundaries and invariants are defined and validated.

### Minimal operational

**CLOSED.**

A real local one-shot camera capture reaches the M404 observation/admission boundary through productive code.

### Residential distributed physical

**PENDING PHYSICAL CERTIFICATION.**

Still requires a real household source physically associated with a Residential Node and, when cross-residence, an end-to-end M404 → M403 → Primary Home run.

### Experience

**PARTIAL / PENDING PHYSICAL HOUSEHOLD DEPLOYMENT.**

The local camera path is usable under its existing conditions; household sensors/IP cameras remain dependent on concrete hardware and configuration.

## 6. Explicit deferred certifications

### Residential Sensor Physical Certification

Future evidence should demonstrate:

`real household sensor → source-specific read_once → M404 admission → M403 → Primary Home`

A concrete source must exist first. No generic sensor platform is authorized in advance.

### Residential IP Camera Physical Certification

Future evidence should demonstrate a real governed IP-camera source. Visual transport/interpretation will require a separate governed media/reference decision so that the same acquisition artifact can be consumed without recapture or implicit persistence.

## 7. Explicit NO-GO after interim closure

Do not open M404.3 merely to add:

- generic sensor framework;
- MQTT/Home Assistant platform;
- SensorManager/polling daemon;
- generic IP-camera abstraction without a real device;
- media repository/archive;
- automatic M403 synchronization;
- automatic Vision inference;
- memory/knowledge insertion;
- device actuation.

A future physical source may authorize a small source-specific integration/certification branch, not a redesign of M404 Foundation.

## 8. Master-plan impact

The recovered physical/distributed trunk is now:

`Distributed Residence → Connectivity → Physical Transport → Residential Node → Governed Synchronization → Residential Perception`

All six steps are architecturally closed. Residential Node and Residential Perception retain separate physical deployment/certification dependencies.

This means the project should return to the current Master State before opening another architectural milestone. Missing hardware is not a reason to generate speculative software.

## 9. Final checkpoint decision

**M404 Formal Interim Closure: APPROVED.**  
**M404.3 by continuity: NO-GO.**  
**Architectural blocker: NONE.**  
**External physical dependency: YES.**
