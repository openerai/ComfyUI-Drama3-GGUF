# Drama3 GGUF · Start Here

Generate speech from text or clone a voice from a reference recording. This workflow uses a **Drama3-capable audio.cpp engine and a GGUF package**, obtained separately.

## Model Links

Choose **one GGUF**. The original TTS checkpoint and a separate codec download are not required.

- [Q2 experts / Q8 backbone · 15.88 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf)
- [Q3 experts / Q8 backbone · 18.93 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf)
- [Q4 experts / Q4 backbone · 21.78 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf)
- [Q4 experts / Q8 backbone · 22.91 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf)

These are disk sizes, not RAM or VRAM requirements. See the **Hardware** note for starting suggestions.

## Model Storage Location

Suggested layout; another folder is fine when specified by model_path in config.json.

```text
ComfyUI/
├─ models/
│  ├─ drama3/
│  │  └─ <selected-file>.gguf
│  └─ asr/                     <- auto-transcript Clone only
│     └─ qwen3_asr_0.6b_bf16.safetensors
└─ custom_nodes/
   ├─ ComfyUI-Drama3-GGUF/
   │  ├─ config.managed.example.json
   │  └─ config.json           <- settings for this installation
   └─ ComfyUI-Drama3/          <- optional ASR nodes
```

**Do not select the GGUF in a normal Checkpoint Loader.** A separate audio.cpp server loads model_path. **Model ID=auto** selects a model registered on that server.

## Engine & Config

1. Prepare the engine using the [compatible backend guide](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend). CPU, CUDA and other backends depend on your build.
2. On first install, copy config.managed.example.json to config.json. Merge changes into an existing configuration rather than replacing it.
3. Set `mode=managed`, `executable=<engine-path>` and `backend=<supported-backend>`. For the suggested layout, model_path is:

```text
../../models/drama3/<selected-file>.gguf
```

Relative paths start from the config.json folder. After changes, run `python run_server.py --stop` with ComfyUI's Python from the node folder; the next request starts the updated server. For an external server, set **Server URL** and install/register the model on that server.

## How to Use

1. **TTS:** enter new dialogue in Script & Direction if present; in a basic workflow, enter it directly in Generate / Voice Clone's New speech text.
2. **Clone:** choose Load Reference Audio, trim a clean segment, and enter the **exact words spoken in that segment** as Reference transcript.
3. **Auto-transcript Clone only:** download the 0.6B file above (about 1.6 GB) from the [ASR model files](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main) and install the [Qwen3-ASR nodes](https://github.com/PedroMarinhoDev/ComfyUI-Drama3). Select ASR Model, then use **Run Branch** on Reference Transcript to review recognition.
4. Put emotion/delivery instructions in Direction if available. In basic workflows, prepend a bracket instruction such as `[friendly delivery]` to the new dialogue. Keep acting instructions out of the reference transcript. Click **Run**, then preview/save the output.
5. Controls variants also adjust speed, gain and loudness after generation. See **Guide** for FFmpeg requirements and emotion examples.

See **Hardware** for long-form/context/memory settings and **Setup** for full installation details. [Model and hardware guide](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_EN.md)

Checked 2026-10-18. Hardware suggestions are starting points, not a guarantee of execution on every system.
