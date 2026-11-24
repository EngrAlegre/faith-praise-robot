"""End-to-end checks for the server and the runner.

Starts the real server on a spare port, talks to it over HTTP, and stops it.
Run:  python tests/test_api.py
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
PORT = 8899
BASE = f"http://127.0.0.1:{PORT}"

passed = 0
failed = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}" + (f"  -> {detail}" if detail else ""))


def wait_for_port(port: int, timeout: float = 25.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def post(path: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def get(path: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(BASE + path, timeout=20) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def main() -> int:
    proc = subprocess.Popen([PY, str(ROOT / "server.py"), "--port", str(PORT)],
                            cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not wait_for_port(PORT):
            print("server did not start")
            return 2

        print("server and static files")
        status, body = get("/api/health")
        health = json.loads(body)
        check("health responds", status == 200 and health.get("ok") is True)
        check("a compiler is configured", bool(health.get("compiler")), str(health.get("compiler")))

        status, body = get("/")
        check("index.html is served", status == 200 and b"C++ Lab" in body)
        status, body = get("/data/course.json")
        course = json.loads(body)
        check("course.json loads", status == 200 and course["total"] > 0)
        check("all levels present", len(course["levels"]) == 4)
        status, body = get("/styles.css")
        check("styles are served as css", status == 200 and b"--accent" in body)
        status, body = get("/auth.js")
        check("account module is served", status == 200 and b"signUp" in body)
        status, body = get("/vendor/firebase-app-compat.js")
        check("firebase sdk is vendored locally", status == 200 and b"firebase" in body.lower())

        print("\nlesson data")
        total = 0
        bad = []
        for lv in course["levels"]:
            status, body = get(f"/data/lessons/{lv['id']}.json")
            data = json.loads(body)
            total += len(data["lessons"])
            for lesson in data["lessons"]:
                if not (3 <= len(lesson["quiz"]) <= 5):
                    bad.append(f"{lesson['id']}: quiz size")
                if not lesson["activity"].get("hints"):
                    bad.append(f"{lesson['id']}: no hints")
                if "int main" not in lesson["example"]["code"]:
                    bad.append(f"{lesson['id']}: example not a program")
        check("every level file loads", status == 200)
        check("lesson count matches the index", total == course["total"], f"{total} vs {course['total']}")
        check("every lesson has a quiz and hints", not bad, "; ".join(bad[:3]))

        print("\nrunning code")
        code = '#include <iostream>\nint main(){ std::cout << "hello\\n"; }'
        status, res = post("/api/run", {"code": code})
        check("hello compiles and runs", status == 200 and res["ok"] and res["stdout"] == "hello\n",
              str(res)[:160])

        code = '#include <iostream>\nint main(){ int n{}; std::cin >> n; std::cout << n * 2 << "\\n"; }'
        status, res = post("/api/run", {"code": code, "stdin": "21\n"})
        check("stdin is passed through", res.get("stdout") == "42\n", str(res)[:160])

        code = '#include <iostream>\nint main(){ std::cout << missing; }'
        status, res = post("/api/run", {"code": code})
        check("compile errors are reported, not hidden",
              res.get("phase") == "compile" and not res.get("ok") and "missing" in res.get("stderr", ""))

        code = '#include <iostream>\nint main(){ while (true) {} }'
        started = time.time()
        status, res = post("/api/run", {"code": code})
        elapsed = time.time() - started
        check("an infinite loop is stopped", not res.get("ok") and "stopped" in res.get("message", ""),
              str(res)[:160])
        check("the stop happens near the 5 s limit", 4.0 < elapsed < 30.0, f"{elapsed:.1f}s")

        code = '#include <iostream>\nint main(){ int unused = 4; std::cout << "warned\\n"; }'
        status, res = post("/api/run", {"code": code})
        check("warnings do not block the run", res.get("ok") and res["stdout"] == "warned\n")
        check("warnings are surfaced", bool(res.get("warnings")), str(res.get("warnings"))[:80])

        status, res = post("/api/run", {"code": ""})
        check("empty code is refused", status == 400 or res.get("ok") is False)

        big = "#include <iostream>\n" + "// filler\n" * 12000 + "int main(){}"
        status, res = post("/api/run", {"code": big})
        check("oversized programs are refused", status == 413 or not res.get("ok"))

        print("\nsafety")
        status, body = get("/data/../server.py")
        check("path traversal is blocked", status in (403, 404), f"status {status}")
        status, body = get("/../server.py")
        check("traversal from the web root is blocked", status in (403, 404), f"status {status}")
        status, res = post("/api/nope", {})
        check("unknown endpoints 404", status == 404)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
