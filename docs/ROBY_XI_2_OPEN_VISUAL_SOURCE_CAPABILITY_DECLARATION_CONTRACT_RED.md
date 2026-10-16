# ROBY XI.2 — Open Visual Source Capability Declaration — Contract RED

## Status
CONTRACT RED complete / pending Owner certification.

## Authorized seam
Only `OPEN_VISUAL_SOURCE_CAPABILITY_DECLARATION`.

## RED obligations
1. `GovernedInformationSource` exposes an explicit semantic capability set.
2. The capability vocabulary includes `OPEN_VISUAL_SUBJECT_QUERY`.
3. Legacy/current source declarations default to an empty capability set.
4. NASA remains without `OPEN_VISUAL_SUBJECT_QUERY`.
5. An open-visual request with no capable source remains typed `UNAVAILABLE`.
6. A synthetic test-only source explicitly declaring the capability becomes
   eligible through the existing canonical selector.
7. `GovernedSourceQueryContract.prepare()` rejects open-visual queries against
   non-capable sources and accepts an explicitly capable synthetic source.
8. Empty topics, query text, adapter registration, media type, or technical
   query support never substitute for the capability declaration.
9. No productive provider, adapter, registry, selector, executor, freshness
   ordering, or presentation behavior is added.

The synthetic source is a contractual fixture only. It is not a productive
general image provider.

Expected RED root: capability vocabulary/metadata and enforcement are absent.
