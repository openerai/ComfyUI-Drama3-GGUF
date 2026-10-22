# 컴퓨터 사양별 가이드

**현재 audio.cpp + Jmica GGUF 구성의 선택 출발점**입니다. 파일 크기는 VRAM 요구량이 아니며, 아래 표는 최소 사양·실행 보장이 아닙니다.

| 내 컴퓨터 | 어디서 시작할까 |
| --- | --- |
| RAM 16 GB 이하 / VRAM 8 GB 이하 | 이 구성에서 실행을 확인하지 않았습니다. Q2도 부족할 수 있어 외부 서버를 우선 검토합니다. |
| RAM 32 GB 이상 / VRAM 8–12 GB | Q2부터 짧은 TTS로 시험합니다. CPU 전문가 오프로딩·streaming을 검토하고 RAM·VRAM을 함께 봅니다. 8 GB 실행은 미확인입니다. |
| RAM 32–64 GB 이상 / VRAM 16 GB | Q2부터 시작하고 복제까지 메모리 피크를 확인합니다. 여유가 확인된 뒤 Q3·Q4를 비교합니다. |
| RAM 64 GB 이상 / VRAM 24 GB 이상 | Q3·Q4 비교 후보입니다. 큰 문맥·참조 음성도 추가 메모리를 쓰므로 짧은 입력부터 확인합니다. |
| CPU / Apple 통합 메모리 / 다른 GPU | 해당 엔진 빌드의 Drama3 지원이 필요합니다. CUDA 설정을 그대로 사용하지 않으며, 이 프로젝트의 실제 추론 검증 범위 밖입니다. |

**실제 확인 범위**
- Windows · RAM 128 GB · RTX 5070 Ti 16 GB: Q2로 TTS·수동/자동 받아쓰기 복제 실행 확인.
- 별도의 Windows · RAM 32 GB · VRAM 12 GB 구성: Q2·streaming 장문 TTS 74.7초 생성 기록. 해당 조합 전체의 품질 보장은 아닙니다.
- Q3·Q4와 다른 운영체제의 추론은 이 프로젝트에서 미검증입니다.

**부담을 줄이는 순서**
1. 일반 TTS와 짧은 문장으로 먼저 확인합니다.
2. SSD에 모델을 두고, disk_experts=true · expert_cache_size=8 · pin_experts=false를 출발점으로 검토합니다.
3. VRAM이 부족하면 CPU 전문가 오프로딩·코덱 CPU·streaming을 검토합니다. RAM 사용과 대기 시간은 늘 수 있습니다.
4. 자동 받아쓰기는 ASR 0.6B부터 시작합니다. 복제는 참조 음성 인코딩 때문에 TTS보다 메모리를 더 쓸 수 있습니다.

설정은 각 PC의 config.json에서 선택합니다. 이 안내는 설정을 자동 변경하지 않습니다.

[상세 설정](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/model_setup_KO.md) · [실제 검증 기록](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/verification.md)

[설치와 경로](https://github.com/openerai/ComfyUI-Drama3-GGUF/blob/main/docs/portable_install.md)
