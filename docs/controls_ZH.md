# 表演、采样与音频调节

## Script & Direction

在 New speech text 中填写新台词，在 Direction 中用自然语言描述表演方式，不必加方括号。Script & Direction 会在前面添加 `[direction]`。没有此节点的基础版可直接在生成文本中输入方括号指示。

Delivery 会用成对标签包裹整个短句。若只想强调某个词，请设置 Delivery=none 并手写标签，例如 `今天是<emphasis>全新的</emphasis>开始。` 或 `<whisper>请保持安静。</whisper>`。`[sighs]` 等声音指示应放在希望出现的位置。这些指示不保证表演或声音质量，请先用短句比较。参考转写只填写录音中实际说出的内容。

### 情绪示例

Delivery 预设并不是全部情绪列表。可使用自然语言描述情绪，并先从 Delivery=none 开始。

- 喜悦：`bright and happy, with a slight smile in the voice`
- 悲伤：`quietly sad, holding back tears`
- 克制的愤怒：`low and firm, suppressing anger`
- 窘迫：`hesitate briefly, then speak cautiously`
- 情绪变化：`anxious at first, relieved at the end`

也可以在句中插入指示：`[surprised] 真的吗？ [relieved] 太好了。` 这些是表演指示，并不意味着存在一套保证生效的固定情绪命令或数值强度控制。

原生默认分块长度为 200 个字符，长成对标签的作用范围不会跨块延续。选择 Delivery 时，Script & Direction 会拒绝包含标签和指示后超过 200 字符的输入。较长的手写标签段落请拆成短句。[官方语法](https://docs.fish.audio/features/text-to-speech/drama-3)

## 生成与采样

建议从 Temperature=1.0 / Top P=0.9 / Top K=4097 开始，每次只改一个参数。温度过低可能产生静音或重复。本运行时拒绝 Top P=0 和 Top K=0。Temperature=0 也不保证所有重复处理路径完全确定。固定 seed 有助于在相同配置内比较；更改量化、后端或卸载位置可能改变输出。

4097与官方演示一样保留结束标记和全部候选，旧文件的值不会自动更改。生成节点的 Raw output check 显示归一化前的信号。低音量或达到预算的提示不等于已自动判定没有语音，请试听确认。单纯放大或缩短预算不是生成失败的通用解决办法。[对照验证](verification.md#sampling-and-output-diagnostics-0111)

Max seconds 是每个文本块的预算。新节点默认 12 秒，保存的工作流从**每块 47 秒**开始。该值可调，并非总输出时长上限。模型对应的输入上限为 12,173 秒，由 262,144 个上下文位置和编解码器帧率推导而来，并非输出时长或质量保证。提示词、参考和历史也会消耗上下文。

托管服务器的上下文默认从 `fish_drama3.context_length=4096` 开始。config.json 中明确设置的旧值会保留，直至手动修改。合并修改时不要删除路径、后端或内存设置。使用 `python run_server.py --stop` 停止后，下次请求才会应用修改。更多上下文需要更多内存。`request_timeout_seconds=0` 关闭 HTTP 读取等待限制，默认值为 600 秒。超时不会取消服务器推理，重试前应先检查状态。

## Audio Controls (Local)

- Speed=1.0 保持原速；1.2 更快，0.8 更慢。FFmpeg atempo 保持音高。
- Volume dB：0 保持增益；-6 降低，+3 提高。
- Normalize loudness 使用本地 EBU R128 处理。此处 Target LUFS 默认为 -16，不保证与 Fish 网页版一致，也不保证每个短音频都精确达到目标。
- 处理顺序：速度 → 响度归一化 → 增益 → 0.98 峰值限制。归一化后追加增益会改变最终响度。

非原样传递的处理需要 PATH 中有 FFmpeg，或在 config.json 中设置 ffmpeg_path。1x / 0dB / 关闭归一化时，音频采样原样传递。采样率和声道数保持不变，支持一个音频批次。只修改音频调节参数时，可以复用同一图中的生成音频。单独运行 ASR 分支可能清空 ComfyUI 的生成缓存。

## 与 Fish 网页版的区别

这些是本地后处理控制，并非模型原生速度控制，也不是对 Fish 云服务的完整复现。尚未实现云端数字/日期文本规范化、自动标签或 S2.1 标签兼容模式。较难读的数字或单位请改成希望朗读的写法。此前查看的网页为 Drama3 提供音量/速度选项，为 S2.1 Pro 额外提供规范化/标签选项；它们是不同模型与服务。
