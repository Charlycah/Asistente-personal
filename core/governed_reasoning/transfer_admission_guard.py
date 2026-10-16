from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_rule_admission import (
    GovernedTemporaryConcreteRuleAdmission,
    GovernedTemporaryConcreteRuleAdmissionBoundary,
)
from core.governed_reasoning.inference import InMemoryInferenceRuleRegistry
from core.governed_reasoning.transfer_instantiation import (
    GovernedTransferInstantiationPackage,
    TransferInstantiationStatus,
)
from core.scope_guard import ScopeDomain

_SCHEMA_VERSION = "rc-1.4-governed-transfer-admission-guard-v1"


class TransferAdmissionGuardStatus(StrEnum):
    ADMITTED_FOR_REVIEW = "admitted_for_review"
    NOT_TRANSFER_INSTANTIATED = "not_transfer_instantiated"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class GovernedTransferAdmission:
    status: TransferAdmissionGuardStatus | str
    scope_reference: str
    transfer_package_fingerprint: str
    source_memory_id: int
    source_memory_content_fingerprint: str
    source_grounding_fingerprint: str
    source_compilation_fingerprint: str
    transfer_candidate_fingerprint: str
    target_projection_fingerprint: str
    instantiated_candidate_fingerprint: str
    canonical_admission: GovernedTemporaryConcreteRuleAdmission | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    session_local: bool = True
    persistent: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    establishes_truth: bool = False
    authorizes_inference: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        status = TransferAdmissionGuardStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("transfer admission must preserve reasoning authority")
        if not self.scope_reference.strip() or self.source_memory_id <= 0:
            raise ValueError("transfer admission requires scope and source memory")
        fingerprints = (
            self.transfer_package_fingerprint,
            self.source_memory_content_fingerprint,
            self.source_grounding_fingerprint,
            self.source_compilation_fingerprint,
            self.transfer_candidate_fingerprint,
            self.target_projection_fingerprint,
            self.instantiated_candidate_fingerprint,
            self.source_fingerprint,
        )
        if any(len(item) != 64 for item in fingerprints):
            raise ValueError("transfer admission requires SHA-256 provenance")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("transfer admission requires rationale codes")
        if any(
            (
                not self.session_local,
                self.persistent,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.establishes_truth,
                self.authorizes_inference,
                self.executes_actions,
                self.grants_authority,
                self.uses_provider,
                self.uses_retrieval,
            )
        ):
            raise ValueError("transfer admission violates governed limits")
        if status is TransferAdmissionGuardStatus.ADMITTED_FOR_REVIEW:
            if self.canonical_admission is None:
                raise ValueError("admitted transfer requires canonical admission")
            if not self.canonical_admission.rule.requires_review:
                raise ValueError("transferred rule must require review")
            if not self.canonical_admission.rule.temporary:
                raise ValueError("transferred rule must remain temporary")
        elif self.canonical_admission is not None:
            raise ValueError("failed transfer admission cannot expose admission")

    @property
    def normalized_status(self) -> TransferAdmissionGuardStatus:
        return TransferAdmissionGuardStatus(self.status)


