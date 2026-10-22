# PCスペック別ガイド

**現在のaudio.cpp + Jmica GGUF構成での出発点**です。ファイル容量はVRAM使用量ではありません。最低要件や動作保証ではありません。

| PCの構成 | どこから試すか |
| --- | --- |
| RAM 16 GB以下 / VRAM 8 GB以下 | この構成では未検証です。Q2でも不足する可能性があり、外部サーバーを先に検討します。 |
| RAM 32 GB以上 / VRAM 8–12 GB | Q2と短い通常TTSから開始。CPUエキスパートオフロードとstreamingを検討し、RAM・VRAMを測定。8 GBでの実行は未確認です。 |
| RAM 32–64 GB以上 / VRAM 16 GB | Q2から開始し、音声複製のピークも確認。余裕があればQ3・Q4を比較します。 |
| RAM 64 GB以上 / VRAM 24 GB以上 | Q3・Q4の比較候補です。長い文脈や参照もメモリを使うため、短い入力から確認します。 |
| CPU / Apple統合メモリ / その他GPU | 対応ビルドのDrama3サポートが必要です。CUDA設定を流用しません。本プロジェクトでは実推論未検証です。 |

**実行確認の範囲**
- Windows・RAM 128 GB・RTX 5070 Ti 16 GB：Q2でTTS・手動/自動文字起こし複製を実行。
- 別のWindows・RAM 32 GB・VRAM 12 GB構成：Q2・streamingで74.7秒のTTS生成記録。仕様区分全体の品質保証ではありません。
- Q3・Q4と他OSでの推論は本プロジェクトでは未検証です。

**負荷を下げる順序**
1. 短い通常TTSから確認します。
2. SSDにモデルを置き、disk_experts=true・expert_cache_size=8・pin_experts=falseを出発点として検討。
3. VRAM不足ならCPUエキスパートオフロード・CPUコーデック・streamingを検討。RAMと待ち時間は増える場合があります。
4. 自動文字起こしはASR 0.6Bから開始。複製は参照のエンコードで通常TTSよりメモリを使う場合があります。

設定は各PCのconfig.jsonで選択します。このガイドは自動変更しません。

[詳細設定](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_JA.md) · [実行検証](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

[導入とパス](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)
