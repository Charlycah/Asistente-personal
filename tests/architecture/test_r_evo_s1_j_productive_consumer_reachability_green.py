from __future__ import annotations

from app.explicit_multisource_productive_consumer_reachability_adapter import (
    ExplicitMultisourceProductiveConsumerReachabilityAdapterV1,
)
from app.explicit_multisource_productive_continuity_adapter import (
    ExplicitMultisourceProductiveContinuityAdapterV1,
)


class _Consumer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def consume(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return kwargs["result"]


def test_s1_j_delivers_exact_f4_lineage_and_result_to_supplied_consumer() -> None:
    result = object()
    continuity = ExplicitMultisourceProductiveContinuityAdapterV1().project(
        owner="owner",
        session_id="session",
        turn_id="turn",
        result=result,  # type: ignore[arg-type]
    )
    consumer = _Consumer()

    returned = ExplicitMultisourceProductiveConsumerReachabilityAdapterV1().deliver(
        continuity=continuity,
        consumer=consumer,
    )

    assert returned is result
    assert consumer.calls == [
        {
            "owner": "owner",
            "session_id": "session",
            "turn_id": "turn",
            "result": result,
        }
    ]
