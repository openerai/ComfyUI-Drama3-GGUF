# ComfyUI Drama3 GGUF

Drama3 GGUF를 실행하는 audio.cpp 서버와 ComfyUI를 연결하는 노드입니다.
공유 워크플로우에는 특정 GPU·RAM 용량·사용자 경로·모델 파일명이 들어 있지 않습니다.

## 설치

1. ComfyUI의 `custom_nodes` 안에 이 저장소를 clone합니다.
2. **ComfyUI를 실행하는 Python 환경**으로 `requirements.txt`를 설치하고 ComfyUI를 재시작합니다.
3. 일반 TTS는 `example_workflows/Drama3_GGUF_TTS.json`, 음성 복제는
   `example_workflows/Drama3_GGUF_Voice_Clone.json`을 엽니다.

**audio.cpp 실행 파일과 GGUF 모델은 별도로 필요합니다.**
노드만 설치해도 추론 엔진이 자동 설치되는 구성은 아닙니다.
Windows 빌드 명령과 원본 다운로드 링크는 [영문 설치 안내](README.md#obtain-a-compatible-backend)에 있습니다.

## 각 PC의 설정

- **기존 서버 연결:** 기본 동작입니다. 노드의 `server_url`에 서버 주소를 넣습니다.
  비워 두면 `config.json` 또는 `http://127.0.0.1:8035`를 사용합니다.
- **자동 시작:** `config.managed.example.json`을 `config.json`으로 복사하고
  `executable`·`model_path`·`backend`를 본인 환경에 맞춥니다.
  상대 경로의 기준은 설정 파일이 있는 폴더입니다.
- **모델 선택:** `model_id=auto`는 서버에 Drama3 모델이 하나일 때 선택합니다.
  여러 모델이 있으면 사용할 ID를 지정합니다.
- **다른 GPU/메모리:** backend, device, CPU offload, codec 위치, 메모리 제한은
  각 PC의 `config.json`에서 조절합니다. 설정을 바꾸면 관리 서버를 재시작하세요.

관리 서버 종료는 노드 폴더에서 ComfyUI Python으로 실행합니다.

```sh
python run_server.py --stop
```

개인 설정, 로그, 모델, 오디오는 Git에 포함되지 않습니다.
관리 모드는 다른 프로세스나 다른 설정으로 실행 중인 서버를 자동으로 채택하지 않습니다.
기존 서버를 공유하려면 `external` 모드를 사용하세요.

## 메모리와 지원 범위

Windows 관리 모드는 실제 RAM 작업 집합과 private memory 한도를 적용합니다.
기본 RAM 작업 집합 목표는 총 RAM에 따라 2~8GiB로 조절되며,
예를 들어 32GiB에서는 4GiB입니다. 이 값은 **캐시 제한**이며 모델 실행 보장이 아닙니다.
가용 RAM이 설정한 기준 아래로 내려가면 해당 서버만 중단합니다.
자동 목표는 총 RAM을 기준으로 하므로, 다른 프로그램을 함께 쓰면
로컬 `working_set_gib`를 낮추고 관리 서버를 재시작해야 할 수 있습니다.
다른 OS에서는 감시 후 중단 기능만 적용되며 Windows의 하드 제한은 적용되지 않습니다.

실제 추론을 확인한 환경과 미확인 범위는 [검증 기록](docs/verification.md)에 적었습니다.
CPU·Vulkan·Metal 선택을 제공하지만 모든 환경에서의 추론 성공을 검증한 것은 아닙니다.
VRAM 부족 시 CPU offload가 가능하지만 RAM 사용량과 속도가 달라집니다.
복제는 참조 인코딩도 수행하므로 일반 TTS가 실행되는 설정에서도 VRAM이 부족할 수
있습니다. CPU 전문가 레이어 오프로딩과 코덱 설정은 각 PC에서 조절하세요.
지원하는 서버에서는 로컬 `run_mode=streaming`으로 코덱을 한 프레임씩 처리하고
완성된 WAV를 받을 수 있습니다. 기본은 `offline`이며, 변경 후 관리 서버를 재시작하세요.
최종 코덱 그래프 할당을 줄이는 선택지이며 모델 실행을 보장하지는 않습니다.
긴 글은 짧은 문장으로 나누어 생성하세요.

## 음성 복제

복제 전용 워크플로우는 **Load Audio → Trim Audio Duration → Reference Preview
→ Voice Clone → Save Audio**로 연결돼 있습니다. 참조 음성과 전사문이 모두
필수이므로 참조 없이 일반 TTS로 대신 실행하지 않습니다.

한 사람의 깨끗한 말소리 파일을 선택하고, `start_index`와 `duration`으로
5~10초 정도의 구간을 고릅니다. 단위는 초입니다. `reference_text`에는
**자른 구간에서 실제 말한 대사**, `text`에는 **새로 생성할 문장**을 적습니다.
참조 구간을 바꾸면 전사문도 맞춰 수정하세요. 공유 파일에는 녹음과 전사문이
없으므로 실행 전에 직접 선택해야 합니다.

복제 전에 참조만 들으려면 **Reference Preview 노드만 우클릭 → Run Branch**를
선택하세요. 해당 참조 경로만 실행해 재생기를 만들며 Voice Clone과 Save Audio는
실행하지 않습니다. 전사문을 확인한 뒤 상단 **Run**으로 전체 복제를 실행합니다.
ComfyUI 0.41.0 / frontend 1.55.17에서 실제 확인했습니다.

빈 음성·무음·NaN/Inf·여러 배치는 미리 거절합니다. 기본 참조 상한은 15초입니다.
더 긴 참조가 필요하면 서버의 문맥 용량을 확인한 뒤 로컬 설정의
`reference_max_seconds`를 조절하세요. 짧은 파일도 길이가 길면 기본 1024-token
문맥을 초과할 수 있습니다. 기존 TTS 노드도 전사문만 있고 오디오가 없으면 거절합니다.

참조는 설정한 서버에 WAV base64로 전송되며 5MiB 제한이 있습니다.
여러 화자·언어의 복제 품질은 아직 검증하지 않았습니다.

### 참조 대사 자동 전사

`example_workflows/Drama3_GGUF_Voice_Clone_Auto_Transcript.json`은 선택한 음성
구간을 **로컬 Qwen3-ASR → Reference Transcript → reference_text**로 연결합니다.
추가로 [ComfyUI-Drama3](https://github.com/PedroMarinhoDev/ComfyUI-Drama3)의
`Qwen3ASRLoader`·`Qwen3ASRTranscribe` 노드와 호환되는 Qwen3-ASR 모델이
`models/asr`에 필요합니다. ASR 모델은 ASR Model에서 직접 선택하세요.
이 저장소가 ASR 엔진이나 모델을 자동 설치·다운로드하지는 않습니다.
기존 수동 복제 워크플로우는 이 추가 의존성 없이 사용할 수 있습니다.

오디오 파일과 Trim 구간을 고른 뒤 **Reference Transcript만 우클릭 → Run Branch**로
전사를 확인합니다. 파일 업로드만으로는 전사를 실행하지 않습니다. 전체 **Run**에서는
전사와 복제가 차례로 실행됩니다. ASR과 복제는 동일한 잘린 음성을 사용합니다.
`Correction`은 빈칸이면 자동 인식을 사용하며, 내용을 적으면 정확한 전체 대사를
대신 사용합니다. **파일이나 구간을 바꾸면 Correction을 비우고 다시 확인하세요.**
`Used reference transcript`는 복제에 실제로 전달되는 대사입니다.

복제 노드의 `Reference transcript`는 **참조 녹음에서 실제로 한 말**이고,
`New speech text`는 **그 목소리로 새로 생성할 문장**입니다. 내부 입력 이름은
기존 `reference_text`·`text`를 유지해 저장된 워크플로우와 API가 호환됩니다.

`UNKNOWN`과 빨간 오류가 함께 보이면 노드 정의를 불러오지 못한 상태일 수 있습니다.
ComfyUI 시작 로그에서 import 오류와 노드 등록을 확인하고, 서버가 준비된 뒤
브라우저를 새로고침하세요. 라벨만 바꾸어 누락된 노드 오류를 숨기지는 않습니다.

코드 라이선스는 MIT입니다. audio.cpp와 모델에는 별도 조건이 적용됩니다.
[원본과 라이선스 안내](THIRD_PARTY_NOTICES.md)

## 연기·속도·음량 조절 (0.1.3)

예제의 **Script & Direction**에서 새 대사와 자연어 연기 지시·쌍 태그를 지정합니다.
Generate / Voice Clone에는 `temperature`·`top_p`·`top_k`를 추가했습니다.
**Audio Controls (Local)**은 생성 후 속도·볼륨·음량 정규화를 처리합니다.
후처리에는 FFmpeg가 PATH에 필요하며, `config.json`의 `ffmpeg_path`로도 지정할 수 있습니다.
기본 설정은 음성을 그대로 통과시키므로 FFmpeg가 없어도 기존 생성은 가능합니다.
각 워크플로우의 한국어 Guide 노트와 [조절 가이드](docs/controls_KO.md)에
기본값, 태그 예시, 캐시 재사용, Fish 웹앱과 다른 적용 범위를 적었습니다.

### 생성 길이 범위 (0.1.4)

특정 PC를 기준으로 둔 24초 상한을 제거했습니다. `max_seconds`는 모델의
262144개 문맥 위치와 코덱 프레임 비율로 계산한 범위(입력 상한 12173초)까지
설정할 수 있으며 기본값은 12초입니다. 이는 이론상 문맥 예산이지 해당 길이의
출력·품질 보장이 아닙니다. 입력·참조·이전 구간도 문맥을 함께 사용합니다.
각 서버에서 `fish_drama3.context_length`를 설정하며, 실행 불가능하면 문맥·메모리·
응답 시간 초과의 원인을 안내합니다. PC별 메모리 보호 한도를 자동으로 늘리지 않습니다.

생성 대기 시간은 `config.json`의 `request_timeout_seconds`로 설정합니다.
기본 600초이며, 0은 읽기 대기 제한을 해제합니다. 대기 시간이 초과돼도 서버는
계속 추론 중일 수 있으므로 상태를 확인하고 재시도하세요.
