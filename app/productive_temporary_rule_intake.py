from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning import (
    ContextualCaseClaimProjectionStatus,
    ContextualCaseGroundingStatus,
    ContextualRuleGroundingCompilationStatus,
    ContextualRuleInstantiationStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualCaseClaimProjection,
    GovernedContextualCaseClaimProjector,
    GovernedContextualCaseRoleGrounder,
    GovernedContextualRuleGroundingCompilation,
    GovernedContextualRuleGroundingCompiler,
    GovernedContextualRuleInstantiator,
    GovernedContextualSemanticGroundingCandidate,
    GovernedTemporaryConcreteRuleAdmission,
    GovernedTemporaryConcreteRuleAdmissionBoundary,
    InMemoryInferenceRuleRegistry,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.scope_guard import ScopeDomain


class ProductiveTemporaryRuleIntakeStatus(StrEnum):
    NO_CHANGE = "no_change"
    SPEC_STORED = "spec_stored"
    RULE_ADMITTED = "rule_admitted"
    CASE_INSUFFICIENT = "case_insufficient"
    CASE_AMBIGUOUS = "case_ambiguous"
    CASE_UNSUPPORTED = "case_unsupported"


@dataclass(frozen=True)
class SessionLocalCompiledRuleSpec:
    scope_reference: str
    source_reference: str
    compilation: GovernedContextualRuleGroundingCompilation
    stored_at: datetime
    expires_at: datetime

    @property
    def spec(self):
        return self.compilation.instantiation_spec


@dataclass(frozen=True)
class ProductiveTemporaryRuleIntakeResult:
    status: ProductiveTemporaryRuleIntakeStatus
    scope_reference: str
    source_reference: str
    pending_specs: int
    projection: GovernedContextualCaseClaimProjection | None = None
    admission: GovernedTemporaryConcreteRuleAdmission | None = None
    projections: tuple[GovernedContextualCaseClaimProjection, ...] = ()
    admissions: tuple[GovernedTemporaryConcreteRuleAdmission, ...] = ()
    semantic_grounding: GovernedContextualSemanticGroundingCandidate | None = None
    canonical_authority: str = "governed_reasoning"
    session_local: bool = True
    persistent: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    grants_authority: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive rule intake must preserve reasoning authority")
        if not self.scope_reference.strip() or not self.source_reference.strip():
            raise ValueError("productive rule intake requires scope and provenance")
        if len(self.projections) > 2 or len(self.admissions) > 2:
            raise ValueError("productive rule intake v1 admits at most two rules")
        if self.admissions and len(self.projections) != len(self.admissions):
            raise ValueError("productive rule intake aggregate results must align")
        if self.projection is not None and self.projections:
            if self.projection != self.projections[-1]:
                raise ValueError(
                    "primary projection must match final aggregate projection"
                )
        if self.admission is not None and self.admissions:
            if self.admission != self.admissions[-1]:
                raise ValueError(
                    "primary admission must match final aggregate admission"
                )
        if any(
            (
                not self.session_local,
                self.persistent,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.grants_authority,
                self.executes_actions,
            )
        ):
            raise ValueError("productive rule intake violates governed limits")


class ProductiveTemporaryRuleIntake:
    """Compose certified RF-E rule contracts on the canonical reasoning registry."""

    _MAX_PENDING_PER_SESSION = 4
    _MAX_ADMISSIONS_PER_OBSERVATION = 2
    _LIFETIME = timedelta(minutes=30)

    def __init__(self, registry: InMemoryInferenceRuleRegistry) -> None:
        self._registry = registry
        self._pending: dict[str, list[SessionLocalCompiledRuleSpec]] = {}
        self._interpreter = GovernedContextualRuleInterpretationProducer()
        self._semantic_grounder = GovernedBoundedSemanticRoleRelationGrounder()
        self._compiler = GovernedContextualRuleGroundingCompiler()
        self._case_grounder = GovernedContextualCaseRoleGrounder()
        self._projector = GovernedContextualCaseClaimProjector()
        self._instantiator = GovernedContextualRuleInstantiator()
        self._admission = GovernedTemporaryConcreteRuleAdmissionBoundary()
        self._last_result: ProductiveTemporaryRuleIntakeResult | None = None

    @property
    def last_result(self) -> ProductiveTemporaryRuleIntakeResult | None:
        return self._last_result

    def pending_count(self, scope_reference: str) -> int:
        return len(self._pending.get(scope_reference, ()))

    def observe(
        self,
        *,
        owner: str,
        text: str,
        scope_reference: str,
        domains: tuple[ScopeDomain | str, ...],
        now: datetime,
    ) -> ProductiveTemporaryRuleIntakeResult:
        if not owner.strip() or not text.strip() or not scope_reference.strip():
            raise ValueError("productive rule intake requires owner, text, and scope")
        if now.tzinfo is None:
            raise ValueError("productive rule intake timestamp must be timezone-aware")
        self._prune(now)
        source_reference = self._source_reference(scope_reference, text)

        candidate = self._interpreter.produce(
            text,
            source_reference=source_reference,
            scope_reference=scope_reference,
        )
        semantic = self._semantic_grounder.ground(
            candidate,
            scope_reference=scope_reference,
        )
        compilation = self._compiler.compile(
            rule_candidate=candidate,
            semantic_grounding=semantic,
            scope_reference=scope_reference,
        )
        if (
            compilation.normalized_status
            is ContextualRuleGroundingCompilationStatus.COMPILED
            and compilation.instantiation_spec is not None
        ):
            self._store(
                SessionLocalCompiledRuleSpec(
                    scope_reference=scope_reference,
                    source_reference=source_reference,
                    compilation=compilation,
                    stored_at=now,
                    expires_at=now + self._LIFETIME,
                )
            )
            return self._remember(
                ProductiveTemporaryRuleIntakeStatus.SPEC_STORED,
                scope_reference,
                source_reference,
                semantic_grounding=semantic,
            )

        pending = tuple(self._pending.get(scope_reference, ()))
        if not pending:
            return self._remember(
                ProductiveTemporaryRuleIntakeStatus.NO_CHANGE,
                scope_reference,
                source_reference,
                semantic_grounding=semantic,
            )

        fallback = ProductiveTemporaryRuleIntakeStatus.CASE_INSUFFICIENT
        projections: list[GovernedContextualCaseClaimProjection] = []
        admissions: list[GovernedTemporaryConcreteRuleAdmission] = []
        admitted_stored: list[SessionLocalCompiledRuleSpec] = []
        for stored in reversed(pending):
            if len(admissions) >= self._MAX_ADMISSIONS_PER_OBSERVATION:
                break
            spec = stored.spec
            if spec is None:
                continue
            case = self._case_grounder.ground(
                case_text=text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
            )
            if case.normalized_status is ContextualCaseGroundingStatus.AMBIGUOUS:
                fallback = ProductiveTemporaryRuleIntakeStatus.CASE_AMBIGUOUS
                continue
            if case.normalized_status is ContextualCaseGroundingStatus.UNSUPPORTED:
                fallback = ProductiveTemporaryRuleIntakeStatus.CASE_UNSUPPORTED
                continue
            if case.normalized_status is not ContextualCaseGroundingStatus.GROUNDED:
                continue

            projection = self._projector.project(
                spec=spec,
                case_grounding=case,
                scope_reference=scope_reference,
                owner=owner,
                created_at=now,
            )
            if (
                projection.normalized_status
                is not ContextualCaseClaimProjectionStatus.PROJECTED
            ):
                continue
            instantiated = self._instantiator.instantiate(
                spec=spec,
                bindings=case.bindings,
                scope_reference=scope_reference,
            )
            if (
                instantiated.status
                is not ContextualRuleInstantiationStatus.INSTANTIATED
            ):
                continue
            admission = self._admission.admit(
                candidate=instantiated,
                registry=self._registry,
                scope_reference=scope_reference,
                allowed_domains=domains,
                admitted_at=now,
                expires_at=min(stored.expires_at, now + self._LIFETIME),
            )
            projections.append(projection)
            admissions.append(admission)
            admitted_stored.append(stored)

        if admissions:
            for stored in admitted_stored:
                self._pending[scope_reference].remove(stored)
            if not self._pending[scope_reference]:
                self._pending.pop(scope_reference, None)
            return self._remember(
                ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED,
                scope_reference,
                source_reference,
                projection=projections[-1],
                admission=admissions[-1],
                projections=tuple(projections),
                admissions=tuple(admissions),
                semantic_grounding=semantic,
            )
        return self._remember(
            fallback,
            scope_reference,
            source_reference,
            semantic_grounding=semantic,
        )

    def _store(self, stored: SessionLocalCompiledRuleSpec) -> None:
        items = self._pending.setdefault(stored.scope_reference, [])
        fingerprint = stored.compilation.source_fingerprint
        if any(item.compilation.source_fingerprint == fingerprint for item in items):
            return
        items.append(stored)
        if len(items) > self._MAX_PENDING_PER_SESSION:
            del items[: -self._MAX_PENDING_PER_SESSION]

    def _prune(self, now: datetime) -> None:
        for scope in tuple(self._pending):
            live = [item for item in self._pending[scope] if item.expires_at > now]
            if live:
                self._pending[scope] = live
            else:
                self._pending.pop(scope, None)

    def _remember(
        self,
        status: ProductiveTemporaryRuleIntakeStatus,
        scope_reference: str,
        source_reference: str,
        *,
        projection: GovernedContextualCaseClaimProjection | None = None,
        admission: GovernedTemporaryConcreteRuleAdmission | None = None,
        projections: tuple[GovernedContextualCaseClaimProjection, ...] = (),
        admissions: tuple[GovernedTemporaryConcreteRuleAdmission, ...] = (),
        semantic_grounding: GovernedContextualSemanticGroundingCandidate | None = None,
    ) -> ProductiveTemporaryRuleIntakeResult:
        result = ProductiveTemporaryRuleIntakeResult(
            status=status,
            scope_reference=scope_reference,
            source_reference=source_reference,
            pending_specs=self.pending_count(scope_reference),
            projection=projection,
            admission=admission,
            projections=projections,
            admissions=admissions,
            semantic_grounding=semantic_grounding,
        )
        self._last_result = result
        return result

    @staticmethod
    def _source_reference(scope_reference: str, text: str) -> str:
        digest = sha256(text.encode("utf-8")).hexdigest()[:16]
        return f"conversation:{scope_reference}/turn:{digest}"
