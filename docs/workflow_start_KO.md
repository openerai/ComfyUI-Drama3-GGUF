# Drama3 GGUF · 시작 안내

텍스트로 음성을 만들거나 참조 녹음으로 목소리를 복제합니다. 이 워크플로우는 **Drama3 지원 audio.cpp 엔진 + GGUF 모델**을 사용합니다. 엔진과 모델은 별도로 준비하세요.

## Model Links · 모델 다운로드

아래에서 **GGUF 하나만** 선택합니다. 원본 TTS 체크포인트와 별도 코덱은 추가로 필요하지 않습니다.

- [Q2 전문가 / Q8 backbone · 15.88 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q2_K.gguf)
- [Q3 전문가 / Q8 backbone · 18.93 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q3_K_S.gguf)
- [Q4 전문가 / Q4 backbone · 21.78 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-4bit-experts-Q4_K_S.gguf)
- [Q4 전문가 / Q8 backbone · 22.91 GiB](https://huggingface.co/Jmica/Drama-3-GGUF/blob/main/drama-3-backbone-8bit-experts-Q4_K_S.gguf)

파일 크기는 RAM·VRAM 필요량과 다릅니다. 사양별 선택 기준은 **Hardware 노트**에 있습니다.

## Model Storage Location · 저장 폴더

아래는 **권장 배치 예시**입니다. 다른 폴더를 사용해도 config.json의 model_path로 지정할 수 있습니다.

```text
ComfyUI/
├─ models/
│  ├─ drama3/
│  │  └─ <선택한 파일명>.gguf
│  └─ asr/                     ← 자동 전사 Clone만
│     └─ qwen3_asr_0.6b_bf16.safetensors
└─ custom_nodes/
   ├─ ComfyUI-Drama3-GGUF/
   │  ├─ config.managed.example.json
   │  └─ config.json           ← 각 PC의 실행 설정
   └─ ComfyUI-Drama3/          ← 자동 전사용 네이티브 소스
```

**GGUF는 일반 Checkpoint Loader에서 선택하지 않습니다.** config.json의 model_path를 읽는 별도 audio.cpp 서버가 모델을 실행합니다. 워크플로우의 **Model ID=auto**는 서버에 등록된 모델을 고릅니다.

## Engine & Config · 엔진 연결

1. [호환 audio.cpp 빌드·설치 안내](https://github.com/openerai/ComfyUI-Drama3-GGUF#obtain-a-compatible-backend)에 따라 엔진을 준비합니다. CPU·CUDA 등은 해당 엔진의 지원을 확인합니다.
2. 처음 설치할 때만 config.managed.example.json을 config.json으로 복사합니다. 기존 설정이 있으면 필요한 항목만 수정하세요.
3. `mode=managed`, `executable=<준비한 엔진 경로>`, `backend=<사용할 백엔드>`를 지정합니다. 위 폴더 예시의 model_path는 다음과 같습니다.

```text
../../models/drama3/<선택한 파일명>.gguf
```

상대 경로는 config.json 폴더 기준입니다. 설정 변경 후 노드 폴더에서 ComfyUI Python으로 `python run_server.py --stop`을 실행하면 다음 생성부터 새 설정을 사용합니다. 외부 서버 연결은 **Server URL**을 지정하고 모델을 서버 쪽에 설치합니다.

## How to Use · 사용 순서

1. **일반 TTS:** Script & Direction이 있으면 그곳의 New speech text에, 없는 기본 버전은 Generate / Voice Clone의 New speech text에 읽을 대사를 적습니다.
2. **Clone:** Load Reference Audio → Trim으로 참조 구간을 고르고, Reference transcript에 **그 구간에서 실제로 말한 내용**을 적습니다.
3. **자동 전사 Clone만:** [ASR 모델 파일 목록](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/tree/main)에서 위 0.6B 파일(약 1.6 GB)을 받고 [Qwen3-ASR 노드](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)를 설치합니다. ASR Model에서 선택한 뒤 Reference Transcript만 **Run Branch**로 실행해 전사를 확인합니다.
4. Script & Direction이 있으면 감정·말투를 Direction에 입력합니다. 없는 기본 버전은 새 대사 앞에 `[친근한 말투로]`처럼 직접 적습니다. 참조 전사문에는 연기 지시를 넣지 않습니다. 상단 **Run**으로 생성하고 Save Audio에서 결과를 확인합니다.
5. Controls 버전은 생성 후 속도·볼륨·음량 정규화도 조절합니다. FFmpeg가 필요한 설정과 감정 예시는 **Guide 노트**를 보세요.

긴 생성·문맥·메모리 설정은 **Hardware 노트**, 전체 설치 설명은 **Setup 노트**에 있습니다. [전체 모델·사양 안내](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_KO.md)

2026-10-18 확인. 사양별 안내는 선택 출발점이며 모든 환경의 실행을 보장하지 않습니다.

## 출력 확인 · 0.1.11
일반 TTS의 reference_text는 비워두세요. 목소리·성별 선택 칸이 아닙니다. Voice Clone에서는 선택한 참조 녹음의 실제 대사를 입력합니다. 새 기본 Top K=4097은 종료 토큰을 포함한 전체 후보를 사용합니다. 이전 파일에 저장된 30은 자동 변경되지 않습니다. 생성 후 노드의 Raw output check에서 원본 길이·음량과 구간 예산 도달 가능성을 확인하고 직접 들어보세요. 무음·잡음을 증폭하는 것은 해결이 아닙니다.


## 0.2.0 설치 점검 · ASR 파일 형식
위 네 GGUF는 TTS용 선택 후보이며, Q2만 이 프로젝트에서 실제 추론을 검증했습니다. Qwen3-ASR은 별도의 받아쓰기 모델입니다. 변환된 `qwen3_asr_0.6b_bf16.safetensors` 단일 파일을 `models/asr`에 넣고 **Drama3 GGUF · ASR Model (Local File)**에서 선택합니다. 다른 확장의 원본 HF 폴더형 Qwen 로더와 혼용하지 마세요. 이 저장소의 고유 노드 `Drama3GGUFASRLoader` → `Drama3GGUFASRTranscribe`를 사용하며 타임스탬프·ForcedAligner는 필요 없습니다.
자동 전사에는 ComfyUI-Drama3의 고정 버전 네이티브 ASR 소스도 필요합니다. 외부 노드를 직접 수정하지 마세요. [범용 설치 절차](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)의 순서대로 준비하고, ComfyUI Python으로 `python check_install.py`와 `python install_workflows.py`를 실행하세요. 세 워크플로우가 **Drama3-GGUF-0.2.0** 폴더에 복사됩니다. 사용자 경로가 다르면 --comfy-root 또는 --workflow-dir를 지정합니다. 재시작·화면 새로고침 후 그 파일을 새로 여세요. 이전 화면의 Top K=30은 파일 업데이트만으로 바뀌지 않습니다. 새 예제는 4097이며 품질은 직접 재생해서 확인합니다.
