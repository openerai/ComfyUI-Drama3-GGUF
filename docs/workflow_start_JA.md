# Drama3 GGUF · はじめに

テキストから音声を生成したり、参照録音を使って声を複製したりできます。このワークフローには、別途入手する **Drama3 対応 audio.cpp エンジンと GGUF パッケージ**が必要です。

## モデルのリンク

**GGUF を1つ選択**してください。元の TTS チェックポイントや、別のコーデックのダウンロードは不要です。

- [Q2 experts / Q8 backbone · 15.88 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf)
- [Q3 experts / Q8 backbone · 18.93 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf)
- [Q4 experts / Q4 backbone · 21.78 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf)
- [Q4 experts / Q8 backbone · 22.91 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf)

上記はディスク容量であり、必要な RAM や VRAM の容量ではありません。設定の出発点は **Hardware** ノートを参照してください。

## モデルの保存場所

以下は推奨配置です。config.json の model_path で指定すれば、別のフォルダーも使用できます。

```text
ComfyUI/
├─ models/
│  ├─ drama3/
│  │  └─ <selected-file>.gguf
│  └─ asr/                     <- 参照音声を自動文字起こしする Clone のみ
│     └─ qwen3_asr_0.6b_bf16.safetensors
└─ custom_nodes/
   ├─ ComfyUI-Drama3-GGUF/
   │  ├─ config.managed.example.json
   │  └─ config.json           <- この環境固有の設定
   └─ ComfyUI-Drama3/          <- 任意の ASR ノード
```

**通常の Checkpoint Loader で GGUF を選択しないでください。** 別の audio.cpp サーバーが model_path を読み込みます。**Model ID=auto** は、そのサーバーに登録されたモデルを選択します。

## エンジンと設定

1. [対応バックエンドのガイド](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)に従ってエンジンを用意します。CPU、CUDA などの対応状況はビルドによって異なります。
2. 初回のみ config.managed.example.json を config.json にコピーします。既存の設定がある場合は、ファイルを置き換えずに変更点を統合してください。
3. `mode=managed`、`executable=<engine-path>`、`backend=<supported-backend>` を設定します。上記の配置の場合、model_path は次のとおりです。

```text
../../models/drama3/<selected-file>.gguf
```

相対パスの基準は config.json のフォルダーです。変更後はノードのフォルダーで、ComfyUI の Python を使って `python run_server.py --stop` を実行します。次のリクエストで新しい設定のサーバーが起動します。外部サーバーの場合は **Server URL** を設定し、そのサーバー側でモデルを配置・登録してください。

## 使い方

1. **TTS:** Script & Direction がある場合は、そこで新しいセリフを入力します。基本版では Generate / Voice Clone の New speech text に直接入力します。
2. **Clone:** Load Reference Audio で録音を選び、明瞭な区間を切り出します。Reference transcript には **その区間で実際に話した言葉を正確に**入力します。
3. **自動文字起こし Clone のみ:** [ASR モデルファイル](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main)から上記の 0.6B ファイル（約 1.6 GB）を取得し、[Qwen3-ASR ノード](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)をインストールします。ASR Model を選び、Reference Transcript の **Run Branch** で認識結果を確認します。
4. 感情や話し方は、Direction があればそこに指定します。基本版では `[friendly delivery]` のような括弧付き指示を新しいセリフの先頭に付けます。参照音声の文字起こしには演技指示を入れません。**Run** を押して、出力を試聴・保存します。
5. Controls 版では、生成後の速度・ゲイン・ラウドネスも調整できます。FFmpeg の要件と感情表現の例は **Guide** を参照してください。

長文・コンテキスト・メモリの設定は **Hardware**、詳しい導入手順は **Setup** を参照してください。[モデルとハードウェアのガイド](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_JA.md)

確認日: 2026-10-18。ハードウェアの提案は設定の出発点であり、すべての環境での動作を保証するものではありません。

## 出力の確認 · 0.1.11
通常のTTSでは reference_text を空欄にします。声や性別を選ぶ欄ではありません。Voice Cloneには選択した録音で実際に話した言葉を入力します。新しい既定値 Top K=4097 は終了トークンを含む全候補を使います。古いファイルの30などの値は自動変更しません。生成後に Raw output check の長さ・音量・予算到達の表示を確認し、実際に聞いてください。無音や雑音の増幅は生成の修正にはなりません。
