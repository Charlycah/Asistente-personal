from __future__ import annotations

import sqlite3
from hashlib import sha256
from pathlib import Path

from core.cognitive_intent import CognitiveIntentAnalyzer
from core.cognitive_memory import (
    CognitiveLearningPolicy,
    LearningAction,
    LearningCandidate,
    LearningCategory,
)
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
)
from core.cognitive_memory_store import (
    CognitiveMemoryRecord,
    CognitiveMemorySearch,
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.conversation_strategy import ConversationStrategyPlanner
from core.llm_provider import LLMRequest
from core.memory_planning_evidence import (
    METADATA_KEY as MEMORY_PLANNING_METADATA_KEY,
)
from core.memory_planning_evidence import (
    encode_memory_planning_evidence,
    project_recalled_memory,
)
from core.memory_prompt_context import MemoryPromptContextBuilder
from core.platform_runtime_compatibility import apply_private_file_permissions

from .models import (
    MemoryRuntimeConfig,
    MemoryRuntimeContext,
    MemoryRuntimeRecalledAntecedentCandidate,
    MemoryRuntimeScope,
    MemoryRuntimeWriteResult,
)


class MemoryRuntimeIntegration:
    """Connects governed runtime turns to ROBY's existing cognitive memory stack."""

    def __init__(self, config: MemoryRuntimeConfig | None = None) -> None:
        self.config = config or MemoryRuntimeConfig()
        self.intent_analyzer = CognitiveIntentAnalyzer()
        self.strategy_planner = ConversationStrategyPlanner()
        self.learning_policy = CognitiveLearningPolicy()
        self.context_builder = MemoryPromptContextBuilder()
        self._stores: dict[str, CognitiveMemoryStore] = {}

    def enrich(
        self, *, owner: str, text: str, request: LLMRequest
    ) -> MemoryRuntimeContext:
        normalized_owner = self._owner(owner)
        scopes = (MemoryRuntimeScope.PRIVATE,)
        if self.config.include_shared:
            scopes += (MemoryRuntimeScope.SHARED,)
        if not self.config.enable_recall:
            return MemoryRuntimeContext(
                owner=normalized_owner,
                scopes=scopes,
                request=request,
                rationale=("memory_recall_disabled",),
            )

        intent = self.intent_analyzer.analyze(text)
        strategy = self.strategy_planner.plan(intent)
        memories = []
        ids = []
        for scope in scopes:
            recall = CognitiveMemoryRecall(self._store(normalized_owner, scope)).recall(
                CognitiveMemoryRecallRequest(
                    text=text,
                    intent_result=intent,
                    strategy=strategy,
                    limit=self.config.recall_limit,
                )
            )
            memories.extend(recall.items)
            ids.extend(f"{scope.value}:{item.memory.id}" for item in recall.items)
        selected = tuple(memories[: self.config.recall_limit])
        if not selected:
            return MemoryRuntimeContext(
                owner=normalized_owner,
                scopes=scopes,
                request=request,
                rationale=("no_relevant_memory",),
            )
        from core.cognitive_memory_recall import CognitiveMemoryRecallResult

        prompt_context = self.context_builder.build(
            CognitiveMemoryRecallResult(True, selected, "runtime_memory_recall"),
            strategy=strategy,
        )
        scoped_ids = tuple(ids[: self.config.recall_limit])
        recalled_antecedent_candidates = tuple(
            MemoryRuntimeRecalledAntecedentCandidate(
                scoped_memory_reference=scoped_reference,
                content_fingerprint=sha256(
                    item.memory.content.encode("utf-8")
                ).hexdigest(),
                recall_score=item.score,
            )
            for item, scoped_reference in zip(selected, scoped_ids, strict=True)
        )
        planning_evidence = project_recalled_memory(
            owner=normalized_owner,
            items=selected,
            scoped_ids=scoped_ids,
        )
        metadata = {**request.metadata, "memory_context": "included"}
        if planning_evidence:
            metadata[MEMORY_PLANNING_METADATA_KEY] = encode_memory_planning_evidence(
                planning_evidence
            )
        enriched = LLMRequest(
            prompt=self.context_builder.wrap_prompt(request.prompt, prompt_context),
            system_prompt=request.system_prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metadata=metadata,
        )
        return MemoryRuntimeContext(
            owner=normalized_owner,
            scopes=scopes,
            request=enriched,
            recalled_memory_ids=scoped_ids,
            recalled_antecedent_candidates=recalled_antecedent_candidates,
            recalled_count=len(selected),
            context_included=True,
            rationale=("memory_context_included",),
        )

    def record(self, *, owner: str, text: str) -> MemoryRuntimeWriteResult:
        normalized_owner = self._owner(owner)
        if not self.config.enable_learning:
            return MemoryRuntimeWriteResult(
                owner=normalized_owner,
                stored_memory_ids=(),
                stored_count=0,
                learning_enabled=False,
                rationale=("memory_learning_disabled",),
            )
        intent = self.intent_analyzer.analyze(text)
        strategy = self.strategy_planner.plan(intent)
        result = self.learning_policy.evaluate(
            text=text,
            intent_result=intent,
            strategy=strategy,
        )
        stored = []
        if result.should_store:
            store = self._store(normalized_owner, MemoryRuntimeScope.PRIVATE)
            for candidate in result.candidates:
                if candidate.action.value == "store":
                    stored.append(f"private:{store.store_candidate(candidate)}")
        return MemoryRuntimeWriteResult(
            owner=normalized_owner,
            stored_memory_ids=tuple(stored),
            stored_count=len(stored),
            learning_enabled=True,
            rationale=("memory_stored" if stored else "memory_not_stored",),
        )

    def store_explicit(
        self,
        *,
        owner: str,
        text: str,
        metadata: dict[str, str] | None = None,
    ) -> MemoryRuntimeWriteResult:
        normalized_owner = self._owner(owner)
        normalized_text = " ".join(text.strip().split())
        if not normalized_text:
            raise ValueError("explicit memory text must not be blank")
        if not self.config.enable_learning:
            return MemoryRuntimeWriteResult(
                owner=normalized_owner,
                stored_memory_ids=(),
                stored_count=0,
                learning_enabled=False,
                rationale=("memory_learning_disabled",),
            )
        candidate = LearningCandidate(
            content=normalized_text,
            category=LearningCategory.STABLE_KNOWLEDGE,
            action=LearningAction.STORE,
            confidence=1.0,
            reason="explicit_user_memory_request",
            tags=("explicit", "personal"),
            metadata=metadata or {},
        )
        memory_id = self.private_store(normalized_owner).store_candidate(candidate)
        return MemoryRuntimeWriteResult(
            owner=normalized_owner,
            stored_memory_ids=(f"private:{memory_id}",),
            stored_count=1,
            learning_enabled=True,
            rationale=("explicit_memory_stored",),
        )

    def store_governed_learning(
        self,
        *,
        owner: str,
        text: str,
        confidence: float,
        metadata: dict[str, str],
        idempotency_key: str,
        learning_category: LearningCategory = LearningCategory.USER_PREFERENCE,
    ) -> MemoryRuntimeWriteResult:
        normalized_owner = self._owner(owner)
        normalized_text = " ".join(text.strip().split())
        if not normalized_text:
            raise ValueError("governed learning text must not be blank")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("governed learning confidence must be between 0 and 1")
        if not idempotency_key.strip():
            raise ValueError("governed learning requires idempotency key")
        if not self.config.enable_learning:
            return MemoryRuntimeWriteResult(
                owner=normalized_owner,
                stored_memory_ids=(),
                stored_count=0,
                learning_enabled=False,
                rationale=("memory_learning_disabled",),
            )

        candidate = LearningCandidate(
            content=normalized_text,
            category=learning_category,
            action=LearningAction.STORE,
            confidence=confidence,
            reason="governed_human_approved_learning",
            tags=(
                "governed_learning",
                "human_approved",
                (
                    "preference"
                    if learning_category is LearningCategory.USER_PREFERENCE
                    else learning_category.value
                ),
            ),
            metadata=metadata,
        )
        memory_id, created = self.private_store(
            normalized_owner
        ).store_candidate_idempotent(
            candidate,
            idempotency_key=idempotency_key,
        )
        rationale = (
            "governed_learning_stored"
            if created
            else "governed_learning_already_stored"
        )
        return MemoryRuntimeWriteResult(
            owner=normalized_owner,
            stored_memory_ids=(f"private:{memory_id}",),
            stored_count=1 if created else 0,
            learning_enabled=True,
            rationale=(rationale,),
        )

    def apply_governed_knowledge_revision(
        self,
        *,
        owner: str,
        target_memory_id: str,
        target_category: str,
        expected_current_content: str,
        expected_target_fingerprint: str,
        replacement_content: str,
        replacement_idempotency_key: str,
        revision_request_id: str,
        revision_proposal_id: str,
        revision_approval_id: str,
        application_proposal_id: str,
        corrective_evidence_ids: tuple[str, ...],
        revision_proposal_fingerprint: str,
        human_approval_fingerprint: str,
        application_proposal_fingerprint: str,
    ) -> tuple[int, bool]:
        normalized_owner = self._owner(owner)
        return self.private_store(normalized_owner).apply_governed_revision_atomic(
            target_memory_id=target_memory_id,
            target_category=target_category,
            expected_current_content=expected_current_content,
            expected_target_fingerprint=expected_target_fingerprint,
            replacement_content=replacement_content,
            replacement_idempotency_key=replacement_idempotency_key,
            revision_request_id=revision_request_id,
            revision_proposal_id=revision_proposal_id,
            revision_approval_id=revision_approval_id,
            application_proposal_id=application_proposal_id,
            corrective_evidence_ids=corrective_evidence_ids,
            revision_proposal_fingerprint=revision_proposal_fingerprint,
            human_approval_fingerprint=human_approval_fingerprint,
            application_proposal_fingerprint=application_proposal_fingerprint,
            target_owner=normalized_owner,
        )

    def search(
        self,
        *,
        owner: str,
        query: str | None,
        limit: int = 5,
        active_only: bool = False,
    ) -> tuple[CognitiveMemoryRecord, ...]:
        normalized_owner = self._owner(owner)
        records = self.private_store(normalized_owner).search(
            CognitiveMemorySearch(query=query, limit=limit)
        )
        if not active_only:
            return records
        return tuple(
            record
            for record in records
            if record.metadata.get("status", "active") not in {"archived", "superseded"}
        )

    def governed_learning_temporal_introspection(
        self,
        *,
        owner: str,
        created_at_from: str,
        created_at_before: str,
        limit: int = 20,
    ) -> tuple[CognitiveMemoryRecord, ...]:
        normalized_owner = self._owner(owner)
        return self.private_store(normalized_owner).search(
            CognitiveMemorySearch(
                tag="governed_learning",
                created_at_from=created_at_from,
                created_at_before=created_at_before,
                limit=limit,
            )
        )

    def count(self, *, owner: str) -> int:
        return self.private_store(self._owner(owner)).count()

    def private_store(self, owner: str) -> CognitiveMemoryStore:
        return self._store(self._owner(owner), MemoryRuntimeScope.PRIVATE)

    def shared_store(self) -> CognitiveMemoryStore:
        return self._store("shared", MemoryRuntimeScope.SHARED)

    def _store(self, owner: str, scope: MemoryRuntimeScope) -> CognitiveMemoryStore:
        key = "shared" if scope is MemoryRuntimeScope.SHARED else owner.casefold()
        cache_key = f"{scope.value}:{key}"
        if cache_key not in self._stores:
            filename = self._store_filename(key=key, scope=scope)
            path = Path(self.config.root_path) / filename
            if (
                self.config.canonical_joint_owner
                and scope is MemoryRuntimeScope.PRIVATE
            ):
                self._copy_unambiguous_legacy_store(path)
            self._stores[cache_key] = CognitiveMemoryStore(
                CognitiveMemoryStoreConfig(db_path=path)
            )
            try:
                apply_private_file_permissions(path)
            except OSError:
                pass
        return self._stores[cache_key]

    def _store_filename(self, *, key: str, scope: MemoryRuntimeScope) -> str:
        if scope is MemoryRuntimeScope.SHARED:
            return "shared.sqlite3"
        if self.config.canonical_joint_owner:
            return self.config.canonical_store_filename
        digest = sha256(key.encode()).hexdigest()[:16]
        return f"owner-{digest}.sqlite3"

    def _copy_unambiguous_legacy_store(self, target: Path) -> None:
        if target.exists():
            return
        root = Path(self.config.root_path)
        candidates = []
        for owner in self.config.legacy_store_owners:
            digest = sha256(owner.casefold().encode()).hexdigest()[:16]
            candidate = root / f"owner-{digest}.sqlite3"
            if candidate.exists():
                candidates.append(candidate)
        if len(candidates) > 1:
            raise RuntimeError(
                "multiple recognized legacy memory stores require human review"
            )
        if len(candidates) == 1:
            target.parent.mkdir(parents=True, exist_ok=True)
            with (
                sqlite3.connect(candidates[0]) as source,
                sqlite3.connect(target) as destination,
            ):
                source.backup(destination)

    def _owner(self, owner: str) -> str:
        normalized = owner.strip()
        if not normalized:
            raise ValueError("memory runtime owner must not be blank")
        if self.config.canonical_joint_owner:
            accepted = {item.casefold() for item in self.config.accepted_owner_aliases}
            if normalized.casefold() not in accepted:
                raise ValueError("memory owner is not a recognized ROBY coowner")
            return self.config.canonical_owner
        return normalized
