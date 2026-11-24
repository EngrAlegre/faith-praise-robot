"""Compile and run every example and every activity solution.

This is the check that stops the course from teaching something that does not
build. It uses the same runner the app uses, so a lesson passing here means the
Run button will behave the same way.

Run:  python tools/verify_lessons.py            (all lessons)
      python tools/verify_lessons.py b01 i04    (just these)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import runner


def normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip("\n")


def compare(got: str, want: str) -> tuple[bool, str]:
    g, w = normalise(got), normalise(want)
    if g == w:
        return True, ""
    g_lines, w_lines = g.split("\n"), w.split("\n")
    for i in range(max(len(g_lines), len(w_lines))):
        gl = g_lines[i] if i < len(g_lines) else "<no line>"
        wl = w_lines[i] if i < len(w_lines) else "<no line>"
        if gl != wl:
            return False, f"line {i + 1}: want {wl!r}, got {gl!r}"
    return False, "differs"


def main(argv: list[str]) -> int:
    wanted = set(argv)
    gxx = runner.find_compiler()
    print(f"compiler: {runner.compiler_version(gxx) or 'NOT FOUND'}")
    if not gxx:
        print("no compiler available - cannot verify")
        return 2

    lessons_dir = ROOT / "data" / "lessons"
    failures = 0
    checked = 0

    for path in sorted(lessons_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for lesson in data["lessons"]:
            if wanted and lesson["id"] not in wanted:
                continue
            checked += 1
            lid = lesson["id"]

            # ---- example must compile and print exactly what it claims
            ex = lesson["example"]
            res = runner.run_cpp(ex["code"], ex.get("stdin", ""))
            if not res["ok"]:
                failures += 1
                print(f"FAIL {lid} example: {res['phase']}")
                print("     " + (res.get("stderr") or res.get("message", "")).split("\n")[0])
            else:
                ok, why = compare(res["stdout"], ex["output"])
                if not ok:
                    failures += 1
                    print(f"FAIL {lid} example output: {why}")

            # ---- starter must compile (it is handed to learners as-is)
            act = lesson["activity"]
            res = runner.run_cpp(act["starter"], act.get("stdin", ""))
            if not res["ok"] and res["phase"] == "compile":
                failures += 1
                print(f"FAIL {lid} starter does not compile")
                print("     " + (res.get("stderr") or "").split("\n")[0])

            # ---- solution must compile and hit the expected output
            res = runner.run_cpp(act["solution"], act.get("stdin", ""))
            if not res["ok"]:
                failures += 1
                print(f"FAIL {lid} solution: {res['phase']}")
                print("     " + (res.get("stderr") or res.get("message", "")).split("\n")[0])
            else:
                ok, why = compare(res["stdout"], act["expected"])
                if not ok:
                    failures += 1
                    print(f"FAIL {lid} solution output: {why}")

            if failures == 0 or lid not in str(failures):
                pass

    print(f"\nchecked {checked} lessons, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
