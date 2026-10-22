"""Read-only installation checks. Does not download, start servers or generate audio."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import sys

from asr_backend import find_backend
from install_workflows import comfy_root


def check_workflow(path):
    workflow = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    issues = []
    for node in workflow.get("nodes", []):
        kind = node.get("type")
        values = node.get("widgets_values", [])
        if kind in {"Drama3GGUFGenerate", "Drama3GGUFClone"} and len(values) >= 10 and values[-1] != 4097:
            issues.append(f"Node {node['id']}: saved Top K={values[-1]}; use 4097 for the reproduced silence issue.")
        if kind in {"Qwen3ASRLoader", "Qwen3ASRTranscribe", "Drama3Qwen3ASRLoader", "Drama3Qwen3ASRTranscribe"}:
            issues.append(f"Node {node['id']}: old ASR ID {kind}; open the 0.2.2 automatic-transcription example.")
    return issues


def converted_asr_file(path):
    with Path(path).open("rb") as handle:
        size = struct.unpack("<Q", handle.read(8))[0]
        if size > 16 * 1024 * 1024:
            return False
        header = json.loads(handle.read(size))
    return "qwen3_asr_config" in header.get("__metadata__", {})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config")
    parser.add_argument("--comfy-root")
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--asr-model", type=Path, help="Check optional converted ASR file and native source")
    parser.add_argument("--probe-server", action="store_true", help="Explicitly request GET /v1/models; no generation")
    args = parser.parse_args()
    errors = []
    print(f"Python: {sys.executable}")
    for dependency in ("requests", "soundfile", "psutil", "numpy", "torch"):
        if importlib.util.find_spec(dependency) is None:
            errors.append(f"Missing {dependency}; run in the Python environment that launches ComfyUI.")
    if errors:
        for error in errors:
            print(f"CHECK: {error}")
        return 1
    from configuration import load_config, managed_server_config, resolve_path
    try:
        config = load_config(args.config)
        print(f"Config: {config['_path']} ({config['mode']})")
        if config["mode"] == "managed":
            native = managed_server_config(config)
            model = Path(native["models"][0]["path"])
            with model.open("rb") as handle:
                if handle.read(4) != b"GGUF":
                    errors.append("TTS model is not a GGUF file (check for an incomplete download).")
            print(f"Backend: {native['backend']}; TTS package: {model}")
        else:
            print(f"External server: {config['server_url']} (install backend/model on that server)")
        if args.asr_model:
            installation = comfy_root(args.comfy_root)
            override = resolve_path(config, config["asr_backend_path"]) if config.get("asr_backend_path") else None
            source = find_backend([installation / "custom_nodes"], override)
            print(f"ASR source: {source}")
            if not converted_asr_file(args.asr_model):
                errors.append("ASR file lacks converted qwen3_asr_config metadata; a raw Hugging Face folder is different.")
            print(f"ASR file: {args.asr_model}")
        if args.probe_server:
            import requests
            try:
                response = requests.get(config["server_url"] + "/v1/models", timeout=10)
                response.raise_for_status()
                models = response.json()
                entries = models.get("data", models.get("models", []))
                if not any(entry.get("family") == "fish_drama3" for entry in entries):
                    errors.append("Server does not advertise a fish_drama3 model.")
                print(f"Server models: {entries}")
            except requests.RequestException as error:
                errors.append(f"Server probe failed: {error}")
    except (OSError, ValueError, KeyError, struct.error, ImportError) as error:
        errors.append(str(error))
    if args.workflow:
        try:
            errors.extend(check_workflow(args.workflow))
        except (OSError, ValueError) as error:
            errors.append(f"Workflow check failed: {error}")
    for error in errors:
        print(f"CHECK: {error}")
    if errors:
        return 1
    print("Checks passed for the requested scope. Listen to a generated take to verify speech; hardware/quality are not certified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
