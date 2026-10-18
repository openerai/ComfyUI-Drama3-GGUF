# Drama3 조절 가이드

공유된 세 예제에 Script & Direction, 모델 샘플링 값, Audio Controls (Local),
한국어 Guide 노트를 추가했습니다. 기존 노드 이름과 입력 API는 유지합니다.

| 항목 | 이 워크플로우에서의 의미 |
| --- | --- |
| Direction | 새 대사 앞에 `[자연어 연기 지시]`를 붙입니다. |
| Delivery tag | 짧은 문장 전체를 선택한 쌍 태그로 감쌉니다. 한 단어만 바꾸려면 본문에 직접 태그를 적습니다. |
| Temperature / Top P / Top K | 로컬 Drama3 서버에 전달하는 생성 샘플링 값입니다. 기본 1.0 / 0.9 / 30입니다. |
| Speed | 생성 후 FFmpeg atempo로 음정을 유지하며 속도를 바꿉니다. 1.2는 빠르게, 0.8은 느리게입니다. |
| Volume dB | 생성 후 볼륨입니다. 0은 유지, 음수는 작게, 양수는 크게입니다. |
| Normalize loudness / Target LUFS | 로컬 EBU R128 음량 정규화입니다. 기본 목표 -16 LUFS는 이 노드의 설정입니다. |

새로 말할 문장은 **Script & Direction**에, 녹음의 실제 대사는 **Reference transcript**에
적습니다. 연기 지시는 참조 전사문에 넣지 않습니다. 예를 들어 Direction에
`친근하고 편안한 안내 말투로`, 본문에 `오늘은 <emphasis>새로운</emphasis> 시작입니다.`를
적을 수 있습니다. 본문에서 단어별 태그를 직접 쓸 때 Delivery는 `none`으로 둡니다.
Delivery 선택값은 문장 전체에 적용됩니다. 공식 문법은
[Drama3 안내](https://docs.fish.audio/features/text-to-speech/drama-3)를 참고하세요.

태그와 연기 지시의 효과는 목소리와 대사에 따라 달라집니다. 짧은 문장부터 비교하세요.
이 로컬 서버의 기본 200자 청크는 긴 쌍 태그의 범위를 이어서 관리하지 않습니다.
Delivery를 선택하면 지시와 태그를 포함해 200자를 넘는 입력은 거절합니다.
수동으로 긴 태그 문장을 쓸 때도 문장을 나눠 주세요.

샘플링 값은 기본값부터 한 번에 하나씩 바꾸세요. 이 네이티브 런타임은 Top P=0,
Top K=0을 받지 않습니다. Temperature를 매우 낮추면 침묵이나 반복이 생길 수 있으며,
0도 모든 반복 방지 경로가 완전히 결정적인 것은 아닙니다. Seed 고정은 비교에 도움이
되지만 서로 다른 장비·백엔드의 동일 출력을 보장하지 않습니다.

오디오 처리 순서는 **속도 → 음량 정규화 → 볼륨 → 피크 제한(0.98)**입니다.
정규화 후 볼륨을 올리면 최종 LUFS도 바뀌고, 큰 피크는 제한됩니다. 목표 LUFS는 모든
짧은 녹음에서 정확히 달성되는 값이라는 뜻은 아닙니다. 기본 1x / 0dB / 정규화 끔은
샘플을 그대로 통과시킵니다. 그 외 설정에는 FFmpeg가 PATH에 필요합니다. 로컬
`config.json`의 `ffmpeg_path`로 실행 파일을 지정할 수도 있습니다. 속도·음량만 바꾸면
같은 그래프의 생성 음성을 재사용할 수 있습니다. 전사만 Run Branch로 따로 실행하면
ComfyUI가 이전 생성 캐시를 비울 수 있습니다.

## Fish 웹앱과의 차이

2026-10-18에 로그인하지 않은 실제 [웹앱](https://fish.audio/ko/app/text-to-speech/)에서
Drama3는 볼륨·속도, S2.1 Pro는 음량·텍스트 정규화와 태그 호환 모드도 표시하는 것을
확인했습니다. 전달받은 스크린샷은 S2.1 Pro가 선택된 상태였습니다.

이 구현은 Fish 클라우드 API를 호출하지 않습니다. 로컬 오디오 후처리는 웹서비스와
같은 알고리즘이라는 뜻이 아닙니다. 숫자·날짜를 발화 단어로 바꾸는 클라우드
텍스트 정규화, 자동 태그, S2.1 태그 호환 모드를 그대로 복제하지 않았습니다.
읽기 어려운 숫자·단위는 원하는 발음대로 직접 적으세요.
[Fish API](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)는
텍스트 정규화와 오디오 prosody를 별개로 설명합니다. native tokenizer의 NFC 처리는
이 숫자 읽기 기능과 다릅니다.

음량 처리는 [FFmpeg atempo](https://ffmpeg.org/ffmpeg-filters.html#atempo)와
[loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)을 사용하며 원래 샘플링률과
채널 수를 유지합니다. 단일 AUDIO 배치만 처리하고 여러 배치는 명확히 거절합니다.
