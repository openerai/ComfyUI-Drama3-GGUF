"""Collision-free adapters for the optional converted Qwen3-ASR model."""
import os

import folder_paths

from .asr_backend import find_backend, load_backend
from .configuration import load_config, resolve_path

LANGUAGES = ["auto", "Chinese", "English", "Cantonese", "Arabic", "German", "French", "Spanish", "Portuguese",
             "Indonesian", "Italian", "Korean", "Russian", "Thai", "Vietnamese", "Japanese", "Turkish", "Hindi",
             "Malay", "Dutch", "Swedish", "Danish", "Finnish", "Polish", "Czech", "Filipino", "Persian", "Greek",
             "Romanian", "Hungarian", "Macedonian"]


def register_asr_folder():
    folder_paths.add_model_folder_path("asr", os.path.join(folder_paths.models_dir, "asr"))
    paths, _ = folder_paths.folder_names_and_paths["asr"]
    folder_paths.folder_names_and_paths["asr"] = (paths, folder_paths.supported_pt_extensions)


class Drama3GGUFASRLoader:
    @classmethod
    def INPUT_TYPES(cls):
        register_asr_folder()
        return {"required": {"model_name": (folder_paths.get_filename_list("asr"), {
            "tooltip": "Converted qwen3_asr_0.6b_bf16.safetensors (or 1.7B) in models/asr. "
                       "This takes a single converted file, not a Hugging Face model directory."})}}

    RETURN_TYPES = ("DRAMA3_GGUF_ASR_MODEL",)
    FUNCTION = "load"
    CATEGORY = "audio/drama3/asr"
    DESCRIPTION = "Optional local ASR. Uses ComfyUI-Drama3's native implementation with unique node/socket IDs."

    def load(self, model_name):
        register_asr_folder()
        config = load_config()
        override = resolve_path(config, config["asr_backend_path"]) if config.get("asr_backend_path") else None
        path = find_backend(folder_paths.get_folder_paths("custom_nodes"), override)
        backend = load_backend(path)
        model = backend.load_qwen3_asr(folder_paths.get_full_path_or_raise("asr", model_name))
        return ({"model": model, "transcribe": backend.transcribe},)


class Drama3GGUFASRTranscribe:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("DRAMA3_GGUF_ASR_MODEL",), "audio": ("AUDIO",),
            "language": (LANGUAGES, {"default": "auto"}),
            "context": ("STRING", {"default": "", "multiline": True}),
            "max_new_tokens": ("INT", {"default": 256, "min": 1, "max": 32768}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "language")
    FUNCTION = "transcribe"
    CATEGORY = "audio/drama3/asr"
    DESCRIPTION = "Transcribe the selected reference segment. Text only: no timestamps or forced aligner."

    def transcribe(self, model, audio, language="auto", context="", max_new_tokens=256):
        waveform = audio["waveform"]
        if waveform.ndim != 3 or waveform.shape[0] != 1 or waveform.shape[-1] == 0:
            raise ValueError("ASR expects one nonempty [1, channels, samples] reference segment.")
        text, detected = model["transcribe"](
            model["model"], waveform[0], audio["sample_rate"],
            None if language == "auto" else language, context, max_new_tokens)
        if not text.strip():
            raise ValueError("No reference speech recognized. Preview the selected segment and adjust its trim.")
        return (text, detected)
