# Models for this audio.cpp setup

These are Jmica packages. Other Drama-3 GGUFs may require a different engine or patch.


**TTS: download ONE GGUF.**

| Download | Disk size | Project validation |
| --- | ---: | --- |
| [Q2 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | Inference checked |
| [Q3 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | Untested option |
| [Q4 / Q4 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | Untested option |
| [Q4 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | Untested option |

**Automatic-transcript Clone only: add ONE ASR file.** Plain TTS and manual Clone skip it.

| Download | Disk size | Project validation |
| --- | ---: | --- |
| [Qwen3-ASR 0.6B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors) | 1.46 GiB | Inference checked |
| [Qwen3-ASR 1.7B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_1.7b_bf16.safetensors) | 3.80 GiB | Untested option |

**Storage**
- GGUF → `models/drama3/`; select its path in config.json
- ASR → `models/asr/`; select it in ASR Model (Local File)

ASR uses a **converted single safetensors file**, not another extension's raw HF directory loader.

GiB means disk size, not RAM/VRAM requirements. The GGUF embeds its codec; a compatible audio.cpp engine is separate.

[Full filenames, advanced GGUFs and hashes](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_downloads.md) · [Model/hardware guide](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_EN.md)

Use **Toggle detailed help** above for hardware profiles, acting and memory notes.