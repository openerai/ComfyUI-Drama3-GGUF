# 현재 audio.cpp용 모델

Jmica 배포본 기준입니다. 다른 Drama-3 GGUF는 전용 엔진이나 패치가 필요할 수 있습니다.


**음성 생성(TTS): GGUF 하나만 받으세요.**

| 다운로드 | 디스크 크기 | 이 프로젝트 확인 |
| --- | ---: | --- |
| [Q2 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | 실제 실행 확인 |
| [Q3 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | 미검증 선택지 |
| [Q4 / Q4 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | 미검증 선택지 |
| [Q4 / Q8 backbone](https://huggingface.co/Jmica/Drama-3-GGUF/blob/17a5b40c5dc2c2be986f5371a7e650108b828e29/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | 미검증 선택지 |

**자동 받아쓰기 복제만: ASR 하나를 추가합니다.** 일반 TTS·수동 복제에는 필요 없습니다.

| 다운로드 | 디스크 크기 | 이 프로젝트 확인 |
| --- | ---: | --- |
| [Qwen3-ASR 0.6B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors) | 1.46 GiB | 실제 실행 확인 |
| [Qwen3-ASR 1.7B](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_1.7b_bf16.safetensors) | 3.80 GiB | 미검증 선택지 |

**저장 위치**
- GGUF → `models/drama3/`에 두고 config.json의 model_path로 지정
- ASR → `models/asr/`에 두고 ASR Model (Local File)에서 선택

ASR은 **변환된 단일 safetensors**입니다. 다른 확장의 원본 HF 폴더용 로더와 혼용하지 마세요.

GiB는 디스크 크기이며 RAM·VRAM 요구량이 아닙니다. GGUF 안에 코덱이 들어 있고, 호환 audio.cpp 엔진은 별도입니다.

[전체 파일명·고급 GGUF·해시](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_downloads.md) · [모델·사양 안내](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_KO.md)

사양·연기·메모리 설명은 상단 **자세한 설명 접기/펼치기** 버튼으로 봅니다.