class GovernedTransferAdmissionGuard:
    """Guard transferred-rule eligibility before canonical temporary admission."""

    def __init__(self) -> None:
        self._admission = GovernedTemporaryConcreteRuleAdmissionBoundary()

    def admit(
        self,
        *,
        package: GovernedTransferInstantiationPackage,
        registry: InMemoryInferenceRuleRegistry,
        scope_reference: str,
        allowed_domains: tuple[ScopeDomain | str, ...],
        admitted_at: datetime,
        expires_at: datetime,
    ) -> GovernedTransferAdmission:
        if not scope_reference.strip():
            raise ValueError("transfer admission guard requires scope")

        if (
            package.normalized_status
            is not TransferInstantiationStatus.TRANSFER_INSTANTIATED
        ):
            return self._result(
                status=TransferAdmissionGuardStatus.NOT_TRANSFER_INSTANTIATED,
                package=package,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_admission:package_not_transfer_instantiated",
                    "transfer_admission:registry_unchanged",
                ),
            )

        if package.scope_reference != scope_reference:
            return self._result(
                status=TransferAdmissionGuardStatus.SCOPE_MISMATCH,
                package=package,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_admission:scope_mismatch",
                    "transfer_admission:registry_unchanged",
                ),
            )

        candidate = package.instantiated_candidate
        if candidate is None:
            return self._result(
                status=TransferAdmissionGuardStatus.UNSUPPORTED,
                package=package,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_admission:instantiated_candidate_missing",
                    "transfer_admission:registry_unchanged",
                ),
            )

        if not self._package_integrity_valid(package):
            return self._result(
                status=TransferAdmissionGuardStatus.PROVENANCE_MISMATCH,
                package=package,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_admission:package_provenance_mismatch",
                    "transfer_admission:registry_unchanged",
                ),
            )

        canonical = self._admission.admit(
            candidate=candidate,
            registry=registry,
            scope_reference=scope_reference,
            allowed_domains=allowed_domains,
            admitted_at=admitted_at,
            expires_at=expires_at,
        )
        if not canonical.rule.requires_review or not canonical.rule.temporary:
            raise ValueError("canonical admission weakened transfer review limits")

        return self._result(
            status=TransferAdmissionGuardStatus.ADMITTED_FOR_REVIEW,
            package=package,
            scope_reference=scope_reference,
            canonical_admission=canonical,
            rationale_codes=(
                "transfer_admission:transfer_lineage_verified",
                "transfer_admission:canonical_boundary_reused",
                "transfer_admission:temporary_review_required",
            ),
        )

    @staticmethod
    def _package_integrity_valid(
        package: GovernedTransferInstantiationPackage,
    ) -> bool:
        candidate = package.instantiated_candidate
        if candidate is None:
            return False
        fingerprints = (
            package.source_memory_content_fingerprint,
            package.source_grounding_fingerprint,
            package.source_compilation_fingerprint,
            package.transfer_candidate_fingerprint,
            package.target_projection_fingerprint,
            candidate.source_fingerprint,
            package.source_fingerprint,
        )
        if any(len(item) != 64 for item in fingerprints):
            return False
        payload = repr(
            (
                "rc-1.3-governed-transfer-instantiation-package-v1",
                package.normalized_status.value,
                package.scope_reference,
                package.source_memory_id,
                package.source_memory_content_fingerprint,
                package.source_grounding_fingerprint,
                package.source_compilation_fingerprint,
                package.transfer_candidate_fingerprint,
                package.target_projection_fingerprint,
                package.bindings,
                candidate.source_fingerprint,
                package.rationale_codes,
            )
        )
        expected = sha256(payload.encode("utf-8")).hexdigest()
        return expected == package.source_fingerprint

    @staticmethod
    def _result(
        *,
        status: TransferAdmissionGuardStatus,
        package: GovernedTransferInstantiationPackage,
        scope_reference: str,
        rationale_codes: tuple[str, ...],
        canonical_admission: GovernedTemporaryConcreteRuleAdmission | None = None,
    ) -> GovernedTransferAdmission:
        candidate = package.instantiated_candidate
        candidate_fingerprint = (
            candidate.source_fingerprint
            if candidate is not None and len(candidate.source_fingerprint) == 64
            else "0" * 64
        )
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                scope_reference,
                package.source_fingerprint,
                package.source_memory_id,
                package.source_memory_content_fingerprint,
                package.source_grounding_fingerprint,
                package.source_compilation_fingerprint,
                package.transfer_candidate_fingerprint,
                package.target_projection_fingerprint,
                candidate_fingerprint,
                (
                    canonical_admission.rule.fingerprint
                    if canonical_admission is not None
                    else None
                ),
                rationale_codes,
            )
        )
        return GovernedTransferAdmission(
            status=status,
            scope_reference=scope_reference,
            transfer_package_fingerprint=package.source_fingerprint,
            source_memory_id=package.source_memory_id,
            source_memory_content_fingerprint=package.source_memory_content_fingerprint,
            source_grounding_fingerprint=package.source_grounding_fingerprint,
            source_compilation_fingerprint=package.source_compilation_fingerprint,
            transfer_candidate_fingerprint=package.transfer_candidate_fingerprint,
            target_projection_fingerprint=package.target_projection_fingerprint,
            instantiated_candidate_fingerprint=candidate_fingerprint,
            canonical_admission=canonical_admission,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
