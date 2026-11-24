"""
Compile and run one learner program, with limits.

This is a local, single-user runner. It is NOT a hardened sandbox: it protects
the host from runaway loops, accidental output floods and runaway memory, but
it does not block file or network access. Run the server bound to 127.0.0.1,
and use a container if you ever expose it to a network you do not control.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPILE_TIMEOUT = 20.0
RUN_TIMEOUT = 5.0
MAX_OUTPUT = 20_000
MAX_SOURCE = 64 * 1024
MEMORY_LIMIT = 512 * 1024 * 1024


# --------------------------------------------------------------------------
# compiler discovery
# --------------------------------------------------------------------------
def find_compiler() -> str | None:
    env = os.environ.get("CPP_LAB_GXX")
    if env and Path(env).is_file():
        return env
    for candidate in sorted((ROOT / "tools").rglob("g++.exe")):
        return str(candidate)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        candidate = Path(directory) / "g++.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def compiler_version(gxx: str | None) -> str | None:
    if not gxx:
        return None
    try:
        out = subprocess.run([gxx, "--version"], capture_output=True, text=True,
                             timeout=15, encoding="utf-8", errors="replace")
        return out.stdout.splitlines()[0].strip() if out.stdout else None
    except Exception:
        return None


# --------------------------------------------------------------------------
# windows job object: hard memory ceiling, killed when the handle closes
# --------------------------------------------------------------------------
class _MemoryJob:
    def __init__(self, limit_bytes: int):
        self.handle = None
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            self.handle = kernel32.CreateJobObjectW(None, None)
            if not self.handle:
                return

            class IO_COUNTERS(ctypes.Structure):
                _fields_ = [(n, ctypes.c_ulonglong) for n in (
                    "ReadOperationCount", "WriteOperationCount",
                    "OtherOperationCount", "ReadTransferCount",
                    "WriteTransferCount", "OtherTransferCount")]

            class BASIC(ctypes.Structure):
                _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                            ("PerJobUserTimeLimit", ctypes.c_int64),
                            ("LimitFlags", ctypes.c_uint32),
                            ("MinimumWorkingSetSize", ctypes.c_size_t),
                            ("MaximumWorkingSetSize", ctypes.c_size_t),
                            ("ActiveProcessLimit", ctypes.c_uint32),
                            ("Affinity", ctypes.c_size_t),
                            ("PriorityClass", ctypes.c_uint32),
                            ("SchedulingClass", ctypes.c_uint32)]

            class EXTENDED(ctypes.Structure):
                _fields_ = [("BasicLimitInformation", BASIC),
                            ("IoInfo", IO_COUNTERS),
                            ("ProcessMemoryLimit", ctypes.c_size_t),
                            ("JobMemoryLimit", ctypes.c_size_t),
                            ("PeakProcessMemoryUsed", ctypes.c_size_t),
                            ("PeakJobMemoryUsed", ctypes.c_size_t)]

            info = EXTENDED()
            JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
            JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
            info.BasicLimitInformation.LimitFlags = (
                JOB_OBJECT_LIMIT_PROCESS_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
            info.ProcessMemoryLimit = limit_bytes
            self._kernel32 = kernel32
            ok = kernel32.SetInformationJobObject(
                self.handle, 9, ctypes.byref(info), ctypes.sizeof(info))
            if not ok:
                kernel32.CloseHandle(self.handle)
                self.handle = None
        except Exception:
            self.handle = None

    def assign(self, pid: int) -> None:
        if not self.handle:
            return
        try:
            PROCESS_SET_QUOTA, PROCESS_TERMINATE = 0x0100, 0x0001
            h = self._kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid)
            if h:
                self._kernel32.AssignProcessToJobObject(self.handle, h)
                self._kernel32.CloseHandle(h)
        except Exception:
            pass

    def close(self) -> None:
        if self.handle:
            try:
                self._kernel32.CloseHandle(self.handle)
            except Exception:
                pass
            self.handle = None


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------
def _cap(text: str, limit: int = MAX_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    head = text[:limit]
    return head + f"\n... output stopped at {limit} characters ..."


def _clean_text(text: str, workdir: Path) -> str:
    """Strip the throwaway folder so messages read 'main.cpp:3:5: error: ...'."""
    if not text:
        return text
    cleaned = text.replace(str(workdir) + os.sep, "").replace(str(workdir), "")
    return cleaned


def run_cpp(code: str, stdin_text: str = "") -> dict:
    """Compile and run `code`. Returns a dict describing what happened."""
    result = {
        "ok": False, "phase": "setup", "stdout": "", "stderr": "",
        "exit": None, "compile_ms": 0, "run_ms": 0, "compiler": None,
        "message": "", "truncated": False,
    }

    if not isinstance(code, str) or not code.strip():
        result["message"] = "No code was sent."
        return result
    if len(code) > MAX_SOURCE:
        result["message"] = f"Program is too long ({len(code)} characters, limit {MAX_SOURCE})."
        return result

    gxx = find_compiler()
    result["compiler"] = compiler_version(gxx)
    if not gxx:
        result["phase"] = "no-compiler"
        result["message"] = ("No C++ compiler found. Put a MinGW toolchain under "
                             "C++/tools/ or set CPP_LAB_GXX to g++.exe.")
        return result

    workdir = Path(tempfile.mkdtemp(prefix="cpplab-"))
    try:
        src = workdir / "main.cpp"
        exe = workdir / "main.exe"
        src.write_text(code, encoding="utf-8")

        # ---- compile
        result["phase"] = "compile"
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                [gxx, "-std=c++20", "-O1", "-pipe", "-Wall", "-Wextra",
                 "-fdiagnostics-color=never", str(src), "-o", str(exe), "-static-libstdc++",
                 "-static-libgcc"],
                capture_output=True, text=True, timeout=COMPILE_TIMEOUT,
                encoding="utf-8", errors="replace", cwd=str(workdir))
        except subprocess.TimeoutExpired:
            result["compile_ms"] = int((time.perf_counter() - started) * 1000)
            result["message"] = "Compilation took too long and was stopped."
            return result
        result["compile_ms"] = int((time.perf_counter() - started) * 1000)
        if proc.returncode != 0:
            result["stderr"] = _cap(_clean_text(proc.stderr.strip(), workdir))
            result["exit"] = proc.returncode
            result["message"] = "The compiler found a problem. Read the first error line."
            return result
        if proc.stderr.strip():
            result["warnings"] = _cap(_clean_text(proc.stderr.strip(), workdir))

        # ---- run
        result["phase"] = "run"
        started = time.perf_counter()
        job = _MemoryJob(MEMORY_LIMIT)
        try:
            child = subprocess.Popen(
                [str(exe)], cwd=str(workdir), stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            job.assign(child.pid)
            try:
                out, err = child.communicate(stdin_text, timeout=RUN_TIMEOUT)
            except subprocess.TimeoutExpired:
                child.kill()
                out, err = child.communicate()
                result["run_ms"] = int((time.perf_counter() - started) * 1000)
                result["stdout"] = _cap(out or "")
                result["stderr"] = _cap(err or "")
                result["message"] = (f"Still running after {RUN_TIMEOUT:.0f} s, so it was "
                                     "stopped. Look for a loop that never ends.")
                return result
        finally:
            job.close()

        result["run_ms"] = int((time.perf_counter() - started) * 1000)
        stdout = out or ""
        result["truncated"] = len(stdout) > MAX_OUTPUT
        result["stdout"] = _cap(stdout)
        result["stderr"] = _cap(_clean_text((err or "").strip(), workdir))
        result["exit"] = child.returncode
        result["ok"] = child.returncode == 0
        if not result["ok"] and not result["message"]:
            result["message"] = f"The program exited with code {child.returncode}."
        return result
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
