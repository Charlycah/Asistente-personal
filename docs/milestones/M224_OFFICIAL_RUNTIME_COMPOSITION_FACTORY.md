# M224 — Official Runtime Composition Factory

M224 closes the last startup gap between ROBY's certified architecture and its development console.

## Official value

```dotenv
ROBY_RUNTIME_ROOT_FACTORY=app.runtime_root_factory:build_runtime_root
```

## First run

```powershell
python main.py --setup
python main.py --doctor
python main.py
```

The setup assistant now proposes the official factory automatically. Existing custom factories remain supported through `--factory paquete.modulo:funcion`.

## Runtime graph

The factory composes:

- the local OpenAI-compatible provider configured in `.env`;
- runtime readiness and provider-health observations;
- conversational workload classification;
- internal knowledge need classification;
- deterministic `LLMRequest` construction;
- the official `RuntimeCompositionRoot` and governed conversation pipeline.

Retrieval remains disabled until an explicit governed retriever is configured. M224 does not introduce deployment, infrastructure mutation, background workers, or secret management.
