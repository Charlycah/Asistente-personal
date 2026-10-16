# M178 — Runtime Composition Root

## Objective

Create ROBY's single official composition boundary for the governed operational runtime.

## Composition path

1. Accept explicit runtime dependencies for readiness, provider observations, workload, knowledge need, inference request construction, local providers, and retrievers.
2. Construct one M166 provider health evaluator.
3. Construct one M167 local-first provider policy.
4. Construct one M168 governed provider router.
5. Construct one M169 knowledge-source policy.
6. Construct one M170 retrieval orchestrator.
7. Construct M171, M173, and M175 execution and assembly boundaries.
8. Adapt M166-M170 into the M177 preparation port.
9. Return one official M177 operational conversation pipeline.

## Governance

- The root wires modules; it does not classify, infer, authorize, retrieve, or generate responses.
- Turn-specific facts are supplied through explicit ports.
- Exact lineage is preserved across M166-M177.
- Composition is idempotent and side-effect free.
- No provider, retriever, network, or platform action occurs during composition.
- The composed graph is immutable and inspectable.

## Delivered

- `RuntimeCompositionDependencies` and `RuntimeCompositionConfig`.
- Explicit ports for readiness, observations, workload, knowledge need, and inference requests.
- `GovernedRuntimePreparation` implementing the M177 preparation contract.
- Immutable `RuntimeComposition` graph.
- Idempotent `RuntimeCompositionRoot.compose()` and official `build()` entry point.
- Optional retrieval composition while preserving the M177 contract.

## Validation

- 20 focused M178 tests.
- 47 combined M177-M178 tests.
- Ruff clean.
- Full repository suite passing without regressions.
