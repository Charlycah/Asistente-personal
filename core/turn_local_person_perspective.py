from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256


class PersonPerspectiveEvidenceStatus(str, Enum):
    THIRD_PERSON_EXPLICIT = "third_person_explicit"
    MIXED_PERSPECTIVE = "mixed_perspective"
    FIRST_PERSON_ONLY = "first_person_only"
    IDENTITY_CLAIM = "identity_claim"
    AMBIGUOUS = "ambiguous"
    NO_SIGNAL = "no_signal"


@dataclass(frozen=True)
class TurnLocalPersonPerspectiveEvidence:
    status: PersonPerspectiveEvidenceStatus
    third_person_mentions: tuple[str, ...]
    first_person_present: bool
    explicit_identity_claim: bool
    relationship_explicit: bool
    ambiguous_reference: bool
    evidence_codes: tuple[str, ...]
    source_fingerprint: str
    read_only: bool = True
    transient: bool = True
    persists_results: bool = False
    creates_person: bool = False
    creates_relationship: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    modifies_identity: bool = False
    modifies_profile: bool = False
    modifies_world_model: bool = False
    modifies_grounding_state: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    @property
    def supports_referential_grounding(self) -> bool:
        return self.status in {
            PersonPerspectiveEvidenceStatus.THIRD_PERSON_EXPLICIT,
            PersonPerspectiveEvidenceStatus.MIXED_PERSPECTIVE,
        }


