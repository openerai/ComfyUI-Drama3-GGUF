# Model downloads · 받을 모델 파일

Checked 2026-10-22. Download **one TTS GGUF**; automatic reference transcription additionally needs **one converted ASR file**. Sizes are disk GiB, not RAM/VRAM requirements.

TTS GGUF 하나를 선택하고, 자동 받아쓰기를 쓸 때만 ASR 하나를 추가합니다. 아래의 실행 확인은 이 프로젝트에서의 범위입니다. 메타데이터 확인만 된 파일은 동일 품질·호환성을 보장하지 않습니다.

## TTS · original four profiles / 기본 네 후보

| File | Disk | Project validation |
| --- | ---: | --- |
| [drama-3-backbone-8bit-experts-Q2_K.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | Local inference / 실행 확인 |
| [drama-3-backbone-8bit-experts-Q3_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | Metadata only / 실행 미검증 |
| [drama-3-backbone-4bit-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | Metadata only / 실행 미검증 |
| [drama-3-backbone-8bit-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | Metadata only / 실행 미검증 |

## Optional ASR / 자동 받아쓰기만

| File | Disk | Project validation |
| --- | ---: | --- |
| [qwen3_asr_0.6b_bf16.safetensors](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors) | 1.46 GiB | Local inference / 실행 확인 |
| [qwen3_asr_1.7b_bf16.safetensors](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_1.7b_bf16.safetensors) | 3.80 GiB | Metadata only / 실행 미검증 |

## Advanced GGUF comparisons / 고급 비교용 · pinned runtime unverified

| File | Disk | Project validation |
| --- | ---: | --- |
| [drama-3-backbone-8bit-F32-routers-BF16-embed-head-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-F32-routers-BF16-embed-head-experts-Q4_K_S.gguf) | 23.87 GiB | Metadata only / 실행 미검증 |
| [drama-3-backbone-8bit-F32-routers-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-F32-routers-experts-Q4_K_S.gguf) | 22.97 GiB | Metadata only / 실행 미검증 |

The advanced files are available from the model author, but were not tested by this project with its pinned engine. Higher precision alone does not ensure a better take. No additional codec file is needed by these GGUF packages. ASR files are converted single files; raw Qwen HF directories require another loader.

고급 GGUF 두 종류는 배포자가 제공하는 추가 선택지이며 이 프로젝트의 고정 엔진에서는 검증하지 않았습니다. 높은 정밀도가 더 좋은 음성을 보장하지 않습니다. ASR 모델은 원본 HF 폴더와 다른 변환 파일입니다.

[Exact bytes/revisions/SHA256](../model_catalog.json) · [Installation / 설치](portable_install.md)
