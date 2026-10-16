# ADR-136 — Ambient Context Foundation

## Status
Accepted.

## Context
ROBY now exposes stable terminal contracts for Mobile, Driving, Maps and Visual Understanding. Ambient Context must become a transversal domain capable of receiving governed observations from devices, homes, vehicles, wearables and future services without becoming a sensor adapter or prematurely interpreting presence, activity, sound, environmental conditions or space.

## Decision
Create M134 as a provider-neutral foundation that converts one declarative `AmbientObservationSignal` into an immutable `AmbientContext`.

The foundation governs:
- ownership;
- explicit consent;
- source and scope;
- privacy;
- confidence and freshness;
- external provenance;
- stable deterministic identity.

A ready context only declares that an ambient observation exists and requires future resolution. It cannot authorize presence inference, activity inference, acoustic analysis, environmental-condition analysis, spatial inference or automation.

## Consequences
Ambient Context remains reusable across home, work, vehicle, outdoor and public settings. Future milestones can resolve and interpret ambient evidence without coupling the domain to sensors, providers, platform automation or existing contextual domains.
