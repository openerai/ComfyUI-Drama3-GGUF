# Model downloads and hardware settings

## 1. Download and install

Choose **one standalone GGUF** from [Jmica / Drama-3-GGUF](https://huggingface.co/Jmica/Drama-3-GGUF/tree/main). Open the file link and choose Download. These packages include the codec and required model metadata; an original Drama3 checkpoint or separate codec is not needed for this pipeline.

| Package | Disk size | Selection notes |
| --- | --- | --- |
| [Q8 backbone / Q2 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | Smallest of these four files |
| [Q8 backbone / Q3 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | Comparison candidate |
| [Q4 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | Different backbone precision |
| [Q8 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | Comparison candidate |

Disk size is not a RAM/VRAM requirement or a ranking of GPU memory use. More bits do not guarantee better pronunciation or acting. The additional FP32-router/BF16 profiles have not been separately verified with this project's pinned runtime.

### Storage and engine

1. Store the GGUF in a folder such as `ComfyUI/models/drama3/`. An SSD helps disk-expert reads. Leave extra space for the runtime, cache and outputs.
2. A **Drama3-capable audio.cpp executable is required separately**. Generic LLM GGUF loaders will not work. Follow the [backend build guide](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend).
3. For managed mode, copy config.managed.example.json to config.json only on first install, then set mode, executable, model_path and backend. Preserve other existing settings.
4. For the suggested folder, model_path is `../../models/drama3/<selected-file>.gguf`, relative to config.json. Model ID=auto selects a registered server model, not a file on disk.
5. For external mode, register the model on the server and set Server URL. Client configuration does not control that server's resources.

### Optional automatic reference transcription

Only auto-transcript Clone additionally needs **qwen3_asr_0.6b_bf16.safetensors** (about 1.6 GB) from [Qwen3-ASR-ComfyUI](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main) in `ComfyUI/models/asr/`, plus [ComfyUI-Drama3's Qwen3-ASR nodes](https://github.com/PedroMarinhoDev/ComfyUI-Drama3). Select the file in ASR Model. Ordinary TTS and manual-transcript Clone do not need ASR. A ForcedAligner or original TTS weights are not required by this GGUF workflow.

Sources: [GGUF model card](https://huggingface.co/Jmica/Drama-3-GGUF), [ASR model card](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI). Check each model's own license.

## 2. Hardware settings and troubleshooting

These are **suggested starting points, not minimum requirements or guaranteed configurations**. Most combinations have not been measured by this project. Available memory, other apps, backend, operating system, reference duration and context all matter.

| Environment | Starting candidate |
| --- | --- |
| Around 16 GB RAM / up to 8 GB VRAM | Unverified; even Q2 may not fit. Check fixed GPU weights below and consider CPU or an external server. |
| Around 32 GB RAM / 8–12 GB VRAM | Q2 is the smallest file to try. Start with disk experts, cache=8 and pin_experts=false; monitor available memory. |
| 32–64 GB RAM / around 16 GB VRAM | Compare Q3/Q8 and Q4/Q4 using measured peak memory, not file size alone. |
| 64+ GB RAM / 24+ GB VRAM | Q4/Q8 is another candidate. Increase cache or context only after measuring headroom. |
| CPU / other GPU backends | Confirm Drama3 support in your CPU, Metal or Vulkan build. Do not copy CUDA settings blindly. Unified memory is shared by CPU and GPU. |

The actual long-form check was **74.7 seconds of Q2 TTS on one Windows CUDA system with 32 GB RAM, 12 GB VRAM and streaming mode**. This does not validate every tier or long-form Clone. [Execution record](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

### Settings to adjust

Merge options into the installation's config.json. After changes, run `python run_server.py --stop` using ComfyUI's Python from the node folder. The managed server uses the new settings on its next request.

- **Backend:** cuda requires a compatible NVIDIA CUDA engine; cpu uses the CPU engine. Confirm your build supports metal or vulkan before selecting one.
- **Session options:** `fish_drama3.disk_experts=true`, `fish_drama3.expert_cache_size=8`, `fish_drama3.pin_experts=false` are conservative starting choices. Pinning all experts in RAM needs measured headroom.
- **Low VRAM:** consider `fish_drama3.codec_backend=cpu` and increasing `fish_drama3.cpu_expert_layers` (0–40). Host memory use and latency can increase. With disk experts this moves bounded expert caches, **not the attention, shared backbone or audio tower**. It does not guarantee operation on a very small GPU.
- **Codec memory:** top-level `run_mode=streaming` processes codec frames incrementally in a compatible engine and returns a complete WAV. Compared with the default offline mode, it can reduce the final codec graph allocation. It does not guarantee reference encoding or overall model fit. Restart the managed server after changes.
- **Long-form generation:** `fish_drama3.context_length=4096` is a starting value. Saved Max seconds=47 is a per-chunk budget, not the total output limit. Prompt, reference, previous chunk and next generation share context. Larger budgets may need more context and working memory. `request_timeout_seconds=0` removes only the HTTP read-wait limit.
- **Output checks:** if a token-cap warning appears, check the ending. The model can repeat or omit dialogue. The same seed can produce different results after changing quantization or offload placement.

### Troubleshooting

| Message or symptom | First checks |
| --- | --- |
| Context capacity exceeded | Increase context_length in session_options, then restart the managed server. References and previous chunks also occupy context. |
| CUDA / allocation failure | Inspect VRAM, RAM and, on Windows, memory.private_limit_gib. Distinguish GPU allocation failure from the private/commit cap. |
| Stopped to preserve RAM | Check other apps and memory.working_set_gib; lower the local resident-memory target if needed. Retain the minimum-available-RAM guard. |
| Response timeout | Check whether the server is still generating. Increase request_timeout_seconds or set 0 if appropriate. |

Private commit and resident RAM are different limits. Each installation chooses its own limits; these notes do not automatically change settings.

Sources: [verification](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md), [pinned audio.cpp guide](https://github.com/0xShug0/audio.cpp/blob/ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f/docs/models/fish_drama3.md), [publisher validation limits](https://huggingface.co/Jmica/Drama-3-GGUF#validation-limits). Sizes checked 2026-10-18 and may change.
