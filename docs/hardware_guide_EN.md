# Computer hardware guide

**Starting choices for the current audio.cpp + Jmica GGUF setup.** Disk size is not VRAM demand. These are suggestions, not minimum requirements or guarantees.

| Your computer | Starting point |
| --- | --- |
| RAM 16 GB or less / VRAM 8 GB or less | Unverified with this setup; even Q2 may not fit. Consider an external server first. |
| RAM 32 GB or more / VRAM 8–12 GB | Try Q2 with short plain TTS. Consider CPU expert offload and streaming; monitor both RAM and VRAM. 8 GB execution is unverified. |
| RAM 32–64 GB or more / VRAM 16 GB | Start with Q2 and measure cloning peaks too. Compare Q3/Q4 only after confirming spare memory. |
| RAM 64 GB or more / VRAM 24 GB or more | Q3/Q4 are comparison candidates. Start short; larger context and references need extra memory. |
| CPU / Apple unified memory / other GPU | The engine build must support Drama3 on that backend. Do not copy CUDA settings; actual inference is unverified by this project. |

**Actually exercised**
- Windows, RAM 128 GB, RTX 5070 Ti 16 GB: Q2 TTS, manual Clone and automatic-transcript Clone.
- Separate Windows, RAM 32 GB, VRAM 12 GB setup: a recorded 74.7 s Q2 streaming TTS run. This is not a quality guarantee for that hardware tier.
- Q3/Q4 and inference on other operating systems remain unverified by this project.

**Reduce demand step by step**
1. Begin with short plain TTS.
2. Keep the model on SSD; consider disk_experts=true, expert_cache_size=8, pin_experts=false as starting settings.
3. If VRAM runs out, consider CPU expert offload, CPU codec or streaming. RAM demand and latency can increase.
4. Start optional transcription with ASR 0.6B. Cloning also encodes the reference and may need more memory than TTS.

Choose settings in each PC's config.json. This guide does not change them automatically.

[Detailed settings](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_EN.md) · [Actual validation](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

[Installation and paths](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)
