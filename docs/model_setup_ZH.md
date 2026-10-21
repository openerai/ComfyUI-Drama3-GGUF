# 模型下载与硬件设置

## 1. 下载与安装

从 [Jmica / Drama-3-GGUF](https://huggingface.co/Jmica/Drama-3-GGUF/tree/main) **选择一个独立 GGUF 模型包**，打开文件链接并选择 Download。这些模型包已包含编解码器及必要的模型元数据；本流程不需要原始 Drama3 检查点或单独的编解码器。

| 模型包 | 磁盘大小 | 选择说明 |
| --- | --- | --- |
| [Q8 backbone / Q2 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | 这四个文件中最小的一个 |
| [Q8 backbone / Q3 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | 可供比较 |
| [Q4 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | backbone 精度不同 |
| [Q8 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | 可供比较 |

磁盘大小并非 RAM/显存需求，也不是显存占用排名。更多位数不保证发音或表演更好。额外的 FP32-router/BF16 配置尚未在本项目固定的运行时中单独验证。

### 存储与引擎

1. 将 GGUF 放在 `ComfyUI/models/drama3/` 等目录。SSD 有助于读取磁盘上的 experts。还需为运行时、缓存和输出预留空间。
2. **必须另外准备支持 Drama3 的 audio.cpp 可执行文件。** 通用 LLM GGUF 加载器无法代替它。参阅[后端构建指南](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)。
3. managed 模式下，仅首次安装时将 config.managed.example.json 复制为 config.json，再设置 mode、executable、model_path、backend。保留其他已有设置。
4. 采用建议目录时，model_path 为相对 config.json 的 `../../models/drama3/<selected-file>.gguf`。Model ID=auto 选择服务器已注册的模型，而不是磁盘文件。
5. external 模式下，在服务器注册模型并设置 Server URL。客户端配置不会控制外部服务器的资源。

### 可选的参考录音自动转写

只有自动转写 Clone 需要额外下载 [Qwen3-ASR-ComfyUI](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main) 的 **qwen3_asr_0.6b_bf16.safetensors**（约 1.6 GB），放入 `ComfyUI/models/asr/`，并安装 [ComfyUI-Drama3 的 Qwen3-ASR 节点](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)。在 ASR Model 中选择该文件。普通 TTS 和手动填写转写的 Clone 不需要 ASR。本 GGUF 工作流不需要 ForcedAligner 或原始 TTS 权重。

来源：[GGUF 模型卡](https://huggingface.co/Jmica/Drama-3-GGUF)、[ASR 模型卡](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI)。请检查各模型自身的许可证。

## 2. 硬件设置与故障排查

以下是**建议的初始选择，并非最低要求或运行保证**。大多数组合未在本项目中实测。可用内存、其他应用、后端、操作系统、参考录音时长和上下文都会影响结果。

| 环境 | 初始候选方案 |
| --- | --- |
| RAM 约 16 GB / 显存不超过 8 GB | 未验证；即使 Q2 也可能放不下。注意下文不能卸载的 GPU 权重，并考虑 CPU 或外部服务器。 |
| RAM 约 32 GB / 显存 8–12 GB | Q2 是最小候选。从 disk experts、cache=8、pin_experts=false 开始，并监测可用内存。 |
| RAM 32–64 GB / 显存约 16 GB | 实测峰值内存后比较 Q3/Q8 与 Q4/Q4，不要只看文件大小。 |
| RAM 64 GB 以上 / 显存 24 GB 以上 | Q4/Q8 也是候选。确认余量后再增加缓存或上下文。 |
| CPU / 其他 GPU 后端 | 确认 CPU、Metal 或 Vulkan 构建支持 Drama3。不要直接照搬 CUDA 设置。统一内存由 CPU 和 GPU 共享。 |

已完成的长文本测试是：**在一台 RAM 32 GB、显存 12 GB 的 Windows CUDA 机器上，以 streaming 模式运行 Q2 TTS，生成了 74.7 秒音频**。这不代表已验证所有硬件档位或长文本 Clone。[执行记录](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

### 可调整的设置

将选项合并到当前安装环境的 config.json。修改后，在节点目录使用 ComfyUI 的 Python 执行 `python run_server.py --stop`。托管服务器会在下次请求时采用新设置。

- **Backend：** cuda 需要兼容的 NVIDIA CUDA 引擎；cpu 使用 CPU 引擎。选择 metal 或 vulkan 前请确认构建支持。
- **Session options：** `fish_drama3.disk_experts=true`、`fish_drama3.expert_cache_size=8`、`fish_drama3.pin_experts=false` 是较保守的起点。将全部 experts 固定在 RAM 中之前，应实测内存余量。
- **显存不足：** 可考虑 `fish_drama3.codec_backend=cpu`，并增加 `fish_drama3.cpu_expert_layers`（0–40）。这可能增加主机内存占用和延迟。使用 disk experts 时，转移的是容量受限的 expert 缓存，**不是 attention、共享 backbone 或 audio tower**，因此不保证能在极小显存的 GPU 上运行。
- **编解码器内存：** 支持的引擎可使用顶层 `run_mode=streaming`，逐帧处理编解码器并返回完整 WAV。相比默认 offline 模式，这可以减少最后阶段的编解码器计算图分配，但不保证参考音频编码或整个模型都能放入内存。修改后需重启托管服务器。
- **长文本生成：** `fish_drama3.context_length=4096` 是初始值。保存的 Max seconds=47 是每个文本块的预算，并非总输出时长上限。提示词、参考、上一块和下一次生成共享上下文。更大的预算可能需要更多上下文与工作内存。`request_timeout_seconds=0` 只取消 HTTP 读取等待时间限制。
- **输出检查：** 出现 token 上限警告时，请检查结尾。模型可能重复或遗漏台词。修改量化或卸载位置后，即使 seed 相同，结果也可能变化。

### 故障排查

| 提示或症状 | 首先检查 |
| --- | --- |
| Context capacity exceeded | 增加 session_options 中的 context_length，然后重启托管服务器。参考和之前的文本块也会占用上下文。 |
| CUDA / allocation failure | 检查显存、RAM，以及 Windows 的 memory.private_limit_gib。区分 GPU 分配失败和 private/commit 上限。 |
| Stopped to preserve RAM | 检查其他应用和 memory.working_set_gib；必要时降低本机的驻留内存目标。保留最低可用 RAM 保护阈值。 |
| Response timeout | 检查服务器是否仍在生成。必要时增加 request_timeout_seconds 或设为 0。 |

private commit 与驻留 RAM 是不同的限制。每个安装环境自行选择上限；这些说明不会自动更改配置。

来源：[验证记录](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)、[固定版本的 audio.cpp 指南](https://github.com/0xShug0/audio.cpp/blob/ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f/docs/models/fish_drama3.md)、[发布者的验证范围](https://huggingface.co/Jmica/Drama-3-GGUF#validation-limits)。大小核查日期：2026-10-18，之后可能变化。


## 0.2.0 安装检查与ASR格式
上述四个GGUF是TTS候选，本项目仅对Q2进行了实际推理验证。Qwen3-ASR是独立的转写模型。请把转换后的单文件 `qwen3_asr_0.6b_bf16.safetensors` 放入 `models/asr`，并在 **Drama3 GGUF · ASR Model (Local File)** 中选择。不要与其他扩展的原始HF模型文件夹加载器混用。使用独立节点 `Drama3GGUFASRLoader` → `Drama3GGUFASRTranscribe`，无需时间戳或ForcedAligner。
自动转写还需要固定版本的ComfyUI-Drama3原生ASR源码，无需直接修改外部节点。按[安装步骤](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)准备，然后用ComfyUI的Python执行 `python check_install.py` 和 `python install_workflows.py`。三种示例会复制到 **Drama3-GGUF-0.2.0**。自定义位置用 --comfy-root 或 --workflow-dir 指定。重启并刷新界面后重新打开复制的文件。仅更新文件不会改变已打开画面中的Top K=30，新示例使用4097。请试听确认生成的语音。
