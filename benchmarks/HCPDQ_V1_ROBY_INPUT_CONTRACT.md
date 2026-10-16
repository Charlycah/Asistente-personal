# HCPDQ-v1 ROBY Input Contract

The evaluated cognitive path may receive only the subject payload:
`case_id`, `family`, `difficulty`, and `prompt`.

It must never receive `ground_truth_reference`, scoring mode, expected outcome, answer key, rubric, human response, aggregate score, or previous-case feedback.

The benchmark remains read-only: no Memory/Learning writes, threshold adaptation, authority changes, self-improvement application, or benchmark-driven persistence are authorized.
