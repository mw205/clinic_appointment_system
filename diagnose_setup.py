#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


STATUS_STYLES = {
    "PASS": Color.GREEN,
    "WARN": Color.YELLOW,
    "FAIL": Color.RED,
}


@dataclass
class CheckResult:
    status: str
    label: str
    details: str = ""
    hint: str = ""


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def exists_check(path: Path, label: str, hint: str, warn_only: bool = False) -> CheckResult:
    if path.exists():
        kind = "directory" if path.is_dir() else "file"
        return CheckResult("PASS", label, f"Found {kind}: {relative(path)}")
    status = "WARN" if warn_only else "FAIL"
    return CheckResult(status, label, f"Missing: {relative(path)}", hint)


def contains_check(path: Path, needle: str, label: str, hint: str) -> CheckResult:
    text = read_text(path)
    if text is None:
        return CheckResult("FAIL", label, f"Missing file: {relative(path)}", hint)
    if needle in text:
        return CheckResult("PASS", label, f"Found `{needle}` in {relative(path)}")
    return CheckResult("FAIL", label, f"`{needle}` not found in {relative(path)}", hint)


def parse_python_assignment(path: Path, variable_name: str):
    text = read_text(path)
    if text is None:
        return None, f"Missing file: {relative(path)}"

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return None, f"Could not parse {relative(path)}: {exc}"

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    try:
                        return ast.literal_eval(node.value), ""
                    except Exception as exc:  # pragma: no cover - defensive
                        return None, f"Could not evaluate `{variable_name}` in {relative(path)}: {exc}"
    return None, f"`{variable_name}` is not defined in {relative(path)}"


def check_gitignore() -> list[CheckResult]:
    path = ROOT / ".gitignore"
    results = [exists_check(path, "Root .gitignore exists", "Create `.gitignore` in the repo root.")]
    if not path.exists():
        return results

    results.append(
        contains_check(
            path,
            "node_modules/",
            ".gitignore ignores node_modules",
            "Add `node_modules/` to `.gitignore`.",
        )
    )
    results.append(
        contains_check(
            path,
            "__pycache__/",
            ".gitignore ignores __pycache__",
            "Add `__pycache__/` to `.gitignore`.",
        )
    )
    return results


def check_settings_installed_apps() -> CheckResult:
    path = BACKEND / "core" / "settings.py"
    value, error = parse_python_assignment(path, "INSTALLED_APPS")
    if error:
        return CheckResult(
            "FAIL",
            "Django settings include corsheaders in INSTALLED_APPS",
            error,
            "Add `'corsheaders'` to `INSTALLED_APPS` in `backend/core/settings.py`.",
        )

    if isinstance(value, (list, tuple)) and "corsheaders" in value:
        return CheckResult(
            "PASS",
            "Django settings include corsheaders in INSTALLED_APPS",
            f"Found `corsheaders` in {relative(path)}",
        )

    return CheckResult(
        "FAIL",
        "Django settings include corsheaders in INSTALLED_APPS",
        f"`corsheaders` not present in {relative(path)}",
        "Install django-cors-headers if needed, then add `'corsheaders'` to `INSTALLED_APPS`.",
    )


def check_cors_origins() -> CheckResult:
    path = BACKEND / "core" / "settings.py"
    value, error = parse_python_assignment(path, "CORS_ALLOWED_ORIGINS")
    if error:
        return CheckResult(
            "FAIL",
            "Django settings define CORS_ALLOWED_ORIGINS",
            error,
            "Define `CORS_ALLOWED_ORIGINS = [...]` in `backend/core/settings.py`.",
        )

    if isinstance(value, (list, tuple)):
        return CheckResult(
            "PASS",
            "Django settings define CORS_ALLOWED_ORIGINS",
            f"Found {len(value)} origin(s) in {relative(path)}",
        )

    return CheckResult(
        "FAIL",
        "Django settings define CORS_ALLOWED_ORIGINS",
        f"`CORS_ALLOWED_ORIGINS` exists but is not a list/tuple in {relative(path)}",
        "Set `CORS_ALLOWED_ORIGINS` to a list of allowed frontend URLs.",
    )


