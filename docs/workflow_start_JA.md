# ダウンロードするファイル

**TTS：GGUFを1つだけ選びます。**

| ダウンロード | ディスク容量 | 本プロジェクトの確認 |
| --- | ---: | --- |
| [Q2 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | 推論確認済み |
| [Q3 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | 未検証の選択肢 |
| [Q4 / Q4 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | 未検証の選択肢 |
| [Q4 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | 未検証の選択肢 |

**自動文字起こしCloneのみ：ASRを1つ追加。** 通常TTS・手動Cloneには不要です。

| ダウンロード | ディスク容量 | 本プロジェクトの確認 |
| --- | ---: | --- |
| [Qwen3-ASR 0.6B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors) | 1.46 GiB | 推論確認済み |
| [Qwen3-ASR 1.7B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_1.7b_bf16.safetensors) | 3.80 GiB | 未検証の選択肢 |

**保存先**
- GGUF → `models/drama3/`、config.jsonのmodel_pathで指定
- ASR → `models/asr/`、ASR Model (Local File)で選択

ASRは**変換済み単一safetensors**です。他の拡張の元HFフォルダー用ローダーと混用しません。

GiBはディスク容量で、RAM・VRAM要件ではありません。GGUFにはコーデックが入り、対応audio.cppエンジンは別途必要です。

[全ファイル名・高度なGGUF・ハッシュ](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_downloads.md) · [モデル・仕様](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_JA.md)

上の **詳しい説明を開閉** で導入・演技・メモリ説明を表示できます。
