# モデルのダウンロードとハードウェア設定

## 1. ダウンロードと導入

[Jmica / Drama-3-GGUF](https://huggingface.co/Jmica/Drama-3-GGUF/tree/main) から **単体で使える GGUF を1つ**選び、ファイルのリンクを開いて Download を選択します。これらのパッケージにはコーデックと必要なモデル情報が含まれています。この構成では、元の Drama3 チェックポイントや別のコーデックは不要です。

| パッケージ | ディスク容量 | 選択時の目安 |
| --- | --- | --- |
| [Q8 backbone / Q2 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | この4つの中で最小のファイル |
| [Q8 backbone / Q3 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | 比較候補 |
| [Q4 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | backbone の精度が異なる構成 |
| [Q8 backbone / Q4 experts](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | 比較候補 |

ファイル容量は必要な RAM/VRAM 容量でも、GPU メモリ使用量の順位でもありません。ビット数が多くても、発音や演技が必ず良くなるとは限りません。追加の FP32-router/BF16 構成は、このプロジェクトが固定しているランタイムでは個別に検証していません。

### 保存場所とエンジン

1. GGUF を `ComfyUI/models/drama3/` などに置きます。disk experts の読み取りには SSD が役立ちます。ランタイム・キャッシュ・出力用の空き容量も確保してください。
2. **Drama3 対応 audio.cpp 実行ファイルが別途必要**です。一般的な LLM 用 GGUF ローダーでは動きません。[バックエンドのビルド手順](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)を参照してください。
3. managed モードでは、初回のみ config.managed.example.json を config.json にコピーし、mode・executable・model_path・backend を設定します。その他の既存設定は保持してください。
4. 推奨配置の場合、model_path は config.json を基準に `../../models/drama3/<selected-file>.gguf` です。Model ID=auto はディスク上のファイルではなく、サーバーに登録されたモデルを選びます。
5. external モードではサーバー側にモデルを登録し、Server URL を設定します。クライアントの設定では、そのサーバーのリソースを制御できません。

### 任意の参照音声の自動文字起こし

自動文字起こし Clone のみ、[Qwen3-ASR-ComfyUI](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main) の **qwen3_asr_0.6b_bf16.safetensors**（約 1.6 GB）を `ComfyUI/models/asr/` に置き、[ComfyUI-Drama3 の Qwen3-ASR ノード](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)も追加する必要があります。ASR Model でそのファイルを選択してください。通常の TTS と手入力の文字起こしを使う Clone には ASR は不要です。この GGUF ワークフローには ForcedAligner や元の TTS 重みも不要です。

出典: [GGUF モデルカード](https://huggingface.co/Jmica/Drama-3-GGUF)、[ASR モデルカード](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI)。各モデルのライセンスを確認してください。

## 2. ハードウェア設定と問題解決

以下は **設定の出発点の提案であり、最低要件や動作保証ではありません**。組み合わせの多くは本プロジェクトで実測していません。空きメモリ、他のアプリ、バックエンド、OS、参照音声の長さ、コンテキストが影響します。

| 環境 | 試す際の候補 |
| --- | --- |
| RAM 約 16 GB / VRAM 8 GB 以下 | 未検証で、Q2 でも収まらない場合があります。下記の固定 GPU 重みに注意し、CPU または外部サーバーを検討してください。 |
| RAM 約 32 GB / VRAM 8–12 GB | Q2 が最小の候補です。disk experts、cache=8、pin_experts=false から始め、空きメモリを監視します。 |
| RAM 32–64 GB / VRAM 約 16 GB | ファイル容量だけで判断せず、ピークメモリを実測して Q3/Q8 と Q4/Q4 を比較します。 |
| RAM 64 GB 以上 / VRAM 24 GB 以上 | Q4/Q8 も候補です。余裕を実測してからキャッシュやコンテキストを増やします。 |
| CPU / その他の GPU バックエンド | CPU・Metal・Vulkan ビルドの Drama3 対応を確認してください。CUDA の設定をそのままコピーしないでください。統合メモリは CPU と GPU で共有します。 |

実際の長文テストでは、**RAM 32 GB、VRAM 12 GB の Windows CUDA 環境1台で、streaming モードの Q2 TTS を使い 74.7 秒の音声**を生成しました。すべての環境や長文 Clone の動作を確認したものではありません。[実行記録](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

### 調整する設定

各環境の config.json に設定を統合します。変更後はノードのフォルダーで、ComfyUI の Python を使って `python run_server.py --stop` を実行してください。管理対象サーバーは次のリクエストから新しい設定を使用します。

- **Backend:** cuda には対応する NVIDIA CUDA エンジン、cpu には CPU エンジンが必要です。metal / vulkan はビルドの対応を確認してから選択します。
- **Session options:** `fish_drama3.disk_experts=true`、`fish_drama3.expert_cache_size=8`、`fish_drama3.pin_experts=false` は控えめな出発点です。すべての experts を RAM に固定する場合は、十分な余裕を実測してください。
- **VRAM 不足:** `fish_drama3.codec_backend=cpu` や `fish_drama3.cpu_expert_layers`（0–40）の増加を検討します。RAM 使用量と待ち時間が増える場合があります。disk experts 使用時に移るのは容量の限られた expert キャッシュであり、**attention・共有 backbone・audio tower は移りません**。小容量 GPU での動作保証にはなりません。
- **コーデックのメモリ:** 対応エンジンでトップレベルの `run_mode=streaming` を使うと、コーデックのフレームを順次処理し、完成した WAV を返します。既定の offline モードと比べ、最後のコーデックグラフの割り当てを減らせる場合があります。参照音声のエンコードやモデル全体がメモリに収まる保証ではありません。変更後は管理対象サーバーを再起動します。
- **長文生成:** `fish_drama3.context_length=4096` は出発点です。保存済みの Max seconds=47 はテキストの各チャンクの予算で、総出力時間の上限ではありません。プロンプト・参照・前チャンク・次の生成がコンテキストを共有します。予算を増やすと、より多くのコンテキストと作業メモリが必要になる場合があります。`request_timeout_seconds=0` が解除するのは HTTP の読み取り待ち時間だけです。
- **出力の確認:** トークン上限の警告が出た場合は末尾を確認してください。モデルがセリフを繰り返したり省略したりする場合があります。量子化やオフロード位置を変えると、同じ seed でも結果が変わることがあります。

### 問題解決

| メッセージ・症状 | 最初に確認すること |
| --- | --- |
| Context capacity exceeded | session_options の context_length を増やし、管理対象サーバーを再起動します。参照音声や前チャンクもコンテキストを使います。 |
| CUDA / allocation failure | VRAM・RAM と、Windows では memory.private_limit_gib を確認します。GPU の割り当て失敗と private/commit 上限を区別してください。 |
| Stopped to preserve RAM | 他のアプリと memory.working_set_gib を確認し、必要ならこの環境の常駐メモリ目標を下げます。空き RAM の下限ガードは保持してください。 |
| Response timeout | サーバーがまだ生成中か確認します。必要に応じて request_timeout_seconds を増やすか 0 にします。 |

private commit と常駐 RAM は異なる上限です。上限は各環境で設定します。このノートが設定を自動変更することはありません。

出典: [検証記録](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)、[固定バージョンの audio.cpp ガイド](https://github.com/0xShug0/audio.cpp/blob/ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f/docs/models/fish_drama3.md)、[公開元の検証範囲](https://huggingface.co/Jmica/Drama-3-GGUF#validation-limits)。容量の確認日: 2026-10-18。今後変更される場合があります。
