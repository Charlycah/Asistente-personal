# RP.10 — Continuous Internal Cognitive Loop

RP.10 adds a lightweight resident loop that continuously maintains ROBY's current
cognitive focus without invoking an LLM or producing unsolicited speech.

The loop fuses recent conversational self-analysis, ambient activity and open
commitment counts into one current state: idle, conversation repair, ambient
awareness or open commitments. It is lifecycle-managed by the official desktop
runtime and configured through the local environment.
