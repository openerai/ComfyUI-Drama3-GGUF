# ComfyUI Drama3 GGUF

[한국어 안내](README_KO.md)

Generate speech in ComfyUI using a **Drama3-capable audio.cpp server** and a
[Drama3 GGUF package](https://huggingface.co/Jmica/Drama-3-GGUF).
The workflow has no GPU model, RAM size, local username, or quantization baked into it.

This is an HTTP bridge and an optional managed launcher. It does not implement
the model itself. **A compatible audio.cpp executable and model are separate prerequisites.**
Neither model weights, CUDA libraries, nor server binaries are included.

## Install

Clone this repository into your ComfyUI `custom_nodes` directory:

```sh
git clone https://github.com/openerai/ComfyUI-Drama3-GGUF.git
```

Using the **same Python environment that runs ComfyUI**, install `requirements.txt`,
then restart ComfyUI. Do not install a different PyTorch build for this node.

```sh
python -m pip install -r ComfyUI-Drama3-GGUF/requirements.txt
```

Open `example_workflows/Drama3_GGUF_TTS.json` for text-to-speech, or
`example_workflows/Drama3_GGUF_Voice_Clone.json` for reference voice cloning.
The node ID `Drama3GGUFGenerate` is retained for older local workflows.
The example uses ComfyUI's built-in `SaveAudioAdvanced` node, verified with ComfyUI 0.41.0.

## Choose how to run audio.cpp

**External server (default):** start your own Drama3 audio.cpp server, then set
`server_url` in the workflow. Blank uses `config.json`, or `http://127.0.0.1:8035`
if no config exists. `model_id=auto` requires exactly one registered model whose
family is `fish_drama3`; otherwise enter its ID explicitly. A model identified as
another family is rejected. External mode does not start/stop servers or change their memory settings.

**Managed server:** copy `config.managed.example.json` to `config.json` and set
`executable`, `model_path`, `backend`, and any required `library_dirs`.
Relative paths are resolved against the configuration file, not the current directory.
The node starts the server on its first request. Executable/model paths, backend,
and memory settings remain in the installation's config, not the shared workflow.
Any explicit server URL/model ID entered in a workflow will be saved with that workflow.
Restart the managed server after changing config.
Managed mode refuses to adopt another process or a server running a different configuration.

```sh
python run_server.py --stop
```

An alternative config location can be supplied through `COMFYUI_DRAMA3_CONFIG`.
`config.json` and `.runtime/` are ignored by Git. Logs and generated server settings
are kept in `.runtime/`, or in your configured `state_dir`.

## Obtain a compatible backend

This project pins its bundled model spec to audio.cpp commit
`ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f`.
Generic LLM GGUF loaders and older audio.cpp releases without Drama3 support will not work.
See the upstream [Drama3 build and model guide](https://github.com/0xShug0/audio.cpp/blob/ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f/docs/models/fish_drama3.md).

For Windows CUDA, install compatible Visual Studio C++ build tools (2022 or newer)
and a CUDA toolkit first. Clone audio.cpp and check out the pinned commit:

```sh
git clone https://github.com/0xShug0/audio.cpp.git
git -C audio.cpp checkout ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f
git -C audio.cpp -c submodule.external/audio.cpp-server-frontends.url=https://github.com/0xShug0/audio.cpp-server-frontends.git submodule update --init --recursive
```

From this node's folder in PowerShell:

```powershell
.\scripts\build_audio_cpp.ps1 -AudioCppRoot "path\to\audio.cpp"
```

The helper uses upstream's CUDA architecture detection for the build machine and
the latest installed supported Visual Studio, rather than forcing one GPU architecture.
The resulting executable is `audio.cpp/build/windows-cuda-release/bin/audiocpp_server.exe`.
Configure DLL directories if the runtime cannot locate your CUDA libraries.
This recipe requires a source build; it is not a one-click backend installer.

Download your selected model separately from [Jmica](https://huggingface.co/Jmica/Drama-3-GGUF).
The Q2 package is a smaller starting option; set `model_path` to the package appropriate
for your resources. The model filename is not stored in the shared workflow.

## Hardware and memory

In managed mode, backend and device are explicit settings (`cuda`, `cpu`, `vulkan`,
or `metal`, if supported by your audio.cpp build). There is no silent backend fallback.
The default session uses disk-backed experts, 8 cache slots, a 1024-token context,
and the selected backend for the codec. These trade memory for speed.

On Windows, the launcher applies a Job Object private-memory limit and a hard
working-set limit. Automatic working-set targets are 2 GiB for 16 GiB RAM,
4 GiB for 32 GiB RAM, and up to 8 GiB for 64 GiB or more. These are **cache targets,
not hardware requirements or proof that a model fits**. Override `memory` locally.
The launcher also stops its child if system available RAM falls below your threshold.
Non-Windows managed mode has the monitored RAM/RSS stop checks, not Windows hard limits.
Automatic targets use total RAM; other running applications may require a lower
local `working_set_gib`. If the available-RAM guard stops generation, lower that
cache target and restart the managed server before retrying.

| `memory` setting | Default |
| --- | --- |
| `working_set_gib` | `auto`: total RAM / 8, bounded to 2–8 GiB |
| `private_limit_gib` | At least 10 GiB, or working-set target + 6 GiB |
| `min_available_gib` | 3 GiB (2 GiB on systems below 24 GiB total) |
| `max_rss_gib` | Working-set target + 4 GiB |

The private/commit limit is different from resident RAM; GPU-driver allocations may
also consume this budget. These settings do not cap VRAM. No 16 GiB inference claim
is made by the 2 GiB cache target. `library_dirs` augments PATH for the child process;
on non-Windows systems install backend libraries using the platform's normal loader paths.

If VRAM is insufficient, upstream supports moving the codec to CPU
(`fish_drama3.codec_backend=cpu`) and moving expert layers to CPU
(`fish_drama3.cpu_expert_layers`). This increases host-memory demand and changes performance.
Use the upstream guide and verify your own settings. Split long text into short sentences.
Cloning also encodes the reference, so a configuration that fits ordinary TTS can
still run out of VRAM during cloning. Adjust CPU expert offload and codec settings
locally; the example workflow does not select these settings for other machines.
For a compatible backend, managed `run_mode=streaming` decodes one codec frame at
a time and still returns a complete WAV through this node. `offline` is the default.
This can reduce the final codec graph allocation; it does not guarantee that the
model fits. Restart the managed server after changing `run_mode`.
Managed mode releases ComfyUI's cached models before using the local backend by default;
set `release_comfy_models=false` to keep them, provided enough resources remain.

## Voice clone workflow

The clone example connects **Load Audio → Trim Audio Duration → Reference Preview
→ Voice Clone → Save Audio**. `Drama3GGUFClone` requires both reference audio and
its transcript, so a missing reference cannot silently fall back to ordinary TTS.

Select a clean recording of one person speaking. Set the trim start/duration in
seconds; use a short segment, such as 5–10 seconds. Put the **exact words from that
selected segment** in `reference_text`, and the **new sentence** in `text`.
If you change the selected segment, update its transcript too. The shared example
contains no recording or transcript; choose your own before running the clone.

To listen to the cropped reference **before cloning**, right-click only the
**Reference Preview** node and choose **Run Branch** (ComfyUI 0.41.0 frontend
1.55.17). Its player is generated without running Voice Clone or Save Audio.
Enter/correct the transcript, then use the main **Run** button for the full clone.

References must contain finite, non-silent samples and one audio batch. The default
reference limit is 15 seconds, checked before encoding or starting the server.
Change `reference_max_seconds` in your local config only if your server's context
capacity supports the longer reference plus the generation budget. The default
1024-token context can be exhausted by a long reference even when the file is small.

The existing TTS node still supports optional references. It now rejects a transcript
without reference audio. References are sent as PCM16 WAV base64 so server-side local
paths are not required, including for an external server. The inline WAV limit is
5 MiB. Audio and text are sent to the server URL you configure. Voice-cloning quality
has not been validated across speakers/languages by this project.

### Automatic reference transcription

Open `example_workflows/Drama3_GGUF_Voice_Clone_Auto_Transcript.json` to connect
the selected audio segment to local Qwen3-ASR, then Reference Transcript and the
clone's `reference_text`. This optional example additionally requires
[ComfyUI-Drama3](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)'s
`Qwen3ASRLoader` / `Qwen3ASRTranscribe` and a compatible converted Qwen3-ASR model
in `models/asr`. Select your model in ASR Model. This project does not install
or download an ASR engine or weights. The manual clone example remains independent
of that optional dependency.

Right-click only **Reference Transcript → Run Branch** to transcribe and review
before cloning. Uploading a file alone does not run inference; the main **Run**
executes transcription and cloning in sequence. ASR receives the same trimmed
audio as the clone. Leave **Correction** blank to use ASR, or enter the full exact
transcript to replace it. **Clear Correction and review again whenever the file
or trim changes.** Used reference transcript displays the actual text sent on.

The clone's **Reference transcript** means the words spoken in the reference
recording; **New speech text** means the new sentence to generate. Internal
`reference_text` / `text` names remain unchanged for saved workflows and API clients.

`UNKNOWN` widgets with red node errors can indicate a missing node definition.
Check startup/import errors and node registration, then refresh the browser after
the server is ready. Presentation labels do not repair or hide missing nodes.

## Validation and limits

See [verification](docs/verification.md) for executed checks and unverified cases.
Real inference is validated only on the hardware listed there; portable configuration
does not establish support for every OS/GPU/model. The project is an early beta.

```sh
python -m unittest discover -s tests -v
```

GitHub distribution is provided here; a Comfy Registry listing is not included in this release.
Bridge code is MIT licensed. See [third-party notices](THIRD_PARTY_NOTICES.md) for audio.cpp and weights.
