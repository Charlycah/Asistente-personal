from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "quality" / "M361_QUALITY_BASELINE.json"
PRODUCTION_ROOTS = (
    "app",
    "application",
    "core",
    "domain",
    "handlers",
    "infrastructure",
    "interfaces",
    "m6",
)
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "venv",
    "venv_old",
    ".venv",
}


def _python_files(root_names: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for root_name in root_names:
        root = ROOT / root_name
        if not root.exists():
            continue
        files.extend(
            path
            for path in root.rglob("*.py")
            if not EXCLUDED_PARTS.intersection(path.parts)
        )
    return sorted(files)


def _non_empty_lines(path: Path) -> int:
    return sum(
        1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


def _node_length(node: ast.AST) -> int:
    start = getattr(node, "lineno", 0)
    end = getattr(node, "end_lineno", start)
    return max(0, end - start + 1)


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _analyze(files: list[Path]) -> dict[str, object]:
    broad_exceptions = 0
    bare_exceptions = 0
    imports = Counter()
    functions: list[dict[str, object]] = []
    classes: list[dict[str, object]] = []
    modules: list[dict[str, object]] = []
    syntax_errors: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        non_empty = sum(1 for line in text.splitlines() if line.strip())
        modules.append({"path": _relative(path), "non_empty_lines": non_empty})
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            syntax_errors.append(_relative(path))
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(
                    {
                        "path": _relative(path),
                        "name": node.name,
                        "line": node.lineno,
                        "length": _node_length(node),
                    }
                )
            elif isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "path": _relative(path),
                        "name": node.name,
                        "line": node.lineno,
                        "length": _node_length(node),
                    }
                )
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    bare_exceptions += 1
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    broad_exceptions += 1
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.name.split(".")[0]] += 1
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports[node.module.split(".")[0]] += 1

    modules.sort(key=lambda item: (-int(item["non_empty_lines"]), str(item["path"])))
    functions.sort(
        key=lambda item: (-int(item["length"]), str(item["path"]), int(item["line"]))
    )
    classes.sort(
        key=lambda item: (-int(item["length"]), str(item["path"]), int(item["line"]))
    )

    return {
        "module_count": len(files),
        "non_empty_lines": sum(_non_empty_lines(path) for path in files),
        "function_count": len(functions),
        "class_count": len(classes),
        "broad_exception_handlers": broad_exceptions,
        "bare_exception_handlers": bare_exceptions,
        "syntax_errors": syntax_errors,
        "largest_modules": modules[:20],
        "longest_functions": functions[:20],
        "longest_classes": classes[:20],
        "most_imported_roots": [
            {"name": name, "count": count} for name, count in imports.most_common(20)
        ],
    }


def build_baseline() -> dict[str, object]:
    production_files = _python_files(PRODUCTION_ROOTS)
    test_files = _python_files(("tests",))
    production = _analyze(production_files)
    tests = _analyze(test_files)
    production_lines = int(production["non_empty_lines"])
    test_lines = int(tests["non_empty_lines"])

    return {
        "schema_version": 1,
        "milestone": "M361",
        "canonical_predecessor": "M360.0.e",
        "verified_predecessor_tests": 8677,
        "scope": "static_repository_baseline",
        "production_roots": list(PRODUCTION_ROOTS),
        "production": production,
        "tests": tests,
        "ratios": {
            "test_to_production_non_empty_lines": round(
                test_lines / production_lines, 4
            )
            if production_lines
            else 0.0,
            "test_modules_per_production_module": round(
                int(tests["module_count"]) / int(production["module_count"]), 4
            )
            if int(production["module_count"])
            else 0.0,
        },
        "thresholds": {
            "review_function_length": 100,
            "review_class_length": 300,
            "review_module_non_empty_lines": 500,
            "new_bare_exception_handlers_allowed": 0,
        },
    }


def main() -> None:
    baseline = build_baseline()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(baseline, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
