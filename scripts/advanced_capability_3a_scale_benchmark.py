from __future__ import annotations

import argparse
import json
import platform
import sys
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.governed_information_normalizer import (  # noqa: E402
    GovernedInformationNormalizer,
    InformationVerificationStatus,
    NormalizedInformationKind,
    RawGovernedInformation,
)
from app.governed_information_sources import GovernedInformationSources  # noqa: E402
from app.governed_source_query import (  # noqa: E402
    GovernedSourceQuery,
    GovernedSourceQueryContract,
)
from app.governed_source_query_executor import GovernedSourceQueryExecutor  # noqa: E402
from app.personal_interest_center import (  # noqa: E402
    InterestTopic,
    PersonalInterestCenter,
)
from app.relevance_evaluator import RelevanceEvaluator  # noqa: E402

SCHEMA_VERSION = "advanced-capability-3a-scale-benchmark-v1"
DEFAULT_LEVELS = (100, 1_000, 10_000, 50_000)
QUERY_LIMIT = 100
DECISIVE_ITEM_COUNT = 5
SOURCE_ID = "technology_editorial"
BENCHMARK_TOPIC = InterestTopic.PROGRAMMING


@dataclass(frozen=True)
class ScaleLevelResult:
    input_count: int
    query_count: int
    max_items_per_query: int
    processed_count: int
    selected_count: int
    rejected_count: int
    duplicate_count: int
    decisive_item_count: int
    decisive_items_selected: int
    relevant_evidence_recall: float
    elapsed_seconds: float
    items_per_second: float
    peak_memory_bytes: int
    provenance_integrity: bool
    corrupt_provenance_rejected: bool
    deterministic_digest: str
    passed: bool


@dataclass(frozen=True)
class ScaleBenchmarkReport:
    schema_version: str
    generated_at: str
    python_version: str
    platform: str
    source_authority: str
    normalizer_authority: str
    executor_authority: str
    network_enabled: bool
    automatic_fetch_enabled: bool
    query_limit: int
    levels: tuple[ScaleLevelResult, ...]
    certified_max_items: int
    status: str
    report_fingerprint: str


class SyntheticScaleAdapter:
    network_enabled = False

    def __init__(self, dataset: tuple[Mapping[str, object], ...]) -> None:
        self._dataset = dataset

    def execute(self, query: GovernedSourceQuery) -> tuple[Mapping[str, object], ...]:
        offset = int(query.parameters.get("offset", "0"))
        return self._dataset[offset : offset + query.limit]


def _item(index: int, *, decisive: bool = False) -> dict[str, object]:
    external_id = f"synthetic-{index:07d}"
    return {
        "source_id": SOURCE_ID,
        "external_id": external_id,
        "title": (
            f"Critical programming evidence {index}"
            if decisive
            else f"Routine programming signal {index}"
        ),
        "topics": (BENCHMARK_TOPIC.value,),
        "kind": NormalizedInformationKind.NEWS.value,
        "verification": InformationVerificationStatus.REPORTED.value,
        "importance": 20 if decisive else 0,
        "time_sensitive": decisive,
        "tags": ("decisive",) if decisive else ("noise",),
    }


def build_synthetic_dataset(count: int) -> tuple[Mapping[str, object], ...]:
    if count < DECISIVE_ITEM_COUNT:
        raise ValueError("scale dataset must contain all decisive evidence items")
    decisive_positions = {
        0,
        count // 4,
        count // 2,
        (3 * count) // 4,
        count - 1,
    }
    return tuple(
        _item(index, decisive=index in decisive_positions) for index in range(count)
    )


def _raw_from_mapping(item: Mapping[str, object]) -> RawGovernedInformation:
    topics = frozenset(InterestTopic(str(value)) for value in item["topics"])
    return RawGovernedInformation(
        source_id=str(item["source_id"]),
        external_id=str(item["external_id"]),
        title=str(item["title"]),
        topics=topics,
        kind=NormalizedInformationKind(str(item["kind"])),
        verification=InformationVerificationStatus(str(item["verification"])),
        importance=int(item["importance"]),
        time_sensitive=bool(item["time_sensitive"]),
        tags=tuple(str(value) for value in item["tags"]),
    )


def _digest(values: list[str]) -> str:
    payload = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _corrupt_provenance_is_rejected(normalizer: GovernedInformationNormalizer) -> bool:
    corrupt = RawGovernedInformation(
        source_id="undeclared-scale-source",
        external_id="corrupt-provenance",
        title="Corrupt provenance control",
        topics=frozenset({BENCHMARK_TOPIC}),
    )
    try:
        normalizer.normalize(corrupt)
    except KeyError:
        return True
    return False


