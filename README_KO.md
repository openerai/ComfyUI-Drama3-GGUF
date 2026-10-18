# ComfyUI Drama3 GGUF

Drama3 GGUF를 실행하는 audio.cpp 서버와 ComfyUI를 연결하는 노드입니다.
공유 워크플로우에는 특정 GPU·RAM 용량·사용자 경로·모델 파일명이 들어 있지 않습니다.

## 설치

1. ComfyUI의 `custom_nodes` 안에 이 저장소를 clone합니다.
2. **ComfyUI를 실행하는 Python 환경**으로 `requirements.txt`를 설치하고 ComfyUI를 재시작합니다.
3. `example_workflows/Drama3_GGUF_TTS.json`을 엽니다.

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
긴 글은 짧은 문장으로 나누어 생성하세요.

참조 음성을 쓰려면 Load Audio를 `reference_audio`에 연결하고 정확한 전사문을 입력하세요.
참조는 설정한 서버에 WAV base64로 전송되며 5MiB 제한이 있습니다.
여러 화자·언어의 복제 품질은 아직 검증하지 않았습니다.

코드 라이선스는 MIT입니다. audio.cpp와 모델에는 별도 조건이 적용됩니다.
[원본과 라이선스 안내](THIRD_PARTY_NOTICES.md)
