"""Assemble data/course.json + data/lessons/*.json from content/*.py.

Run:  python tools/build_course.py
Exits non-zero if any lesson fails the structural checks.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LEVELS = [
    ("beginner", "Beginner", "From your first line of code to your first small program."),
    ("intermediate", "Intermediate", "Collections, your own types, and programs that span files."),
    ("advanced", "Advanced", "Ownership, errors, templates and the tools real projects need."),
    ("expert", "Expert Track", "C++20 features, threads, measurement and a tested capstone."),
]

REQUIRED = ["id", "level", "title", "minutes", "goal", "explain", "example",
            "predict", "quiz", "activity", "mistake", "recap"]


def check(lesson: dict, problems: list[str]) -> None:
    lid = lesson.get("id", "<no id>")
    for key in REQUIRED:
        if key not in lesson:
            problems.append(f"{lid}: missing field '{key}'")
    if problems and any(p.startswith(lid) for p in problems):
        return

    if not 3 <= len(lesson["quiz"]) <= 5:
        problems.append(f"{lid}: quiz has {len(lesson['quiz'])} questions, need 3-5")
    for i, q in enumerate(lesson["quiz"]):
        if len(q.get("options", [])) < 2:
            problems.append(f"{lid}: quiz {i} has fewer than 2 options")
        elif not 0 <= q.get("answer", -1) < len(q["options"]):
            problems.append(f"{lid}: quiz {i} answer index out of range")
        if not q.get("why"):
            problems.append(f"{lid}: quiz {i} has no explanation")

    p = lesson["predict"]
    if not p.get("options") or not 0 <= p.get("answer", -1) < len(p["options"]):
        problems.append(f"{lid}: predict answer index out of range")
    if not p.get("why"):
        problems.append(f"{lid}: predict has no explanation")

    ex = lesson["example"]
    for key in ("code", "output", "notes"):
        if not ex.get(key):
            problems.append(f"{lid}: example missing '{key}'")
    if "int main" not in ex.get("code", ""):
        problems.append(f"{lid}: example is not a complete program")

    act = lesson["activity"]
    for key in ("goal", "starter", "expected", "hints", "solution"):
        if not act.get(key):
            problems.append(f"{lid}: activity missing '{key}'")
    if len(act.get("hints", [])) < 2:
        problems.append(f"{lid}: activity needs at least 2 hints")
    if "int main" not in act.get("starter", ""):
        problems.append(f"{lid}: starter is not a complete program")

    if not isinstance(lesson["explain"], list) or len(lesson["explain"]) < 2:
        problems.append(f"{lid}: explain should be 2+ paragraphs")


def main() -> int:
    problems: list[str] = []
    index = []
    all_ids = set()

    out_dir = ROOT / "data" / "lessons"
    out_dir.mkdir(parents=True, exist_ok=True)

    for level_id, name, blurb in LEVELS:
        module_path = ROOT / "content" / f"{level_id}.py"
        if not module_path.is_file():
            print(f"  {level_id}: no content file yet, skipping")
            continue
        module = importlib.import_module(f"content.{level_id}")
        lessons = list(module.LESSONS)
        print(f"  {level_id}: {len(lessons)} lessons")

        for lesson in lessons:
            check(lesson, problems)
            if lesson["id"] in all_ids:
                problems.append(f"{lesson['id']}: duplicate id")
            all_ids.add(lesson["id"])
            index.append({
                "id": lesson["id"], "level": level_id, "title": lesson["title"],
                "minutes": lesson["minutes"], "tags": lesson.get("tags", []),
                "goal": lesson["goal"],
            })

        (out_dir / f"{level_id}.json").write_text(
            json.dumps({"level": level_id, "name": name, "lessons": lessons},
                       indent=1, ensure_ascii=False), encoding="utf-8")

    levels_out = []
    for level_id, name, blurb in LEVELS:
        ids = [i["id"] for i in index if i["level"] == level_id]
        if ids:
            levels_out.append({"id": level_id, "name": name, "blurb": blurb,
                               "lessons": ids})

    course = {
        "title": "C++ Lab",
        "subtitle": "A hands-on C++ course: read, predict, run, test.",
        "standard": "C++20",
        "levels": levels_out,
        "lessons": index,
        "counts": {lvl["id"]: len(lvl["lessons"]) for lvl in levels_out},
        "total": len(index),
    }
    (ROOT / "data" / "course.json").write_text(
        json.dumps(course, indent=1, ensure_ascii=False), encoding="utf-8")

    # the hosted build serves everything from web/, so keep a copy there too
    web_data = ROOT / "web" / "data"
    (web_data / "lessons").mkdir(parents=True, exist_ok=True)
    (web_data / "course.json").write_text(
        (ROOT / "data" / "course.json").read_text(encoding="utf-8"), encoding="utf-8")
    for f in (out_dir).glob("*.json"):
        (web_data / "lessons" / f.name).write_text(
            f.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"  copied data -> web/data ({len(list(out_dir.glob('*.json')))} level files)")

    print(f"\ntotal lessons: {len(index)}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("structure: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
