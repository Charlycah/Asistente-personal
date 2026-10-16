from __future__ import annotations

from datetime import datetime, timezone

from core.governed_provider_routing import ProviderRouteStatus
from core.llm_provider import LLMProvider, LLMRequest, LLMResponse
from core.provider_health_evaluation import ProviderKind

from .models import (
    InMemoryLocalProviderExecutionRepository,
    LocalProviderExecutionAction,
    LocalProviderExecutionConfig,
    LocalProviderExecutionRepository,
    LocalProviderExecutionRequest,
    LocalProviderExecutionResult,
    LocalProviderExecutionStatus,
)


class GovernedProviderExecutionAdapter:
    def __init__(
        self,
        providers: tuple[LLMProvider, ...] = (),
        *,
        config: LocalProviderExecutionConfig | None = None,
        repository: LocalProviderExecutionRepository | None = None,
    ) -> None:
        self._config = config or LocalProviderExecutionConfig()
        self._repository = repository or InMemoryLocalProviderExecutionRepository()
        self._providers: dict[str, LLMProvider] = {}
        for provider in providers:
            name = provider.name.strip()
            if not name:
                raise ValueError("local provider name must not be blank")
            key = name.casefold()
            if key in self._providers:
                raise ValueError("local provider names must be unique")
            self._providers[key] = provider

    @property
    def last_execution(self) -> LocalProviderExecutionResult | None:
        items = self._repository.list_all()
        return items[-1] if items else None

    @staticmethod
    def _payload_observation(provider):
        return getattr(provider, "last_payload_observation", None)

    def execute(
        self,
        request: LocalProviderExecutionRequest,
        *,
        now: datetime | None = None,
    ) -> LocalProviderExecutionResult:
        created_at = now or datetime.now(timezone.utc)
        route = request.route
        selected = route.selected_provider

        if not request.execution_requested:
            return self._store(
                request,
                LocalProviderExecutionStatus.NOT_APPLICABLE,
                LocalProviderExecutionAction.NONE,
                None,
                "",
                "",
                False,
                ("Local provider execution was not requested.",),
                created_at,
            )
        is_local = (
            route.status is ProviderRouteStatus.ROUTED_LOCAL
            and route.route_kind is ProviderKind.LOCAL
        )
        is_remote = (
            route.status is ProviderRouteStatus.ROUTED_REMOTE
            and route.route_kind is ProviderKind.REMOTE
        )
        if selected is None or not (is_local or is_remote):
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                "",
                "",
                False,
                ("Provider execution requires an active governed route.",),
                created_at,
            )
        if is_local and not self._config.allow_local_execution:
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                selected.provider_name,
                selected.model_name,
                False,
                ("Local provider execution is disabled by configuration.",),
                created_at,
            )
        if is_remote and not self._config.allow_remote_execution:
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                selected.provider_name,
                selected.model_name,
                False,
                ("Remote provider execution is disabled by configuration.",),
                created_at,
            )
        if (
            len(request.inference_request.prompt)
            > self._config.maximum_prompt_characters
        ):
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                selected.provider_name,
                selected.model_name,
                False,
                ("The inference prompt exceeds the governed provider limit.",),
                created_at,
            )

        provider = self._providers.get(selected.provider_name.casefold())
        if provider is None:
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                selected.provider_name,
                selected.model_name,
                False,
                ("The routed provider is not registered in the execution adapter.",),
                created_at,
            )

        routed_model = selected.model_name.strip()
        requested_model = (request.inference_request.model or routed_model).strip()
        if (
            self._config.require_route_model_match
            and request.inference_request.model
            and requested_model.casefold() != routed_model.casefold()
        ):
            return self._store(
                request,
                LocalProviderExecutionStatus.WITHHELD,
                LocalProviderExecutionAction.WITHHOLD,
                None,
                selected.provider_name,
                routed_model,
                False,
                ("The requested model does not match the governed route.",),
                created_at,
            )

        governed_request = LLMRequest(
            prompt=request.inference_request.prompt,
            system_prompt=request.inference_request.system_prompt,
            model=routed_model or requested_model or None,
            max_tokens=request.inference_request.max_tokens,
            temperature=request.inference_request.temperature,
            metadata=dict(request.inference_request.metadata),
            messages=tuple(request.inference_request.messages),
        )
        try:
            response = provider.generate(governed_request)
        except Exception as exc:  # provider boundary containment
            failed = LLMResponse(
                text="",
                provider=selected.provider_name,
                model=routed_model or None,
                accepted=False,
                error=type(exc).__name__,
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.FAILED,
                LocalProviderExecutionAction.REPORT_FAILURE,
                failed,
                selected.provider_name,
                routed_model,
                True,
                ("The provider raised an exception and it was contained.",),
                created_at,
                self._payload_observation(provider),
            )

        if not isinstance(response, LLMResponse):
            failed = LLMResponse(
                text="",
                provider=selected.provider_name,
                model=routed_model or None,
                accepted=False,
                error="invalid_response_type",
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.FAILED,
                LocalProviderExecutionAction.REPORT_FAILURE,
                failed,
                selected.provider_name,
                routed_model,
                True,
                ("The provider returned an invalid response type.",),
                created_at,
                self._payload_observation(provider),
            )
        if response.provider.strip().casefold() != selected.provider_name.casefold():
            rejected = LLMResponse(
                text="",
                provider=response.provider,
                model=response.model,
                accepted=False,
                error="provider_mismatch",
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.REJECTED,
                LocalProviderExecutionAction.REJECT_RESPONSE,
                rejected,
                selected.provider_name,
                routed_model,
                True,
                ("The response provider does not match the governed route.",),
                created_at,
                self._payload_observation(provider),
            )
        response_model = (response.model or routed_model).strip()
        if (
            self._config.require_route_model_match
            and routed_model
            and response_model.casefold() != routed_model.casefold()
        ):
            rejected = LLMResponse(
                text="",
                provider=response.provider,
                model=response.model,
                accepted=False,
                error="model_mismatch",
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.REJECTED,
                LocalProviderExecutionAction.REJECT_RESPONSE,
                rejected,
                selected.provider_name,
                routed_model,
                True,
                ("The response model does not match the governed route.",),
                created_at,
                self._payload_observation(provider),
            )
        if not response.accepted or response.error:
            return self._store(
                request,
                LocalProviderExecutionStatus.FAILED,
                LocalProviderExecutionAction.REPORT_FAILURE,
                response,
                selected.provider_name,
                routed_model or response_model,
                True,
                ("The provider did not accept the inference request.",),
                created_at,
                self._payload_observation(provider),
            )
        text = response.text.strip()
        if not text:
            rejected = LLMResponse(
                text="",
                provider=response.provider,
                model=response.model,
                accepted=False,
                error="empty_response",
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.REJECTED,
                LocalProviderExecutionAction.REJECT_RESPONSE,
                rejected,
                selected.provider_name,
                routed_model or response_model,
                True,
                ("The provider returned an empty response.",),
                created_at,
                self._payload_observation(provider),
            )
        if len(text) > self._config.maximum_response_characters:
            rejected = LLMResponse(
                text="",
                provider=response.provider,
                model=response.model,
                accepted=False,
                error="response_too_large",
            )
            return self._store(
                request,
                LocalProviderExecutionStatus.REJECTED,
                LocalProviderExecutionAction.REJECT_RESPONSE,
                rejected,
                selected.provider_name,
                routed_model or response_model,
                True,
                ("The provider response exceeds the governed size limit.",),
                created_at,
                self._payload_observation(provider),
            )

        normalized = LLMResponse(
            text=text,
            provider=selected.provider_name,
            model=routed_model or response_model,
            accepted=True,
        )
        action = (
            LocalProviderExecutionAction.EXECUTE_REMOTE_PROVIDER
            if is_remote
            else LocalProviderExecutionAction.EXECUTE_LOCAL_PROVIDER
        )
        rationale = (
            "The governed remote provider completed inference successfully."
            if is_remote
            else "The governed local provider completed inference successfully."
        )
        return self._store(
            request,
            LocalProviderExecutionStatus.COMPLETED,
            action,
            normalized,
            selected.provider_name,
            routed_model or response_model,
            True,
            (rationale,),
            created_at,
            self._payload_observation(provider),
        )

    def _store(
        self,
        request,
        status,
        action,
        response,
        provider_name,
        model_name,
        attempted,
        rationale,
        created_at,
        provider_payload_observation=None,
    ):
        result = LocalProviderExecutionResult(
            request=request,
            status=status,
            action=action,
            response=response,
            selected_provider_name=provider_name,
            selected_model_name=model_name,
            provider_call_performed=attempted,
            inference_performed=attempted,
            network_access_allowed=(
                attempted and request.route.route_kind is ProviderKind.REMOTE
            ),
            remote_fallback_allowed=False,
            platform_mutation_allowed=False,
            rationale=rationale,
            provider_payload_observation=provider_payload_observation,
            created_at=created_at,
        )
        self._repository.add(result)
        return result
