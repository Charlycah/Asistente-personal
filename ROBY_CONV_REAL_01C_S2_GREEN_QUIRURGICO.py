"""CONV-REAL-01C-S2: guarded, single-file GREEN; preview by default.

Run from HAL root. --apply requires exact reference baseline match.
No new module, authority, or provider changes.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path

TARGET = Path("core/conversational_context_continuity.py")
BASELINE_SHA256 = "75b2b6794f36f5de18494be0046756902067047ae840381b764e7252f25994c2"


def transform(source: str) -> str:
    before_import = (
        "from core.conversation_context_curation import (\n"
        "    curate_recent_conversation_context,\n"
        ")\n"
    )
    after_import = (
        "from core.conversation_context_curation import (\n"
        "    curate_recent_conversation_context,\n"
        "    normalize_conversational_text,\n"
        ")\n"
    )
    before_sanitized = (
        "    sanitized = sanitize_conversation_history(conversation.recent_context)\n"
        "    curated_context = curate_recent_conversation_context(\n"
    )
    after_sanitized = (
        "    sanitized = sanitize_conversation_history(conversation.recent_context)\n"
        "    normalized_current = normalize_conversational_text(conversation.text)\n"
        "    repeat_count = sum(\n"
        "        1\n"
        "        for turn in sanitized.context\n"
        "        if normalized_current\n"
        "        and normalize_conversational_text(turn.user_text)\n"
        "        == normalized_current\n"
        "    )\n"
        "    curated_context = curate_recent_conversation_context(\n"
    )
    before_messages = (
        "    messages: list[ConversationMessage] = []\n"
        "    if inference_request.system_prompt:\n"
        '        messages.append(ConversationMessage("system", '
        "inference_request.system_prompt))\n"
    )
    after_messages = (
        "    messages: list[ConversationMessage] = []\n"
        "    if inference_request.system_prompt:\n"
        '        messages.append(ConversationMessage("system", '
        "inference_request.system_prompt))\n"
        "    if repeat_count:\n"
        "        messages.append(\n"
        "            ConversationMessage(\n"
        '                "system",\n'
        '                "Contexto de esta sesión: el usuario ya formuló una "\n'
        '                "pregunta equivalente. La respuesta anterior se excluyó "\n'
        '                "por curación. No presupongas que fue correcta, que "\n'
        '                "hubo insatisfacción ni que se completó una respuesta.",\n'
        "            )\n"
        "        )\n"
    )
    before_metadata = (
        "    metadata = dict(inference_request.metadata)\n"
        "    if conversation.recent_context:\n"
    )
    after_metadata = (
        "    metadata = dict(inference_request.metadata)\n"
        "    if repeat_count:\n"
        '        metadata["conversation_current_question_repeated"] = "true"\n'
        '        metadata["conversation_current_question_repeat_count"] = str(\n'
        "            repeat_count\n"
        "        )\n"
        "    if conversation.recent_context:\n"
    )
    output = source
    for old, new in (
        (before_import, after_import),
        (before_sanitized, after_sanitized),
        (before_messages, after_messages),
        (before_metadata, after_metadata),
    ):
        if output.count(old) != 1:
            raise SystemExit("STOP: expected integration anchor missing or duplicated")
        output = output.replace(old, new, 1)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not TARGET.is_file():
        raise SystemExit(f"STOP: missing {TARGET}; run from HAL root")
    raw = TARGET.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != BASELINE_SHA256:
        raise SystemExit(
            "STOP: local source differs from inspected ZIP baseline; "
            f"no changes applied. SHA256={digest}"
        )
    source = raw.decode("utf-8")
    output = transform(source)
    compile(output, str(TARGET), "exec")
    diff = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            output.splitlines(keepends=True),
            fromfile=str(TARGET),
            tofile=str(TARGET) + " (candidate)",
        )
    )
    print(diff)
    if not args.apply:
        print("PREVIEW ONLY: no files changed. Run --apply after reviewing diff.")
        return
    TARGET.write_bytes(output.encode("utf-8"))
    print("APPLIED: one production file. Run focal tests and Ruff.")


if __name__ == "__main__":
    main()
