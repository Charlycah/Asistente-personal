from __future__ import annotations

from dataclasses import dataclass

from .official_runtime_composition import OfficialROBYRuntime
from .runtime_compatibility import (
    RUNTIME_COMPATIBILITY_REGISTRY,
    CompatibilityDisposition,
)
from .runtime_execution_inventory import (
    EXECUTION_ROOT_INVENTORY,
    ExecutionRootDisposition,
    ExecutionRootRole,
    canonical_execution_chain,
)


@dataclass(frozen=True)
class RuntimeExecutionCertification:
    """Immutable proof that ROBY converges on one official runtime authority."""

    certified: bool
    process_entrypoints: tuple[str, ...]
    lifecycle_authorities: tuple[str, ...]
    canonical_chain: tuple[str, ...]
    non_executable_compatibility_paths: tuple[str, ...]
    findings: tuple[str, ...]


def certify_runtime_execution(
    runtime: OfficialROBYRuntime | None = None,
) -> RuntimeExecutionCertification:
    process_entrypoints = tuple(
        record.target
        for record in EXECUTION_ROOT_INVENTORY
        if record.role is ExecutionRootRole.CANONICAL_PROCESS_ENTRYPOINT
        and record.disposition is ExecutionRootDisposition.KEEP_CANONICAL
    )
    lifecycle_authorities = tuple(
        record.target
        for record in EXECUTION_ROOT_INVENTORY
        if record.role is ExecutionRootRole.CANONICAL_LIFECYCLE_AUTHORITY
        and record.disposition is ExecutionRootDisposition.KEEP_CANONICAL
    )
    compatibility_paths = tuple(
        record.target
        for record in RUNTIME_COMPATIBILITY_REGISTRY
        if record.disposition is not CompatibilityDisposition.CANONICAL
        and not record.executable
    )

    findings: list[str] = []
    if len(process_entrypoints) != 1:
        findings.append("canonical_process_entrypoint_count_invalid")
    if len(lifecycle_authorities) != 1:
        findings.append("canonical_lifecycle_authority_count_invalid")
    if any(
        record.executable
        for record in RUNTIME_COMPATIBILITY_REGISTRY
        if record.disposition is not CompatibilityDisposition.CANONICAL
    ):
        findings.append("compatibility_path_is_executable")
    if runtime is not None:
        if not isinstance(runtime, OfficialROBYRuntime):
            findings.append("runtime_is_not_official_roby_runtime")
        elif runtime.conversation.bootstrap is not runtime.bootstrap:
            findings.append("conversation_bootstrap_identity_mismatch")
        elif runtime.bootstrap.root is not runtime.root:
            findings.append("composition_root_identity_mismatch")

    return RuntimeExecutionCertification(
        certified=not findings,
        process_entrypoints=process_entrypoints,
        lifecycle_authorities=lifecycle_authorities,
        canonical_chain=canonical_execution_chain(),
        non_executable_compatibility_paths=compatibility_paths,
        findings=tuple(findings),
    )
