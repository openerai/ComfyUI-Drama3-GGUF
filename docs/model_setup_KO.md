# 모델 다운로드와 사양별 설정

2026-10-18 확인. 아래 두 안내는 TTS·Clone 워크플로우의 Setup / Hardware 노트에도 들어 있습니다.

처음 설치한다면 워크플로우 왼쪽의 **About: Drama3 GGUF** 또는
[폴더 구조·사용 순서 안내](workflow_start_KO.md)부터 보세요.

## 1. 모델 다운로드·설치

### GGUF 모델 하나 선택

[Jmica / Drama-3-GGUF 파일 목록](https://huggingface.co/Jmica/Drama-3-GGUF/tree/main)에서 사용할 **GGUF 하나**를 받으세요. 아래 파일명 링크를 열고 Download를 누릅니다. 모두 audio.cpp용 패키지이며, 이 흐름에는 원본 Drama3 체크포인트·별도 코덱을 추가로 받을 필요가 없습니다.

| 파일 | 다운로드 크기 | 선택할 때 참고 |
| --- | --- | --- |
| [drama-3-backbone-8bit-experts-Q2_K.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf) | 15.88 GiB | 아래 기본 4종 중 가장 작은 파일 |
| [drama-3-backbone-8bit-experts-Q3_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf) | 18.93 GiB | Q8 backbone + Q3 전문가 |
| [drama-3-backbone-4bit-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf) | 21.78 GiB | backbone도 4bit인 별도 비교 후보 |
| [drama-3-backbone-8bit-experts-Q4_K_S.gguf](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf) | 22.91 GiB | Q8 backbone + Q4 전문가 |

용량은 **디스크 파일 크기**입니다. RAM·VRAM 필요량과 같지 않습니다. 파일 크기 순서로 GPU 메모리 사용량을 판단하지 마세요. 높은 비트 수가 발음·감정 표현의 개선을 보장하지도 않습니다. 모델 카드의 FP32-router/BF16 추가 프로파일은 고급 비교용이며, 이 노드의 고정 런타임에서 별도 검증하지 않았습니다.

### 저장 위치와 실행 엔진

1. GGUF를 예를 들어 `ComfyUI/models/drama3/`에 보관합니다. SSD는 디스크 전문가 읽기 속도에 도움이 됩니다. 다운로드 파일 외에 실행 도구·캐시·출력용 공간도 남겨 두세요.
2. **Drama3를 지원하는 audio.cpp 실행 파일도 별도로 필요합니다.** 일반 GGUF 텍스트 모델 로더에 연결하지 않습니다. [이 노드의 빌드·설치 안내](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)를 따라 호환 엔진을 준비합니다.
3. 자동 시작은 `custom_nodes/ComfyUI-Drama3-GGUF/config.managed.example.json`을 처음에만 `config.json`으로 복사한 뒤 `mode=managed`, `executable`, `model_path`, `backend`를 지정합니다. 기존 config.json이 있으면 필요한 항목만 수정하세요.
4. 위 예시 폴더를 사용했다면 model_path는 `../../models/drama3/<받은 파일명>.gguf`로 지정할 수 있습니다. 상대 경로 기준은 config.json 폴더입니다. 노드의 `model_id=auto`는 서버에 등록된 모델을 고르며, 디스크 파일을 직접 찾는 옵션이 아닙니다.
5. 외부 서버는 모델을 **서버 쪽에** 등록하고 `server_url`을 연결합니다. 클라이언트의 config.json으로 외부 서버 자원을 조절하지 않습니다.

### 자동 전사 Clone에만 추가할 모델

[Qwen3-ASR-ComfyUI 파일 목록](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main)에서 **qwen3_asr_0.6b_bf16.safetensors**(약 1.6 GB)를 받아 `ComfyUI/models/asr/`에 넣고 ASR Model에서 선택합니다. 이 자동 전사 워크플로우에는 [ComfyUI-Drama3의 네이티브 ASR 소스](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)도 필요합니다. 수동 전사 Clone과 일반 TTS에는 ASR이 필요 없습니다. ForcedAligner나 원본 TTS 가중치는 이 GGUF 워크플로우 때문에 받을 필요가 없습니다.

출처: [GGUF 모델 카드](https://huggingface.co/Jmica/Drama-3-GGUF), [ASR 모델 안내](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI). 모델 배포 라이선스는 해당 모델 카드에서 확인하세요.

## 2. 사양별 설정·문제 해결

### 사양에 따라 어디서 시작할까

아래는 **선택 출발점에 대한 제안**이며 최소 사양이나 실행 보장표가 아닙니다. 사용 가능한 RAM·VRAM, 다른 앱, 운영체제, 참조 길이·문맥·백엔드에 따라 결과가 달라집니다. 대부분의 조합은 이 프로젝트에서 실측하지 않았습니다.

| 환경 | 모델·설정 선택 출발점 |
| --- | --- |
| RAM 16 GB 전후 / VRAM 8 GB 이하 | 실행 미확인입니다. Q2도 맞지 않을 수 있습니다. 아래 고정 GPU 가중치 설명을 먼저 확인하고 CPU 또는 외부 서버도 검토하세요. |
| RAM 32 GB 전후 / VRAM 8–12 GB | 작은 파일부터 시험하려면 Q2 후보. disk_experts=true, cache=8, pin_experts=false로 시작하고 여유 메모리를 관찰합니다. |
| RAM 32–64 GB / VRAM 16 GB 전후 | Q3/Q8 또는 Q4/Q4를 비교할 후보. 파일 크기보다 실제 메모리 피크를 보고 선택합니다. |
| RAM 64 GB 이상 / VRAM 24 GB 이상 | Q4/Q8도 비교할 후보. 여유가 확인된 뒤 전문가 캐시나 문맥을 확대합니다. |
| CPU·다른 GPU 백엔드 | CPU용 엔진 또는 해당 Metal/Vulkan 빌드의 Drama3 지원을 확인합니다. NVIDIA CUDA 설정을 그대로 적용하지 마세요. 통합 메모리는 RAM과 GPU가 같은 용량을 공유합니다. |

이 프로젝트의 실제 장문 확인은 **RAM 32 GB·VRAM 12 GB의 한 Windows CUDA 구성에서 Q2와 streaming으로 74.7초 TTS 생성**한 범위입니다. 위 표 전체나 장문 Clone의 성공을 의미하지 않습니다. [실행 검증 기록](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

### 조정할 설정

설정은 각 설치의 `config.json`에 둡니다. 기존 옵션을 보존하며 필요한 항목을 합쳐 수정하세요. 변경 후 노드 폴더에서 ComfyUI의 Python으로 `python run_server.py --stop`을 실행하면 관리 서버가 다음 생성 때 새 설정으로 시작됩니다.

- **백엔드:** `backend=cuda`는 호환 NVIDIA CUDA 엔진, `cpu`는 CPU 엔진입니다. `metal`·`vulkan`은 해당 빌드 지원을 확인합니다.
- **session_options:** 메모리가 민감하면 `fish_drama3.disk_experts=true`, `fish_drama3.expert_cache_size=8`, `fish_drama3.pin_experts=false`를 출발점으로 삼습니다. 전체 전문가를 RAM에 고정하는 pin 옵션은 충분한 여유를 실측한 뒤 검토합니다.
- **GPU가 부족할 때:** `fish_drama3.codec_backend=cpu`와 `fish_drama3.cpu_expert_layers` 증가를 검토합니다(계층 수 0–40). CPU/RAM 사용과 대기 시간이 늘 수 있습니다. 디스크 모드의 전문가 오프로딩은 제한된 전문가 캐시를 옮기는 것으로, attention·공통 backbone·audio tower까지 CPU로 이동시키지는 않습니다. 아주 작은 GPU에서 실행을 보장하지 않습니다.
- **코덱 메모리:** 관리 config.json의 최상위 `run_mode=streaming`은 지원 런타임에서 코덱을 프레임 단위로 처리하고 완성 WAV를 반환합니다. 기본 `offline`보다 최종 코덱 그래프 메모리를 줄이는 선택지이며, 참조 인코딩이나 모델 전체의 실행을 보장하지는 않습니다. 변경 후 관리 서버를 재시작하세요.
- **긴 생성:** 기본 `fish_drama3.context_length=4096`은 시작값입니다. 워크플로우의 Max seconds=47은 구간당 예산이고 전체 음성 길이 상한이 아닙니다. 입력·참조·이전 구간·다음 생성 예산이 같은 문맥을 사용합니다. 더 큰 예산에는 더 큰 문맥·작업 메모리가 필요할 수 있습니다. `request_timeout_seconds=0`은 HTTP 응답 대기 제한만 해제합니다.
- **생성 후 길이·품질:** 한도 도달 경고가 나면 대사 끝을 확인하세요. 문맥 설정과 별개로 모델이 반복·누락할 수 있으며, 같은 시드도 양자화·CPU/GPU 배치를 바꾸면 결과가 달라질 수 있습니다.

### 오류가 나면 확인할 곳

| 메시지·현상 | 먼저 확인 |
| --- | --- |
| 문맥 용량 초과 | session_options의 context_length를 늘리고 관리 서버 재시작. 참조·이전 구간의 사용량도 포함합니다. |
| CUDA/메모리 할당 실패 | 실제 VRAM과 RAM을 함께 확인. Windows에서는 `memory.private_limit_gib`에 걸릴 수도 있습니다. GPU 오프로딩과 private 상한 중 실제 원인을 구분합니다. |
| RAM 보호로 중단 | 다른 앱 점유와 `memory.working_set_gib`를 확인하고 점유 목표를 줄입니다. 최소 여유 RAM 보호를 없애서 해결하지 않습니다. |
| 응답 대기 시간 초과 | 서버가 아직 생성 중인지 확인. 필요하면 request_timeout_seconds를 늘리거나 0으로 설정합니다. |

private 한도는 실제 RAM 점유 한도와 다릅니다. 필요한 자원 한도는 각 설치에서 선택하며, 이 안내나 워크플로우가 사용자 설정을 자동 변경하지 않습니다.

출처: [이 프로젝트의 검증 기록](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md), [고정 audio.cpp 버전의 Drama3 안내](https://github.com/0xShug0/audio.cpp/blob/ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f/docs/models/fish_drama3.md), [GGUF 배포자의 검증 범위](https://huggingface.co/Jmica/Drama-3-GGUF#validation-limits). 파일 용량은 2026-10-18 공개 메타데이터 기준이며 변경될 수 있습니다.


## 0.2.0 설치 점검 · ASR 파일 형식
위 네 GGUF는 TTS용 선택 후보이며, Q2만 이 프로젝트에서 실제 추론을 검증했습니다. Qwen3-ASR은 별도의 받아쓰기 모델입니다. 변환된 `qwen3_asr_0.6b_bf16.safetensors` 단일 파일을 `models/asr`에 넣고 **Drama3 GGUF · ASR Model (Local File)**에서 선택합니다. 다른 확장의 원본 HF 폴더형 Qwen 로더와 혼용하지 마세요. 이 저장소의 고유 노드 `Drama3GGUFASRLoader` → `Drama3GGUFASRTranscribe`를 사용하며 타임스탬프·ForcedAligner는 필요 없습니다.
자동 전사에는 ComfyUI-Drama3의 고정 버전 네이티브 ASR 소스도 필요합니다. 외부 노드를 직접 수정하지 마세요. [범용 설치 절차](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)의 순서대로 준비하고, ComfyUI Python으로 `python check_install.py`와 `python install_workflows.py`를 실행하세요. 세 워크플로우가 **Drama3-GGUF-0.2.0** 폴더에 복사됩니다. 사용자 경로가 다르면 --comfy-root 또는 --workflow-dir를 지정합니다. 재시작·화면 새로고침 후 그 파일을 새로 여세요. 이전 화면의 Top K=30은 파일 업데이트만으로 바뀌지 않습니다. 새 예제는 4097이며 품질은 직접 재생해서 확인합니다.