def run_scale_level(count: int) -> ScaleLevelResult:
    sources = GovernedInformationSources()
    contract = GovernedSourceQueryContract(sources)
    executor = GovernedSourceQueryExecutor(contract)
    normalizer = GovernedInformationNormalizer(sources)
    relevance = RelevanceEvaluator(PersonalInterestCenter())
    dataset = build_synthetic_dataset(count)
    executor.register(SOURCE_ID, SyntheticScaleAdapter(dataset))

    selected_ids: list[str] = []
    seen_ids: set[str] = set()
    duplicate_count = 0
    rejected_count = 0
    decisive_selected = 0
    processed_count = 0
    query_count = 0
    provenance_integrity = True
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)

    tracemalloc.start()
    started = perf_counter()
    try:
        for offset in range(0, count, QUERY_LIMIT):
            query = GovernedSourceQuery(
                source_id=SOURCE_ID,
                topics=frozenset({BENCHMARK_TOPIC}),
                limit=min(QUERY_LIMIT, count - offset),
                parameters={"offset": str(offset)},
            )
            result = executor.execute(query)
            query_count += 1
            response = result.response
            if response is None:
                raise RuntimeError("scale benchmark query returned no response")
            for item in response.raw_items:
                try:
                    normalized = normalizer.normalize(_raw_from_mapping(item))
                except (KeyError, TypeError, ValueError):
                    rejected_count += 1
                    continue
                processed_count += 1
                if normalized.source_id != SOURCE_ID:
                    provenance_integrity = False
                if normalized.canonical_id in seen_ids:
                    duplicate_count += 1
                seen_ids.add(normalized.canonical_id)
                decision = relevance.evaluate(
                    normalized.as_relevance_candidate(), now=now
                )
                if decision.should_share:
                    selected_ids.append(normalized.canonical_id)
                    if "decisive" in normalized.tags:
                        decisive_selected += 1
    finally:
        elapsed = perf_counter() - started
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    corrupt_rejected = _corrupt_provenance_is_rejected(normalizer)
    recall = decisive_selected / DECISIVE_ITEM_COUNT
    digest = _digest(selected_ids)
    passed = all(
        (
            processed_count == count,
            rejected_count == 0,
            duplicate_count == 0,
            provenance_integrity,
            corrupt_rejected,
            decisive_selected == DECISIVE_ITEM_COUNT,
            executor.observability.observations_retained <= executor.MAX_OBSERVATIONS,
        )
    )
    return ScaleLevelResult(
        input_count=count,
        query_count=query_count,
        max_items_per_query=QUERY_LIMIT,
        processed_count=processed_count,
        selected_count=len(selected_ids),
        rejected_count=rejected_count,
        duplicate_count=duplicate_count,
        decisive_item_count=DECISIVE_ITEM_COUNT,
        decisive_items_selected=decisive_selected,
        relevant_evidence_recall=recall,
        elapsed_seconds=round(elapsed, 6),
        items_per_second=round(count / elapsed, 3) if elapsed > 0 else 0.0,
        peak_memory_bytes=peak_memory,
        provenance_integrity=provenance_integrity,
        corrupt_provenance_rejected=corrupt_rejected,
        deterministic_digest=digest,
        passed=passed,
    )


def run_benchmark(levels: tuple[int, ...] = DEFAULT_LEVELS) -> ScaleBenchmarkReport:
    if not levels or any(level <= 0 for level in levels):
        raise ValueError("scale benchmark levels must be positive")
    sources = GovernedInformationSources()
    normalizer = GovernedInformationNormalizer(sources)
    executor = GovernedSourceQueryExecutor(GovernedSourceQueryContract(sources))
    results = tuple(run_scale_level(level) for level in levels)
    certified = max(
        (result.input_count for result in results if result.passed), default=0
    )
    status = "pass" if all(result.passed for result in results) else "partial"
    fingerprint_payload = {
        "schema_version": SCHEMA_VERSION,
        "levels": [
            {
                "input_count": result.input_count,
                "processed_count": result.processed_count,
                "selected_count": result.selected_count,
                "relevant_evidence_recall": result.relevant_evidence_recall,
                "provenance_integrity": result.provenance_integrity,
                "corrupt_provenance_rejected": result.corrupt_provenance_rejected,
                "deterministic_digest": result.deterministic_digest,
                "passed": result.passed,
            }
            for result in results
        ],
    }
    report_fingerprint = sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ScaleBenchmarkReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        python_version=platform.python_version(),
        platform=platform.platform(),
        source_authority=sources.snapshot.authority,
        normalizer_authority=normalizer.snapshot.authority,
        executor_authority=executor.snapshot.authority,
        network_enabled=False,
        automatic_fetch_enabled=False,
        query_limit=QUERY_LIMIT,
        levels=results,
        certified_max_items=certified,
        status=status,
        report_fingerprint=report_fingerprint,
    )


def write_report(report: ScaleBenchmarkReport, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="ROBY XI.2 governed scale benchmark")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/quality/ADVANCED_CAPABILITY_3A_SCALE_BENCHMARK.json"),
    )
    parser.add_argument("--levels", nargs="*", type=int, default=list(DEFAULT_LEVELS))
    args = parser.parse_args()
    report = run_benchmark(tuple(args.levels))
    write_report(report, args.output)
    print(args.output)
    print(f"status={report.status} certified_max_items={report.certified_max_items}")
    return 0 if report.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
