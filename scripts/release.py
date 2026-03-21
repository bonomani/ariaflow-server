#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
import glob


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_INIT = ROOT / "src" / "aria_queue" / "__init__.py"


def read_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
    if not match:
        raise SystemExit("Could not find project version in pyproject.toml")
    return match.group(1)


def alpha_to_tag(version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)a(\d+)", version)
    if not match:
        raise SystemExit(f"Unsupported version format: {version!r}")
    base, alpha = match.groups()
    return f"v{base}-alpha.{alpha}"


def bump_alpha(version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)a(\d+)", version)
    if not match:
        raise SystemExit(f"Unsupported version format: {version!r}")
    base, alpha = match.groups()
    return f"{base}a{int(alpha) + 1}"


def write_version(version: str) -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    pyproject = re.sub(r'^version = "[^"]+"$', f'version = "{version}"', pyproject, flags=re.MULTILINE)
    PYPROJECT.write_text(pyproject, encoding="utf-8")

    init_py = PACKAGE_INIT.read_text(encoding="utf-8")
    init_py = re.sub(r'^__version__ = "[^"]+"$', f'__version__ = "{version}"', init_py, flags=re.MULTILINE)
    PACKAGE_INIT.write_text(init_py, encoding="utf-8")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def run_py_compile() -> None:
    files = sorted(glob.glob(str(ROOT / "src" / "aria_queue" / "*.py"))) + sorted(glob.glob(str(ROOT / "tests" / "*.py")))
    run(["python3", "-m", "py_compile", *files])


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump ariaflow, tag a prerelease, and push it.")
    parser.add_argument("--version", help="Set an explicit package version like 0.1.1a24.")
    parser.add_argument("--next-alpha", action="store_true", help="Auto-bump the current alpha version by one.")
    parser.add_argument("--no-tests", action="store_true", help="Skip local tests before committing.")
    parser.add_argument("--push", action="store_true", help="Push master and tags after committing.")
    args = parser.parse_args()

    current = read_version()
    if args.version and args.next_alpha:
        raise SystemExit("Use either --version or --next-alpha, not both.")

    next_version = args.version or (bump_alpha(current) if args.next_alpha else None)
    if not next_version:
        raise SystemExit("Provide --version or --next-alpha.")

    tag = alpha_to_tag(next_version)

    if not args.no_tests:
        run_py_compile()
        run(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"])

    write_version(next_version)
    run(["git", "add", "pyproject.toml", "src/aria_queue/__init__.py"])
    alpha = tag.split(".")[-1]
    run(["git", "commit", "-m", f"Bump version for alpha {alpha}"])
    run(["git", "tag", tag])

    if args.push:
        run(["git", "push", "origin", "master", "--tags"])
    else:
        print(f"Tagged {tag}. Push with: git push origin master --tags")

    print(f"Next release tag: {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
