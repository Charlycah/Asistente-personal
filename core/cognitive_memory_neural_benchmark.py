from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class BenchmarkCandidate:
    candidate_id: str
    text: str
    relevance: int = 0


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    family: str
    query: str
    candidates: tuple[BenchmarkCandidate, ...]
    synthetic: bool = True
    private_content: bool = False


@dataclass(frozen=True)
class BenchmarkObservation:
    case_id: str
    family: str
    candidate_ids: tuple[str, ...]
    reranked_candidate_ids: tuple[str, ...]
    membership_changed: bool
    baseline_reciprocal_rank: float
    reranked_reciprocal_rank: float
    baseline_ndcg: float
    reranked_ndcg: float
    latency_ms: float


@dataclass(frozen=True)
class BenchmarkReport:
    baseline_mrr: float
    reranked_mrr: float
    baseline_ndcg: float
    reranked_ndcg: float
    semantic_cases_improved: int
    semantic_cases_total: int
    lexical_exact_regressions: int
    governance_violations: int
    p50_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float

    @property
    def mrr_delta(self) -> float:
        return self.reranked_mrr - self.baseline_mrr

    @property
    def ndcg_delta(self) -> float:
        return self.reranked_ndcg - self.baseline_ndcg


Reranker = Callable[
    [BenchmarkCase, tuple[BenchmarkCandidate, ...]],
    Sequence[BenchmarkCandidate],
]


def _candidate(candidate_id: str, text: str, relevance: int = 0) -> BenchmarkCandidate:
    return BenchmarkCandidate(candidate_id, text, relevance)


def synthetic_benchmark_corpus() -> tuple[BenchmarkCase, ...]:
    return (
        BenchmarkCase(
            "semantic-01",
            "semantic_paraphrase_weak_lexical",
            "¿qué prefería para trabajar sin distracciones?",
            (
                _candidate("sem-distractor", "Prefiere reuniones breves."),
                _candidate(
                    "sem-positive",
                    "Le resulta mejor concentrarse en un ambiente silencioso.",
                    2,
                ),
            ),
        ),
        BenchmarkCase(
            "lexical-01",
            "lexical_exact_preservation",
            "usa PostgreSQL para el proyecto Atlas",
            (
                _candidate(
                    "lex-positive",
                    "Usa PostgreSQL para el proyecto Atlas.",
                    2,
                ),
                _candidate("lex-distractor", "Atlas usa una base de datos."),
            ),
        ),
        BenchmarkCase(
            "distractor-01",
            "hard_distractor",
            "¿dónde prefiere leer cuando necesita calma?",
            (
                _candidate("hard-distractor", "Prefiere calma al leer informes."),
                _candidate(
                    "hard-positive",
                    "Para leer tranquilo suele elegir la biblioteca del barrio.",
                    2,
                ),
            ),
        ),
        BenchmarkCase(
            "multi-01",
            "multi_relevant",
            "¿qué bebidas calientes suele elegir?",
            (
                _candidate("multi-a", "Suele elegir té verde.", 2),
                _candidate("multi-x", "Prefiere caminar por la mañana."),
                _candidate("multi-b", "También disfruta del café suave.", 1),
            ),
        ),
        BenchmarkCase(
            "spanish-01",
            "spanish_morphology_paraphrase",
            "¿cómo organiza sus lecturas?",
            (
                _candidate("es-distractor", "Organiza reuniones los viernes."),
                _candidate(
                    "es-positive",
                    "Mantiene los libros ordenados por temática y autor.",
                    2,
                ),
            ),
        ),
        BenchmarkCase(
            "tie-01",
            "tie_stability",
            "recuerdos equivalentes",
            (
                _candidate("tie-a", "Primer recuerdo equivalente.", 1),
                _candidate("tie-b", "Segundo recuerdo equivalente.", 1),
            ),
        ),
    )


def identity_reranker(
    case: BenchmarkCase,
    candidates: tuple[BenchmarkCandidate, ...],
) -> tuple[BenchmarkCandidate, ...]:
    del case
    return candidates


def _membership_changed(
    expected: tuple[BenchmarkCandidate, ...],
    observed: Sequence[BenchmarkCandidate],
) -> bool:
    expected_ids = tuple(candidate.candidate_id for candidate in expected)
    observed_ids = tuple(candidate.candidate_id for candidate in observed)
    same_size = len(observed_ids) == len(expected_ids)
    same_ids = set(observed_ids) == set(expected_ids)
    return not (same_size and same_ids)


