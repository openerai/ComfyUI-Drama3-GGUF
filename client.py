"""audio.cpp HTTP client. Importing this module starts no processes."""
import base64
import io
import json
import math
from numbers import Integral
from pathlib import Path
import subprocess
import sys
import time

import requests
import soundfile
import psutil
import numpy as np

from .configuration import DEFAULT_CONTEXT_LENGTH, ROOT, managed_server_config, memory_limits, resolve_path, server_url, state_directory

MAX_CONTEXT_TOKENS = 262144
AUDIO_FRAMES_PER_SECOND = 44100 / 2048
MAX_GENERATION_SECONDS = math.floor(MAX_CONTEXT_TOKENS / AUDIO_FRAMES_PER_SECOND)


def generation_frames(seconds):
    if not math.isfinite(seconds) or not 1 <= seconds <= MAX_GENERATION_SECONDS:
        raise ValueError(f"max_seconds must be finite and between 1 and {MAX_GENERATION_SECONDS}. "
                         "This is the model context bound; the server must also fit the prompt and references.")
    return math.ceil(seconds * AUDIO_FRAMES_PER_SECOND)


def context_capacity_error(max_tokens, detail):
    return RuntimeError(f"Drama3 context capacity exceeded (문맥 용량 초과). Requested generation budget: {max_tokens} frames. "
                        "Prompt, reference audio and history need additional context. Increase fish_drama3.context_length "
                        "in the server's session options (managed mode: config.json), then restart that server; "
                        "or reduce the generation budget/input. A larger context requires more memory. "
                        f"Server: {detail}")


def check_generation_capacity(config, url, max_tokens):
    if config["mode"] == "managed" and url == config["server_url"]:
        context = int(config.get("session_options", {}).get("fish_drama3.context_length", DEFAULT_CONTEXT_LENGTH))
        if max_tokens >= context:
            raise context_capacity_error(max_tokens, f"Configured context_length={context}; no model was started.")


def select_model(document, requested="auto"):
    entries = document.get("data", document.get("models", []))
    if not isinstance(entries, list):
        raise RuntimeError("The server returned an invalid model list.")
    entries = [entry for entry in entries if isinstance(entry, dict) and entry.get("id")]
    if requested and requested != "auto":
        entry = next((entry for entry in entries if entry["id"] == requested), None)
        if entry is None:
            raise RuntimeError(f"Model {requested!r} is not registered on this server.")
        if entry.get("family") not in {None, "", "fish_drama3"}:
            raise RuntimeError(f"Model {requested!r} is not a Drama3 model.")
        return requested
    candidates = [entry for entry in entries if entry.get("family") == "fish_drama3"]
    if len(candidates) != 1:
        raise RuntimeError("Set model_id explicitly: the server must expose exactly one Drama3 model for auto selection.")
    return candidates[0]["id"]


def reference_payload(audio, sample_rate, transcript, *, max_seconds=15.0):
    if not transcript.strip():
        raise ValueError("reference_text must match the words spoken in reference_audio.")
    if not isinstance(sample_rate, Integral) or sample_rate <= 0:
        raise ValueError("Reference sample_rate must be a positive integer.")
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim not in {1, 2} or not audio.size or not audio.shape[0]:
        raise ValueError("Reference audio is empty or has an invalid shape. Check the selected time range.")
    if not np.isfinite(audio).all():
        raise ValueError("Reference audio contains NaN or infinite samples.")
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    if np.max(np.abs(mono)) <= 1e-6:
        raise ValueError("Reference audio is silent. Select a section containing clear speech.")
    max_seconds = float(max_seconds)
    if not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("reference_max_seconds must be finite and positive.")
    duration = audio.shape[0] / sample_rate
    if duration > max_seconds:
        raise ValueError(f"Reference audio is {duration:.1f}s; limit is {max_seconds:g}s. Use Trim Audio Duration, or configure reference_max_seconds for your server's context capacity.")
    buffer = io.BytesIO()
    soundfile.write(buffer, audio, int(sample_rate), format="WAV", subtype="PCM_16")
    data = buffer.getvalue()
    if len(data) > 5 * 1024 ** 2:
        raise ValueError("Reference WAV exceeds audio.cpp's 5 MiB inline limit. Use a shorter reference.")
    return {"voice_ref": {"type": "base64", "data": base64.b64encode(data).decode("ascii")},
            "reference_text": transcript}


def get_models(url):
    response = requests.get(url + "/v1/models", timeout=(3, 10))
    response.raise_for_status()
    return response.json()


def verify_managed_server(config, document):
    expected = managed_server_config(config)
    directory = state_directory(config)
    try:
        state = json.loads((directory / "server_status.json").read_text(encoding="utf-8"))
        saved = json.loads((directory / "server.json").read_text(encoding="utf-8"))
        process = psutil.Process(state["pid"])
        owned = (abs(process.create_time() - state["create_time"]) < 0.01
                 and Path(process.exe()).resolve() == resolve_path(config, config["executable"])
                 and str(directory / "server.json") in process.cmdline())
        if not owned or saved != expected or state.get("limits") != memory_limits(config):
            raise ValueError("settings or process ownership differ")
        entries = document.get("data", document.get("models", []))
        model = next(entry for entry in entries if entry.get("id") == expected["models"][0]["id"])
        if (model.get("family") != "fish_drama3"
                or Path(model["path"]).resolve() != resolve_path(config, config["model_path"])):
            raise ValueError("model path differs")
    except (OSError, ValueError, KeyError, StopIteration, psutil.Error) as error:
        raise RuntimeError("This server is not using this installation's managed configuration. Stop/restart your managed server, or use external mode for an existing server.") from error


