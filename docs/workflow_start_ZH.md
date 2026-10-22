# 需要下载的文件

**TTS：只选一个GGUF。**

| 下载 | 磁盘大小 | 本项目验证 |
| --- | ---: | --- |
| [Q2 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | 实际推理已验证 |
| [Q3 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | 未验证选项 |
| [Q4 / Q4 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | 未验证选项 |
| [Q4 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | 未验证选项 |

**仅自动转写Clone：另加一个ASR文件。** 普通TTS和手动Clone不需要。

| 下载 | 磁盘大小 | 本项目验证 |
| --- | ---: | --- |
| [Qwen3-ASR 0.6B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors) | 1.46 GiB | 实际推理已验证 |
| [Qwen3-ASR 1.7B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_1.7b_bf16.safetensors) | 3.80 GiB | 未验证选项 |

**存放位置**
- GGUF → `models/drama3/`，在config.json的model_path中指定
- ASR → `models/asr/`，在ASR Model (Local File)中选择

ASR是**转换后的单个safetensors文件**，不要与其他扩展的原始HF文件夹加载器混用。

GiB是磁盘大小，并非RAM/VRAM需求。GGUF已含编解码器；兼容audio.cpp引擎需另行准备。

[完整文件名、高级GGUF与哈希](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_downloads.md) · [模型与硬件](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_ZH.md)

点击上方 **展开/收起详细说明** 查看安装、表演和内存说明。
