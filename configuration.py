"""Per-installation settings; paths are relative to the configuration file."""
import json
import math
import os
from pathlib import Path
from urllib.parse import urlsplit

import psutil

ROOT = Path(__file__).resolve().parent
DEFAULT_URL = "http://127.0.0.1:8035"
DEFAULT_CONTEXT_LENGTH = 4096
GIB = 1024 ** 3


def server_url(value):
    value = value.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("server_url must be an http:// or https:// server address.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError("Use a server origin without credentials, a path, query, or fragment.")
    _ = parsed.port
    return value


def load_config(path=None):
    explicit = path or os.environ.get("COMFYUI_DRAMA3_CONFIG")
    path = Path(explicit or ROOT / "config.json").expanduser().resolve()
    if explicit and not path.is_file():
        raise FileNotFoundError(f"Drama3 configuration does not exist: {path}")
    config = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}
    if not isinstance(config, dict):
        raise ValueError("Drama3 config.json must contain an object.")
    config.setdefault("mode", "external")
    if config["mode"] not in {"external", "managed"}:
        raise ValueError("mode must be external or managed.")
    config["server_url"] = server_url(config.get("server_url", DEFAULT_URL))
    config["_path"] = str(path)
    return config


def resolve_path(config, value):
    path = Path(os.path.expandvars(str(value))).expanduser()
    return (path if path.is_absolute() else Path(config["_path"]).parent / path).resolve()


def state_directory(config):
    return resolve_path(config, config.get("state_dir", ".runtime"))


def memory_limits(config, total_bytes=None):
    total_gib = (total_bytes or psutil.virtual_memory().total) / GIB
    options = config.get("memory", {})
    working_set = options.get("working_set_gib", "auto")
    if working_set == "auto":
        working_set = min(8.0, max(2.0, round(total_gib) / 8))
    values = {
        "working_set_gib": working_set,
        "private_limit_gib": options.get("private_limit_gib", max(10, float(working_set) + 6)),
        "min_available_gib": options.get("min_available_gib", 3 if total_gib >= 24 else 2),
        "max_rss_gib": options.get("max_rss_gib", float(working_set) + 4),
    }
    values = {name: float(value) for name, value in values.items()}
    if any(not math.isfinite(value) or value <= 0 for value in values.values()):
        raise ValueError("Memory limits must be finite positive GiB values.")
    if values["working_set_gib"] > values["private_limit_gib"]:
        raise ValueError("working_set_gib cannot exceed private_limit_gib.")
    return values


def managed_server_config(config):
    url = urlsplit(config["server_url"])
    if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Managed servers must use http://127.0.0.1:<port> or http://localhost:<port>.")
    for field in ("executable", "model_path"):
        if not config.get(field):
            raise ValueError(f"Set {field} in config.json before using managed mode.")
        if not resolve_path(config, config[field]).is_file():
            raise FileNotFoundError(f"{field}: {resolve_path(config, config[field])}")
    model = resolve_path(config, config["model_path"])
    if model.suffix.lower() != ".gguf":
        raise ValueError("model_path must point to a Drama3 audio.cpp .gguf package.")
    backend = config.get("backend", "cuda")
    if backend not in {"cuda", "cpu", "vulkan", "metal"}:
        raise ValueError("backend must be cuda, cpu, vulkan, or metal, supported by your audio.cpp build.")
    run_mode = config.get("run_mode", "offline")
    if run_mode not in {"offline", "streaming"}:
        raise ValueError("run_mode must be offline or streaming, supported by your audio.cpp model.")
    threads = int(config.get("threads", 0))
    if threads == 0:
        threads = min(8, psutil.cpu_count(logical=False) or 1)
    if threads < 1:
        raise ValueError("threads must be zero (automatic) or a positive integer.")
    session = {
        "fish_drama3.disk_experts": True,
        "fish_drama3.pin_experts": False,
        "fish_drama3.expert_cache_size": 8,
        "fish_drama3.cpu_expert_layers": 0,
        "fish_drama3.context_length": DEFAULT_CONTEXT_LENGTH,
        "fish_drama3.codec_backend": "same",
        "fish_drama3.backbone_prefill_cache_mb": 0,
        "fish_drama3.tower_prefill_cache_mb": 0,
    }
    session.update(config.get("session_options", {}))
    return {
        "host": "127.0.0.1", "port": url.port or 80, "backend": backend,
        "device": int(config.get("device", 0)), "threads": threads,
        "lazy_load": True, "max_loaded_models": 1, "idle_unload_ms": 60000, "ui": True,
        "model_spec_override": str(ROOT / "specs" / "fish_drama3.json"),
        "models": [{"id": config.get("model_id", "drama3"), "family": "fish_drama3",
                    "path": str(model), "task": "tts", "mode": run_mode,
                    "session_options": session,
                    "default_request_options": {"temperature": 1.0, "top_p": 0.9, "top_k": 30, "seed": 123}}],
    }