def parse_package_json() -> tuple[dict | None, str]:
    path = FRONTEND / "package.json"
    text = read_text(path)
    if text is None:
        return None, f"Missing file: {relative(path)}"
    try:
        return json.loads(text), ""
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in {relative(path)}: {exc}"


def check_tailwind_version() -> CheckResult:
    package_json, error = parse_package_json()
    path = FRONTEND / "package.json"
    if error:
        return CheckResult(
            "FAIL",
            "Frontend package.json uses Tailwind CSS v3",
            error,
            "Create or fix `frontend/package.json`, then add `tailwindcss` with version `^3.x.x`.",
        )

    deps = {}
    deps.update(package_json.get("dependencies", {}))
    deps.update(package_json.get("devDependencies", {}))
    version = deps.get("tailwindcss")
    if not version:
        return CheckResult(
            "FAIL",
            "Frontend package.json uses Tailwind CSS v3",
            f"`tailwindcss` is not declared in {relative(path)}",
            "Run `cd frontend && pnpm add -D tailwindcss@^3 autoprefixer postcss`.",
        )

    if re.match(r"^\^?3(\.\d+){0,2}$", version.strip()):
        return CheckResult(
            "PASS",
            "Frontend package.json uses Tailwind CSS v3",
            f"Found `tailwindcss: {version}` in {relative(path)}",
        )

    return CheckResult(
        "FAIL",
        "Frontend package.json uses Tailwind CSS v3",
        f"Expected `^3.x.x`, found `{version}` in {relative(path)}",
        "Pin Tailwind to v3, for example: `cd frontend && pnpm add -D tailwindcss@^3.4.0`.",
    )


