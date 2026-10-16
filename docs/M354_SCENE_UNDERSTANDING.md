# M354 — Scene Understanding gobernado

M354 introduces a descriptive scene-fusion capability over the official Vision
Core. It captures **one authorized frame** and sends that same transient frame
to the configured local person, face, object, OCR and visual-code analyzers.

The deterministic scene analyzer combines only observable outputs:

- person and face counts;
- object labels;
- OCR-region count;
- QR/barcode types;
- aggregate confidence and analyzer provenance.

The result contains no image bytes. Raw media is discarded after transient
processing, and the snapshot retains only counters and the last safe summary.

M354 does not infer activities, identity, intent, emotion, age, gender,
ownership or semantic document meaning. It performs no web request and no
automatic action. Missing analyzers are permitted, but at least one governed
visual analyzer must be configured.

Every scene request requires camera permission, explicit consent, an explicit
user request and the `scene_description` capability.
