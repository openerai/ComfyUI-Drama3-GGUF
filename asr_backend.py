"""Load the optional native ASR implementation without registering its ComfyUI nodes."""
from functools import lru_cache
import hashlib
import importlib
import importlib.util
from pathlib import Path
import sys

ASR_BACKEND_COMMIT = "67a733a96890637dc27b1914974ad00c569405fb"
ASR_BACKEND_URL = "https://github.com/PedroMarinhoDev/ComfyUI-Drama3"


def find_backend(custom_node_roots, override=None):
    candidates = [Path(override)] if override else [Path(root) / "ComfyUI-Drama3" for root in custom_node_roots]
    for candidate in candidates:
        package = candidate / "qwen3_asr"
        if (package / "__init__.py").is_file() and (package / "asr.py").is_file():
            return package.resolve()
    raise FileNotFoundError(
        "Automatic transcription needs the native ASR source from ComfyUI-Drama3. "
        f"Clone {ASR_BACKEND_URL} into custom_nodes and check out {ASR_BACKEND_COMMIT}. "
        "See docs/portable_install.md. Plain TTS and manual cloning do not need ASR.")


@lru_cache(maxsize=1)
def load_backend(package_path):
    suffix = hashlib.sha256(str(package_path).encode("utf-8")).hexdigest()[:12]
    name = __package__ + "._native_asr_" + suffix
    spec = importlib.util.spec_from_file_location(
        name, Path(package_path) / "__init__.py", submodule_search_locations=[str(package_path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        return importlib.import_module(name + ".asr")
    except ImportError as error:
        sys.modules.pop(name, None)
        raise ImportError(
            "Native Qwen3-ASR could not import in this ComfyUI Python environment. "
            "Use the pinned ASR source and a compatible ComfyUI; no qwen-asr pip package is required. "
            f"Original error: {error}") from error