class TurnLocalPersonPerspectiveEvidenceProducer:
    """Extract bounded current-turn person-perspective evidence only."""

    _IDENTITY_RE = re.compile(
        r"^\s*(?:yo\s+)?(?:soy|me\s+llamo|mi\s+nombre\s+es)\s+"
        r"[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúÑñ'-]*\b",
        re.IGNORECASE,
    )
    _FIRST_PERSON_RE = re.compile(
        r"\b(?:yo|me|mí|mi|mis|conmigo|nos|nosotros|nosotras)\b",
        re.IGNORECASE,
    )
    _AMBIGUOUS_PRONOUN_RE = re.compile(
        r"\b(?:él|ella|ellos|ellas)\b",
        re.IGNORECASE,
    )
    _NAME = r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:[-'][A-ZÁÉÍÓÚÑ]?[a-záéíóúñ]+)?"
    _HUMAN_PREDICATE = (
        r"(?:compr(?:ó|a|aron)|llam(?:ó|a|aron)|dij(?:o|eron)|tom(?:ó|a|aron)|"
        r"sali(?:ó|eron)|est(?:á|aba|uvo|án|aban)|fue|eran?|tien(?:e|en)|"
        r"llev(?:ó|a|aron)|perdi(?:ó|eron)|viaj(?:ó|a|aron)|viv(?:e|en|ió)|"
        r"trabaj(?:a|an|ó)|estudi(?:a|an|ó)|lleg(?:ó|a|aron)|volvi(?:ó|eron)|"
        r"naci(?:ó|eron)|quier(?:e|en)|piens(?:a|an)|sab(?:e|en)|hiz(?:o|ieron))"
    )
    _THIRD_PERSON_SUBJECT_RE = re.compile(
        rf"^\s*(?P<name>{_NAME})\s+"
        rf"(?:(?:me|te|lo|la|le|nos|los|las|les|se)\s+)?"
        rf"{_HUMAN_PREDICATE}\b",
    )
    _COORDINATED_NAME_RE = re.compile(rf"\s+y\s+(?P<name>{_NAME})\b")
    _EXPLICIT_RELATION_RE = re.compile(
        rf"^\s*(?P<name>{_NAME})\s+(?:es|era)\s+mi\s+\w+\b",
        re.IGNORECASE,
    )

    def analyze(self, text: str) -> TurnLocalPersonPerspectiveEvidence:
        source = text if isinstance(text, str) else str(text)
        clean = " ".join(source.strip().split())
        fingerprint = sha256(clean.encode("utf-8")).hexdigest()
        if not clean:
            return self._evidence(
                status=PersonPerspectiveEvidenceStatus.NO_SIGNAL,
                fingerprint=fingerprint,
                evidence_codes=("blank_or_empty_turn",),
            )

        if self._IDENTITY_RE.search(clean):
            return self._evidence(
                status=PersonPerspectiveEvidenceStatus.IDENTITY_CLAIM,
                fingerprint=fingerprint,
                first_person_present=True,
                explicit_identity_claim=True,
                evidence_codes=("explicit_interlocutor_identity_claim",),
            )

        relationship_match = self._EXPLICIT_RELATION_RE.search(clean)
        subject_match = self._THIRD_PERSON_SUBJECT_RE.search(clean)
        first_person = bool(self._FIRST_PERSON_RE.search(clean))
        if subject_match is None and relationship_match is not None:
            mentions = (relationship_match.group("name"),)
            return self._evidence(
                status=PersonPerspectiveEvidenceStatus.MIXED_PERSPECTIVE,
                fingerprint=fingerprint,
                third_person_mentions=mentions,
                first_person_present=True,
                relationship_explicit=True,
                evidence_codes=(
                    "explicit_third_person_attribution",
                    "interlocutor_and_third_person_perspectives_coexist",
                    "relationship_explicit_in_current_turn",
                ),
            )
        if subject_match is None:
            return self._evidence(
                status=(
                    PersonPerspectiveEvidenceStatus.FIRST_PERSON_ONLY
                    if first_person
                    else PersonPerspectiveEvidenceStatus.NO_SIGNAL
                ),
                fingerprint=fingerprint,
                first_person_present=first_person,
                evidence_codes=(
                    "first_person_without_third_person_attribution"
                    if first_person
                    else "no_high_confidence_person_perspective_signal",
                ),
            )

        mentions = [subject_match.group("name")]
        mentions.extend(
            match.group("name") for match in self._COORDINATED_NAME_RE.finditer(clean)
        )
        mentions = list(dict.fromkeys(mentions))
        ambiguous = bool(self._AMBIGUOUS_PRONOUN_RE.search(clean))
        relationship_explicit = bool(self._EXPLICIT_RELATION_RE.search(clean))
        if ambiguous:
            return self._evidence(
                status=PersonPerspectiveEvidenceStatus.AMBIGUOUS,
                fingerprint=fingerprint,
                third_person_mentions=tuple(mentions),
                first_person_present=first_person,
                relationship_explicit=relationship_explicit,
                ambiguous_reference=True,
                evidence_codes=("ambiguous_third_person_pronoun_reference",),
            )

        status = (
            PersonPerspectiveEvidenceStatus.MIXED_PERSPECTIVE
            if first_person
            else PersonPerspectiveEvidenceStatus.THIRD_PERSON_EXPLICIT
        )
        codes = ["explicit_third_person_attribution"]
        if first_person:
            codes.append("interlocutor_and_third_person_perspectives_coexist")
        if relationship_explicit:
            codes.append("relationship_explicit_in_current_turn")
        else:
            codes.append("no_relationship_to_interlocutor_established")
        return self._evidence(
            status=status,
            fingerprint=fingerprint,
            third_person_mentions=tuple(mentions),
            first_person_present=first_person,
            relationship_explicit=relationship_explicit,
            evidence_codes=tuple(codes),
        )

    @staticmethod
    def _evidence(
        *,
        status: PersonPerspectiveEvidenceStatus,
        fingerprint: str,
        third_person_mentions: tuple[str, ...] = (),
        first_person_present: bool = False,
        explicit_identity_claim: bool = False,
        relationship_explicit: bool = False,
        ambiguous_reference: bool = False,
        evidence_codes: tuple[str, ...],
    ) -> TurnLocalPersonPerspectiveEvidence:
        return TurnLocalPersonPerspectiveEvidence(
            status=status,
            third_person_mentions=third_person_mentions,
            first_person_present=first_person_present,
            explicit_identity_claim=explicit_identity_claim,
            relationship_explicit=relationship_explicit,
            ambiguous_reference=ambiguous_reference,
            evidence_codes=evidence_codes,
            source_fingerprint=fingerprint,
        )
