import comfy.model_management
import torch

from . import audio_controls, client
from .configuration import load_config


class Drama3GGUFGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "안녕하세요. 오늘도 좋은 하루 보내세요."}),
                "seed": ("INT", {"default": 123, "min": 0, "max": 2147483647, "control_after_generate": True}),
                "max_seconds": ("FLOAT", {"default": 12.0, "min": 1.0, "max": client.MAX_GENERATION_SECONDS, "step": 0.5,
                                           "tooltip": "Generation budget per text chunk, not a target duration. The upper bound uses the model's 262144-position context. The server must fit input/references plus generated frames; increase its context_length if needed."}),
            },
            "optional": {
                "reference_audio": ("AUDIO",),
                "reference_text": ("STRING", {"multiline": True, "default": "", "tooltip": "Exact words in the selected reference segment, not the new text to generate."}),
                "server_url": ("STRING", {"default": "", "tooltip": "Blank uses config.json or localhost:8035. Reference audio is sent to this server."}),
                "model_id": ("STRING", {"default": "auto", "tooltip": "auto selects the only Drama3 model registered on the server."}),
                "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05,
                                           "tooltip": "Sampling variation. Start at 1.0; very low values may produce silence."}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.01, "max": 1.0, "step": 0.01,
                                     "tooltip": "Sampling diversity. Native Drama3 default: 0.9; zero is invalid."}),
                "top_k": ("INT", {"default": 30, "min": 1, "max": 4096,
                                   "tooltip": "Sampling candidate count. Native Drama3 default: 30; zero is unsupported here."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "generate"
    CATEGORY = "audio/drama3"
    DESCRIPTION = "Generate audio with a Drama3 GGUF audio.cpp server. Runtime and memory settings belong to each installation, not the workflow."

    def generate(self, text, seed, max_seconds, reference_audio=None, reference_text="", server_url="", model_id="auto",
                 temperature=1.0, top_p=0.9, top_k=30):
        if not text.strip():
            raise ValueError("text cannot be empty.")
        max_tokens = client.generation_frames(max_seconds)
        client.sampling_options(temperature, top_p, top_k)
        config = load_config()
        target = server_url.strip() or config["server_url"]
        client.check_generation_capacity(config, target.rstrip("/"), max_tokens)
        reference = None
        if reference_audio is None and reference_text.strip():
            raise ValueError("Connect reference_audio when providing reference_text. Use the Voice Clone workflow for cloning.")
        if reference_audio is not None:
            waveform = reference_audio["waveform"]
            if waveform.ndim != 3 or waveform.shape[0] != 1:
                raise ValueError("Use one reference audio at a time: expected a single [1, channels, samples] batch.")
            waveform = waveform[0].detach().float().cpu().transpose(0, 1).numpy()
            reference = client.reference_payload(waveform, reference_audio["sample_rate"], reference_text,
                                                 max_seconds=config.get("reference_max_seconds", 15))
        local_managed = config["mode"] == "managed" and target.rstrip("/") == config["server_url"]
        if local_managed and config.get("release_comfy_models", True) and config.get("backend", "cuda") != "cpu":
            comfy.model_management.unload_all_models()
            comfy.model_management.soft_empty_cache()
        audio, sample_rate = client.generate(config, text, seed, max_tokens,
                                            url=target, model_id=model_id, reference=reference,
                                            interrupted=comfy.model_management.throw_exception_if_processing_interrupted,
                                            temperature=temperature, top_p=top_p, top_k=top_k)
        return ({"waveform": torch.from_numpy(audio.T.copy()).unsqueeze(0), "sample_rate": sample_rate},)


class Drama3GGUFClone(Drama3GGUFGenerate):
    @classmethod
    def INPUT_TYPES(cls):
        inputs = super().INPUT_TYPES()
        required = {name: inputs["optional"].pop(name) for name in ("reference_audio", "reference_text")}
        required.update(inputs["required"])
        required["text"][1]["default"] = "반갑습니다. 이 문장은 참조 음성을 사용한 복제 테스트입니다."
        inputs["required"] = required
        return inputs

    FUNCTION = "clone"
    DESCRIPTION = "Clone using one short speech reference and its exact transcript. Both are required; no unconditioned TTS fallback."

    def clone(self, reference_audio, reference_text, text, seed, max_seconds, server_url="", model_id="auto",
              temperature=1.0, top_p=0.9, top_k=30):
        if reference_audio is None or not reference_text.strip():
            raise ValueError("Voice Clone requires reference_audio and the exact reference_text for that audio segment.")
        return self.generate(text, seed, max_seconds, reference_audio, reference_text, server_url, model_id,
                             temperature, top_p, top_k)


class Drama3GGUFScript:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "text": ("STRING", {"multiline": True, "default": "안녕하세요. 오늘도 좋은 하루 보내세요."}),
            "direction": ("STRING", {"multiline": True, "default": "",
                                      "tooltip": "Optional natural-language acting direction, without brackets. Example: 차분하고 또렷하게."}),
            "delivery": (["none", "whisper", "emphasis", "soft", "fast", "slow", "stress", "forceful"],
                         {"default": "none", "tooltip": "Wrap the whole short script in this paired tag. For one word only, write paired tags directly in text."}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("script",)
    FUNCTION = "prepare"
    CATEGORY = "audio/drama3"
    DESCRIPTION = "Compose new speech text with an optional bracket direction and paired delivery tag. Never connect to the reference transcript."

    def prepare(self, text, direction="", delivery="none"):
        if not text.strip():
            raise ValueError("Enter the new words to speak in text.")
        if delivery not in self.INPUT_TYPES()["required"]["delivery"][0]:
            raise ValueError("Unknown delivery tag.")
        if "[" in direction or "]" in direction:
            raise ValueError("Enter direction without square brackets; the Script node adds them.")
        body = text if delivery == "none" else f"<{delivery}>{text}</{delivery}>"
        script = (f"[{direction.strip()}] " if direction.strip() else "") + body
        if delivery != "none" and len(script) > 200:
            raise ValueError("Keep the script including direction and paired tags within 200 characters, or split it into short sentences yourself.")
        return (script,)


class Drama3GGUFAudioControls:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "audio": ("AUDIO",),
            "speed": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0, "step": 0.05,
                                "tooltip": "Local FFmpeg tempo after generation. Greater than 1 is faster; pitch is preserved."}),
            "volume_db": ("FLOAT", {"default": 0.0, "min": -20.0, "max": 20.0, "step": 0.5,
                                    "tooltip": "Local output gain in dB, after optional loudness normalization. A safety limiter caps peaks."}),
            "normalize_loudness": ("BOOLEAN", {"default": False, "tooltip": "Local FFmpeg EBU R128 loudness normalization. Does not normalize script text."}),
            "target_lufs": ("FLOAT", {"default": -16.0, "min": -30.0, "max": -10.0, "step": 0.5,
                                      "tooltip": "Loudness target, used only when normalization is enabled. Default -16 LUFS; not Fish cloud parity."}),
        }}

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "adjust"
    CATEGORY = "audio/drama3"
    DESCRIPTION = "Local postprocessing: pitch-preserving tempo, loudness normalization, gain, and peak limiting. Neutral controls bypass FFmpeg."

    def adjust(self, audio, speed=1.0, volume_db=0.0, normalize_loudness=False, target_lufs=-16.0):
        waveform = audio["waveform"]
        if waveform.ndim != 3 or waveform.shape[0] != 1:
            raise ValueError("Audio Controls accepts one [1, channels, samples] audio batch at a time.")
        samples = waveform[0].detach().float().cpu().transpose(0, 1).numpy()
        output, rate = audio_controls.adjust_audio(samples, audio["sample_rate"], speed, volume_db,
                                                   normalize_loudness, target_lufs, config=load_config())
        return ({"waveform": torch.from_numpy(output.T.copy()).unsqueeze(0), "sample_rate": rate},)


class Drama3GGUFReferenceText:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "transcript": ("STRING", {"forceInput": True, "tooltip": "Speech recognition of the same trimmed audio used for cloning."}),
            "correction": ("STRING", {"multiline": True, "default": "",
                                       "tooltip": "Leave blank to use speech recognition. Otherwise enter the full corrected transcript. Clear this when changing the reference audio or trim."}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("reference_text",)
    FUNCTION = "prepare"
    OUTPUT_NODE = True
    CATEGORY = "audio/drama3"
    DESCRIPTION = "Preview the reference transcript sent to Voice Clone. An optional full correction replaces ASR text."

    def prepare(self, transcript, correction=""):
        text = correction.strip() or transcript.strip()
        if not text:
            raise ValueError("No reference speech was recognized. Check the selected audio or enter its exact transcript in correction.")
        return {"ui": {"text": [text]}, "result": (text,)}