def _reciprocal_rank(candidates: Sequence[BenchmarkCandidate]) -> float:
    for position, candidate in enumerate(candidates, start=1):
        if candidate.relevance > 0:
            return 1.0 / position
    return 0.0


def _dcg(candidates: Sequence[BenchmarkCandidate]) -> float:
    return sum(
        (2**candidate.relevance - 1) / math.log2(position + 1)
        for position, candidate in enumerate(candidates, start=1)
        if candidate.relevance > 0
    )


def _ndcg(candidates: Sequence[BenchmarkCandidate]) -> float:
    ideal = sorted(candidates, key=lambda candidate: candidate.relevance, reverse=True)
    ideal_dcg = _dcg(ideal)
    if ideal_dcg == 0.0:
        return 0.0
    return _dcg(candidates) / ideal_dcg


def evaluate_case(
    case: BenchmarkCase,
    reranked_candidates: Sequence[BenchmarkCandidate],
    *,
    latency_ms: float = 0.0,
) -> BenchmarkObservation:
    reranked = tuple(reranked_candidates)
    membership_changed = _membership_changed(case.candidates, reranked)
    if membership_changed:
        reranked = case.candidates

    return BenchmarkObservation(
        case_id=case.case_id,
        family=case.family,
        candidate_ids=tuple(candidate.candidate_id for candidate in case.candidates),
        reranked_candidate_ids=tuple(candidate.candidate_id for candidate in reranked),
        membership_changed=membership_changed,
        baseline_reciprocal_rank=_reciprocal_rank(case.candidates),
        reranked_reciprocal_rank=_reciprocal_rank(reranked),
        baseline_ndcg=_ndcg(case.candidates),
        reranked_ndcg=_ndcg(reranked),
        latency_ms=max(0.0, latency_ms),
    )


def _mean(values: Sequence[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def evaluate_benchmark(
    corpus: Sequence[BenchmarkCase],
    *,
    reranker: Reranker,
) -> BenchmarkReport:
    observations: list[BenchmarkObservation] = []
    for case in corpus:
        started = time.perf_counter()
        proposed = tuple(reranker(case, case.candidates))
        latency_ms = (time.perf_counter() - started) * 1000.0
        observations.append(evaluate_case(case, proposed, latency_ms=latency_ms))

    semantic = tuple(
        observation
        for observation in observations
        if observation.family
        in {
            "semantic_paraphrase_weak_lexical",
            "hard_distractor",
            "multi_relevant",
            "spanish_morphology_paraphrase",
        }
    )
    lexical = tuple(
        observation
        for observation in observations
        if observation.family == "lexical_exact_preservation"
    )
    latencies = tuple(observation.latency_ms for observation in observations)

    return BenchmarkReport(
        baseline_mrr=_mean(
            tuple(item.baseline_reciprocal_rank for item in observations)
        ),
        reranked_mrr=_mean(
            tuple(item.reranked_reciprocal_rank for item in observations)
        ),
        baseline_ndcg=_mean(tuple(item.baseline_ndcg for item in observations)),
        reranked_ndcg=_mean(tuple(item.reranked_ndcg for item in observations)),
        semantic_cases_improved=sum(
            item.reranked_reciprocal_rank > item.baseline_reciprocal_rank
            or item.reranked_ndcg > item.baseline_ndcg
            for item in semantic
        ),
        semantic_cases_total=len(semantic),
        lexical_exact_regressions=sum(
            item.reranked_reciprocal_rank < item.baseline_reciprocal_rank
            or item.reranked_ndcg < item.baseline_ndcg
            for item in lexical
        ),
        governance_violations=sum(item.membership_changed for item in observations),
        p50_latency_ms=statistics.median(latencies) if latencies else 0.0,
        p95_latency_ms=_percentile(latencies, 0.95),
        max_latency_ms=max(latencies, default=0.0),
    )


def go_no_go(report: BenchmarkReport) -> str:
    if report.governance_violations != 0:
        return "NO-GO"
    if report.lexical_exact_regressions != 0:
        return "NO-GO"
    if report.mrr_delta <= 0.0 or report.ndcg_delta <= 0.0:
        return "NO-GO"
    if report.semantic_cases_total <= 0:
        return "NO-GO"
    if report.semantic_cases_improved * 2 <= report.semantic_cases_total:
        return "NO-GO"
    return "GO"
