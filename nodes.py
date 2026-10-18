import math
import comfy.model_management
import torch

from . import client
from .configuration import load_config


class Drama3GGUFGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "안녕하세요. 오늘도 좋은 하루 보내세요."}),
                "seed": ("INT", {"default": 123, "min": 0, "max": 2147483647, "control_after_generate": True}),
                "max_seconds": ("FLOAT", {"default": 12.0, "min": 1.0, "max": 24.0, "step": 0.5,
                                           "tooltip": "Generation cap per text chunk. Split long text into short sentences."}),
            },
            "optional": {
                "reference_audio": ("AUDIO",),
                "reference_text": ("STRING", {"multiline": True, "default": ""}),
                "server_url": ("STRING", {"default": "", "tooltip": "Blank uses config.json or localhost:8035. Reference audio is sent to this server."}),
                "model_id": ("STRING", {"default": "auto", "tooltip": "auto selects the only Drama3 model registered on the server."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate"
    CATEGORY = "audio/drama3"
    DESCRIPTION = "Generate audio with a Drama3 GGUF audio.cpp server. Runtime and memory settings belong to each installation, not the workflow."

    def generate(self, text, seed, max_seconds, reference_audio=None, reference_text="", server_url="", model_id="auto"):
        if not text.strip():
            raise ValueError("text cannot be empty.")
        config = load_config()
        target = server_url.strip() or config["server_url"]
        local_managed = config["mode"] == "managed" and target.rstrip("/") == config["server_url"]
        if local_managed and config.get("release_comfy_models", True) and config.get("backend", "cuda") != "cpu":
            comfy.model_management.unload_all_models()
            comfy.model_management.soft_empty_cache()
        reference = None
        if reference_audio is not None:
            waveform = reference_audio["waveform"][0].detach().float().cpu().transpose(0, 1).numpy()
            reference = client.reference_payload(waveform, reference_audio["sample_rate"], reference_text)
        audio, sample_rate = client.generate(config, text, seed, math.ceil(max_seconds * 21.5),
                                            url=target, model_id=model_id, reference=reference,
                                            interrupted=comfy.model_management.throw_exception_if_processing_interrupted)
        return ({"waveform": torch.from_numpy(audio.T.copy()).unsqueeze(0), "sample_rate": sample_rate},)
