from __future__ import annotations

import json

from application.brain import build_m312_16_manual_test_bank


def main() -> None:
    bank = build_m312_16_manual_test_bank()
    print(json.dumps(bank.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
