"""Start or stop this installation's managed audio.cpp server."""
import argparse
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import socket
import time
import urllib.error
import urllib.request
import webbrowser
from urllib.parse import urlsplit

import psutil

from configuration import GIB, load_config, managed_server_config, memory_limits, resolve_path, state_directory


class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                ("flags", wintypes.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t),
                ("process_count", wintypes.DWORD), ("affinity", ctypes.c_size_t),
                ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]


class IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IoCounters), ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]


class WindowsMemoryJob:
    def __init__(self, child, limits):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.SetProcessWorkingSetSizeEx.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t, wintypes.DWORD]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        info = ExtendedLimits()
        info.basic.flags = 0x100 | 0x2000  # private-memory limit; kill on job close
        info.process_memory = int(limits["private_limit_gib"] * GIB)
        child_handle = wintypes.HANDLE(int(child._handle))
        try:
            if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            if not self.kernel.AssignProcessToJobObject(self.handle, child_handle):
                raise ctypes.WinError(ctypes.get_last_error())
            if not self.kernel.SetProcessWorkingSetSizeEx(child_handle, 64 * 1024 ** 2,
                                                          int(limits["working_set_gib"] * GIB), 0x6):
                raise ctypes.WinError(ctypes.get_last_error())
        except Exception:
            self.close()
            raise

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


@contextmanager
def launcher_lock(path):
    with path.open("a+b") as handle:
        if path.stat().st_size == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def save_status(path, state):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(path)


def ready(url, model_id):
    try:
        with urllib.request.urlopen(url + "/v1/models", timeout=1) as response:
            body = json.load(response)
        return any(entry.get("id") == model_id for entry in body.get("data", body.get("models", [])))
    except (OSError, ValueError):
        return False


def stop_server(directory):
    path = directory / "server_status.json"
    if not path.is_file():
        print("No managed server status found.")
        return
    state = json.loads(path.read_text(encoding="utf-8"))
    try:
        process = psutil.Process(state["pid"])
        same_start = abs(process.create_time() - state["create_time"]) < 0.01
        same_executable = Path(process.exe()).resolve() == Path(state["executable"]).resolve()
        same_config = str(directory / "server.json") in process.cmdline()
        if same_start and same_executable and same_config:
            process.terminate()
            process.wait(timeout=15)
            print("Managed Drama3 server stopped.")
        else:
            raise RuntimeError("PID ownership does not match this installation; no process was stopped.")
    except psutil.NoSuchProcess:
        print("Managed server is already stopped.")


def run(config, directory, open_browser=False):
    if config["mode"] != "managed":
        raise ValueError("Set mode to managed and configure executable/model_path first.")
    native_config = managed_server_config(config)
    limits = memory_limits(config)
    if psutil.virtual_memory().available < (limits["min_available_gib"] + 1) * GIB:
        raise RuntimeError("Not enough available system RAM to start safely. Close memory-heavy applications.")
    model_id = native_config["models"][0]["id"]
    target = urlsplit(config["server_url"])
    try:
        with socket.create_connection((target.hostname, target.port or 80), timeout=1):
            raise RuntimeError("Server port is already occupied. Use external mode or stop the existing server first.")
    except (ConnectionRefusedError, TimeoutError):
        pass
    server_config = directory / "server.json"
    server_config.write_text(json.dumps(native_config, indent=2), encoding="utf-8")
    executable = resolve_path(config, config["executable"])
    environment = os.environ.copy()
    library_dirs = [str(resolve_path(config, value)) for value in config.get("library_dirs", [])]
    environment["PATH"] = os.pathsep.join([str(executable.parent), *library_dirs, environment.get("PATH", "")])
    environment["GGML_CUDA_DISABLE_GRAPHS"] = "1"
    state = {"status": "starting", "url": config["server_url"], "executable": str(executable),
             "limits": limits, "peak_rss": 0, "min_available_ram": psutil.virtual_memory().available,
             "hard_limits_applied": os.name == "nt"}
    child = None
    job = None
    status_path = directory / "server_status.json"
    try:
        with (directory / "server.log").open("ab", buffering=0) as log:
            child = subprocess.Popen([str(executable), "--config", str(server_config), "--log"],
                                     cwd=directory, env=environment, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            process = psutil.Process(child.pid)
            state.update(pid=child.pid, create_time=process.create_time())
            if os.name == "nt":
                job = WindowsMemoryJob(child, limits)
            save_status(status_path, state)
            previous_save = 0.0
            opened = False
            while child.poll() is None:
                available = psutil.virtual_memory().available
                try:
                    rss = process.memory_info().rss
                except psutil.NoSuchProcess:
                    break
                state["peak_rss"] = max(state["peak_rss"], rss)
                state["min_available_ram"] = min(state["min_available_ram"], available)
                if available < limits["min_available_gib"] * GIB or rss > limits["max_rss_gib"] * GIB:
                    state.update(status="memory_guard_stopped", error="Stopped to preserve system RAM.")
                    save_status(status_path, state)
                    child.terminate()
                    break
                now = time.monotonic()
                if now - previous_save > 5:
                    if ready(config["server_url"], model_id):
                        state["status"] = "ready"
                        if open_browser and not opened:
                            webbrowser.open(config["server_url"])
                            opened = True
                    save_status(status_path, state)
                    previous_save = now
                time.sleep(0.25)
            state["exit_code"] = child.wait(timeout=15)
            if state["status"] != "memory_guard_stopped":
                state["status"] = "stopped"
            save_status(status_path, state)
    except Exception as error:
        state.update(status="error", error=str(error))
        save_status(status_path, state)
        raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
        if job is not None:
            job.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Path to per-installation config.json")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    directory = state_directory(config)
    directory.mkdir(parents=True, exist_ok=True)
    if args.stop:
        stop_server(directory)
        return
    with launcher_lock(directory / "server.lock") as acquired:
        if acquired:
            run(config, directory, args.open_browser)
        else:
            print("This installation's launcher is already running.")


if __name__ == "__main__":
    main()