def check_frontend_env() -> list[CheckResult]:
    path = FRONTEND / ".env"
    results = [
        exists_check(
            path,
            "Frontend .env exists",
            "Create `frontend/.env` and define `VITE_API_BASE_URL`, for example `VITE_API_BASE_URL=http://127.0.0.1:8000/api`.",
        )
    ]
    if not path.exists():
        results.append(
            CheckResult(
                "FAIL",
                "Frontend .env defines VITE_API_BASE_URL",
                f"Missing file: {relative(path)}",
                "Create `frontend/.env` with `VITE_API_BASE_URL=<backend API URL>`.",
            )
        )
        return results

    text = read_text(path) or ""
    match = re.search(r"^\s*VITE_API_BASE_URL\s*=\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if match:
        results.append(
            CheckResult(
                "PASS",
                "Frontend .env defines VITE_API_BASE_URL",
                f"Found `VITE_API_BASE_URL` in {relative(path)}",
            )
        )
    else:
        results.append(
            CheckResult(
                "FAIL",
                "Frontend .env defines VITE_API_BASE_URL",
                f"`VITE_API_BASE_URL` not found in {relative(path)}",
                "Add `VITE_API_BASE_URL=http://127.0.0.1:8000/api` to `frontend/.env`.",
            )
        )
    return results


def iter_style_files() -> Iterable[Path]:
    patterns = ("*.css", "*.pcss", "*.postcss", "*.scss", "*.sass", "*.less")
    for pattern in patterns:
        for path in FRONTEND.rglob(pattern):
            if any(part in {"node_modules", "dist", ".git"} for part in path.parts):
                continue
            yield path


def check_tailwind_directives() -> CheckResult:
    candidates = [FRONTEND / "src" / "assets" / "main.css"]
    seen = set(candidates)
    candidates.extend(path for path in iter_style_files() if path not in seen)

    for path in candidates:
        if not path.is_file():
            continue
        text = read_text(path) or ""
        directives = ["@tailwind base", "@tailwind components", "@tailwind utilities"]
        if all(directive in text for directive in directives):
            return CheckResult(
                "PASS",
                "Frontend styles include Tailwind directives",
                f"Found all directives in {relative(path)}",
            )

    preferred = FRONTEND / "src" / "assets" / "main.css"
    return CheckResult(
        "FAIL",
        "Frontend styles include Tailwind directives",
        "No stylesheet with `@tailwind base`, `@tailwind components`, and `@tailwind utilities` was found.",
        f"Add the directives to `{relative(preferred)}` or your actual global stylesheet and import it from `frontend/src/main.js`.",
    )


def section_results() -> list[tuple[str, list[CheckResult]]]:
    return [
        (
            "Root Directory Checks",
            check_gitignore()
            + [exists_check(ROOT / "README.md", "Root README.md exists", "Add a `README.md` to document setup and run steps.")],
        ),
        (
            "Backend Checks",
            [
                exists_check(
                    BACKEND / ".venv",
                    "Backend virtual environment exists",
                    "Missing `backend/.venv` - Run: `cd backend && python3 -m venv .venv`",
                ),
                exists_check(
                    BACKEND / "requirements.txt",
                    "Backend requirements.txt exists",
                    "Create `backend/requirements.txt`, for example with `cd backend && pip freeze > requirements.txt`.",
                ),
                exists_check(
                    BACKEND / ".env",
                    "Backend .env exists",
                    "Create `backend/.env` from your sample file, for example: `cp backend/.env.example backend/.env`.",
                    warn_only=True,
                ),
                exists_check(
                    BACKEND / "manage.py",
                    "Backend manage.py exists",
                    "Recreate the Django project scaffold or restore `backend/manage.py`.",
                ),
                check_settings_installed_apps(),
                check_cors_origins(),
                exists_check(
                    BACKEND / "db.sqlite3",
                    "Backend database file exists",
                    "Missing `backend/db.sqlite3` - Run: `cd backend && . .venv/bin/activate && python manage.py migrate`",
                ),
            ],
        ),
        (
            "Frontend Checks",
            [
                exists_check(
                    FRONTEND / "node_modules",
                    "Frontend dependencies installed",
                    "Missing `frontend/node_modules` - Run: `cd frontend && pnpm install`",
                ),
                *check_frontend_env(),
                exists_check(
                    FRONTEND / "tailwind.config.js",
                    "Frontend Tailwind config exists",
                    "Initialize Tailwind v3 in the frontend, for example: `cd frontend && npx tailwindcss init -p`.",
                ),
                check_tailwind_version(),
                exists_check(
                    FRONTEND / "components.json",
                    "Frontend shadcn-vue components.json exists",
                    "Initialize shadcn-vue, which typically creates `frontend/components.json`.",
                ),
                check_tailwind_directives(),
            ],
        ),
    ]


def print_section(title: str, results: list[CheckResult]) -> None:
    print(colorize(f"\n{title}", Color.BOLD + Color.CYAN))
    for result in results:
        style = STATUS_STYLES[result.status]
        status = colorize(f"[{result.status}]", style)
        print(f"{status} {result.label}")
        if result.details:
            print(f"      {result.details}")
        if result.hint:
            hint_color = Color.YELLOW if result.status == "WARN" else Color.RED
            print(f"      {colorize('Hint:', hint_color)} {result.hint}")


def summarize(all_results: list[CheckResult]) -> int:
    passed = sum(result.status == "PASS" for result in all_results)
    warnings = sum(result.status == "WARN" for result in all_results)
    failed = sum(result.status == "FAIL" for result in all_results)
    total = len(all_results)

    print(colorize("\nSummary", Color.BOLD + Color.CYAN))
    print(f"  {colorize(str(passed), Color.GREEN)} passed")
    print(f"  {colorize(str(warnings), Color.YELLOW)} warnings")
    print(f"  {colorize(str(failed), Color.RED)} failed")
    print(f"  {total} total checks")

    if failed:
        print(colorize("\nSetup check failed.", Color.RED))
        return 1
    if warnings:
        print(colorize("\nSetup check passed with warnings.", Color.YELLOW))
        return 0
    print(colorize("\nSetup check passed.", Color.GREEN))
    return 0


def main() -> int:
    if not (BACKEND.exists() and FRONTEND.exists()):
        print(colorize("Expected to run from the repository root containing `backend/` and `frontend/`.", Color.RED))
        return 1

    sections = section_results()
    all_results: list[CheckResult] = []
    print(colorize("clinic_appointment_system setup diagnostic", Color.BOLD))
    for title, results in sections:
        print_section(title, results)
        all_results.extend(results)
    return summarize(all_results)


if __name__ == "__main__":
    sys.exit(main())
