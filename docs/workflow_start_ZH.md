# Drama3 GGUF · 使用入门

根据文本生成语音，或使用参考录音克隆声音。本工作流需要另行获取的 **支持 Drama3 的 audio.cpp 引擎和 GGUF 模型包**。

## 模型链接

**选择一个 GGUF 文件**即可。本流程不需要原始 TTS 检查点，也无需单独下载编解码器。

- [Q2 experts / Q8 backbone · 15.88 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf)
- [Q3 experts / Q8 backbone · 18.93 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf)
- [Q4 experts / Q4 backbone · 21.78 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf)
- [Q4 experts / Q8 backbone · 22.91 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf)

以上为磁盘文件大小，并非 RAM 或显存需求。初始配置建议请参阅 **Hardware** 说明。

## 模型存储位置

建议按以下方式放置；也可以在 config.json 的 model_path 中指定其他目录。

```text
ComfyUI/
├─ models/
│  ├─ drama3/
│  │  └─ <selected-file>.gguf
│  └─ asr/                     <- 仅供参考录音自动转写 Clone 使用
│     └─ qwen3_asr_0.6b_bf16.safetensors
└─ custom_nodes/
   ├─ ComfyUI-Drama3-GGUF/
   │  ├─ config.managed.example.json
   │  └─ config.json           <- 当前安装环境的配置
   └─ ComfyUI-Drama3/          <- 可选的 ASR 节点
```

**不要在普通 Checkpoint Loader 中选择 GGUF。** 独立的 audio.cpp 服务器根据 model_path 加载模型。**Model ID=auto** 选择的是该服务器已注册的模型。

## 引擎与配置

1. 按[兼容后端指南](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)准备引擎。CPU、CUDA 等后端是否可用取决于构建版本。
2. 仅在首次安装时，将 config.managed.example.json 复制为 config.json。已有配置请合并修改，不要直接覆盖。
3. 设置 `mode=managed`、`executable=<engine-path>` 和 `backend=<supported-backend>`。采用上述目录时，model_path 为：

```text
../../models/drama3/<selected-file>.gguf
```

相对路径以 config.json 所在目录为基准。修改后，在节点目录使用 ComfyUI 的 Python 执行 `python run_server.py --stop`；下次请求会启动采用新配置的服务器。使用外部服务器时，设置 **Server URL**，并在服务器端安装、注册模型。

## 使用方法

1. **TTS：** 若有 Script & Direction，在该节点输入新台词；基础版则直接填写 Generate / Voice Clone 的 New speech text。
2. **Clone：** 在 Load Reference Audio 选择录音，裁剪出清晰片段，并在 Reference transcript 中**准确填写该片段实际说出的内容**。
3. **仅自动转写 Clone：** 从 [ASR 模型文件](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main)下载上述 0.6B 文件（约 1.6 GB），安装 [Qwen3-ASR 节点](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)。选择 ASR Model，然后对 Reference Transcript 使用 **Run Branch** 检查识别结果。
4. 若有 Direction，在其中填写情绪和说话方式。基础版可在新台词前添加 `[friendly delivery]` 等方括号指示。参考转写中不要加入表演指示。点击 **Run**，然后试听、保存输出。
5. Controls 版还可在生成后调整速度、增益和响度。FFmpeg 要求及情绪示例请参阅 **Guide**。

长文本、上下文、内存设置见 **Hardware**，完整安装步骤见 **Setup**。[模型与硬件指南](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_ZH.md)

核查日期：2026-10-18。硬件建议只是起点，不保证在所有系统上均可运行。