def ensure_server(config, url, interrupted=lambda: None):
    local_managed = config["mode"] == "managed" and url == config["server_url"]
    def checked_models():
        document = get_models(url)
        if local_managed:
            verify_managed_server(config, document)
        return document
    try:
        return checked_models()
    except requests.ConnectionError as error:
        if config["mode"] != "managed" or url != config["server_url"]:
            raise RuntimeError("Cannot connect to audio.cpp. Start your server or configure managed mode in config.json.") from error
    managed_server_config(config)
    state_dir = state_directory(config)
    state_dir.mkdir(parents=True, exist_ok=True)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    with (state_dir / "launcher.log").open("ab", buffering=0) as log:
        launcher = subprocess.Popen([sys.executable, str(ROOT / "run_server.py"), "--config", config["_path"]],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        interrupted()
        try:
            return checked_models()
        except requests.ConnectionError:
            pass
        except RuntimeError:
            # The native HTTP listener can become ready just before status is written.
            pass
        if launcher.poll() not in {None, 0}:
            raise RuntimeError(f"Managed launcher failed. Check {state_dir / 'launcher.log'}.")
        time.sleep(0.5)
    raise RuntimeError(f"audio.cpp did not start. Check {state_dir / 'launcher.log'} and server.log.")


def sampling_options(temperature, top_p, top_k):
    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2.")
    if not math.isfinite(top_p) or not 0 < top_p <= 1:
        raise ValueError("top_p must be greater than 0 and at most 1.")
    if not isinstance(top_k, Integral) or not 1 <= top_k <= 4096:
        raise ValueError("top_k must be an integer between 1 and 4096.")
    return {"temperature": temperature, "top_p": top_p, "top_k": top_k}


def generate(config, text, seed, max_tokens, *, url="", model_id="auto", reference=None, interrupted=lambda: None,
             temperature=1.0, top_p=0.9, top_k=30):
    sampling = sampling_options(temperature, top_p, top_k)
    if not isinstance(max_tokens, Integral) or not 1 <= max_tokens <= MAX_CONTEXT_TOKENS:
        raise ValueError(f"max_tokens must be an integer between 1 and {MAX_CONTEXT_TOKENS}.")
    request_timeout = float(config.get("request_timeout_seconds", 600))
    if not math.isfinite(request_timeout) or request_timeout < 0:
        raise ValueError("request_timeout_seconds must be finite and nonnegative; 0 disables the read timeout.")
    url = server_url(url or config["server_url"])
    check_generation_capacity(config, url, max_tokens)
    document = ensure_server(config, url, interrupted)
    model = select_model(document, model_id)
    if config["mode"] == "managed" and url == config["server_url"] and model != config.get("model_id", "drama3"):
        raise RuntimeError("Managed mode uses the model_id in config.json. Use external mode to select another registered model.")
    payload = {"model": model, "input": text, "seed": seed,
               "max_tokens": max_tokens, "response_format": "wav", **sampling}
    if reference:
        payload.update(reference)
    try:
        response = requests.post(url + "/v1/audio/speech", json=payload, timeout=(5, request_timeout or None))
    except requests.ConnectTimeout as error:
        raise RuntimeError("Drama3 server connection timed out (서버 연결 시간 초과). Check the server URL and server status.") from error
    except requests.Timeout as error:
        raise RuntimeError("Drama3 server response timed out (응답 대기 시간 초과). "
                           "For long generation, increase request_timeout_seconds in this installation's config.json, "
                           "or set it to 0 for no read timeout. The server may still be generating; check it before retrying.") from error
    except requests.ConnectionError as error:
        status_path = state_directory(config) / "server_status.json"
        if config["mode"] == "managed" and url == config["server_url"] and status_path.is_file():
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if status.get("status") == "memory_guard_stopped":
                raise RuntimeError("Drama3 stopped to preserve system RAM. Close memory-heavy applications or adjust your local memory settings.") from error
        raise RuntimeError("audio.cpp disconnected during generation. Check its server.log.") from error
    if not response.ok:
        detail = response.text[:1200]
        lowered = detail.lower()
        if "exceeds fish_drama3.context_length" in lowered:
            raise context_capacity_error(max_tokens, detail)
        if any(term in lowered for term in ("out of memory", "failed to allocate", "bad_alloc", "insufficient_memory")):
            raise RuntimeError("Drama3 memory allocation failed (메모리 부족). This server cannot fit the current model/request. "
                               "Adjust its backend, offload or context settings, or reduce the request. "
                               f"Server HTTP {response.status_code}: {detail}")
        raise RuntimeError(f"audio.cpp HTTP {response.status_code}: {detail}")
    audio, sample_rate = soundfile.read(io.BytesIO(response.content), dtype="float32", always_2d=True)
    if not audio.size:
        raise RuntimeError("audio.cpp returned empty audio.")
    return audio, sample_rate
