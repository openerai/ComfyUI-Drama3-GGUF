# 电脑配置指南

**适用于当前audio.cpp + Jmica GGUF配置的起点建议。** 文件大小不是显存需求；下表不是最低配置或运行保证。

| 电脑配置 | 从哪里开始 |
| --- | --- |
| RAM 16 GB及以下 / 显存8 GB及以下 | 此配置未经验证，Q2也可能放不下。优先考虑外部服务器。 |
| RAM 32 GB及以上 / 显存8–12 GB | 从Q2和简短普通TTS开始。考虑CPU专家卸载及streaming，同时观察RAM与显存。8 GB运行未经确认。 |
| RAM 32–64 GB及以上 / 显存16 GB | 从Q2开始，并测量克隆峰值。确认有余量后再比较Q3、Q4。 |
| RAM 64 GB及以上 / 显存24 GB及以上 | 可比较Q3、Q4。长上下文和参考音频需要额外内存，先用短输入确认。 |
| CPU / Apple统一内存 / 其他GPU | 对应引擎构建必须支持Drama3，勿直接套用CUDA设置。本项目未验证实际推理。 |

**实际验证范围**
- Windows、RAM 128 GB、RTX 5070 Ti 16 GB：Q2完成TTS、手动及自动转写克隆。
- 另一台Windows、RAM 32 GB、显存12 GB配置：有Q2 streaming生成74.7秒TTS的记录，不保证该配置档位的整体质量。
- 本项目未验证Q3、Q4或其他操作系统上的推理。

**降低负担的顺序**
1. 先用简短普通TTS确认。
2. 模型放SSD；可从disk_experts=true、expert_cache_size=8、pin_experts=false开始考虑。
3. 显存不足时考虑CPU专家卸载、CPU编解码器或streaming，RAM需求与等待时间可能增加。
4. 可选转写从ASR 0.6B开始；克隆需要编码参考音频，可能比普通TTS占用更多内存。

在每台PC的config.json中选择设置，本指南不会自动修改配置。

[详细设置](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_ZH.md) · [实际验证](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

[安装与路径](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)
