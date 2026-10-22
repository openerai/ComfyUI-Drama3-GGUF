import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const labels = {
    reference_audio: "Reference audio · 참조 음성",
    reference_text: "Reference transcript · 일반 TTS는 비움 / 복제는 녹음의 실제 대사",
    text: "New speech text · 새로 생성할 문장",
    seed: "Seed · 생성 시드",
    control_after_generate: "Seed after run · 실행 후 시드 변경",
    max_seconds: "Chunk budget (s) · 구간당 생성 한도(목표 길이 아님)",
    server_url: "Server URL · 서버 주소(빈칸: 로컬 설정)",
    model_id: "Model ID · 모델 선택(auto: 자동)",
    transcript: "ASR transcript · 자동 인식한 대사",
    correction: "Correction · 전사 수정(빈칸: 자동 인식 사용)",
    direction: "Direction · 연기 지시(괄호 없이 입력)",
    delivery: "Delivery tag · 전체 문장의 표현 태그",
    temperature: "Temperature · 표현 변화량",
    top_p: "Top P · 후보 확률 범위",
    top_k: "Top K · 후보 개수",
    speed: "Speed · 재생 속도(음정 유지)",
    volume_db: "Volume dB · 출력 볼륨",
    normalize_loudness: "Normalize loudness · 출력 음량 정규화",
    target_lufs: "Target LUFS · 정규화 목표 음량",
    model_name: "ASR model file · 받아쓰기 모델 파일",
    max_new_tokens: "ASR token budget · 받아쓰기 토큰 한도",
};

function labelNode(node) {
    if (!node.comfyClass?.startsWith("Drama3GGUF")) return;
    for (const item of [...(node.widgets ?? []), ...(node.inputs ?? [])]) {
        if (labels[item.name]) item.label = labels[item.name];
    }
}

app.registerExtension({
    name: "Drama3GGUF.TranscriptAndLabels",
    nodeCreated(node) {
        labelNode(node);
        const transcript = node.comfyClass === "Drama3GGUFReferenceText";
        const generation = ["Drama3GGUFGenerate", "Drama3GGUFClone"].includes(node.comfyClass);
        if (!transcript && !generation) return;
        const preview = ComfyWidgets.STRING(node, transcript ? "used_reference_text" : "generation_status",
            ["STRING", { multiline: true }], app).widget;
        preview.label = transcript ? "Used reference transcript · 실제 복제에 쓰는 대사"
            : "Raw output check · 원본 출력 확인(재생 필요)";
        preview.serialize = false;
        preview.options.serialize = false;
        preview.options.read_only = true;
        const element = preview.element ?? preview.inputEl;
        if (element) element.readOnly = true;
        if (generation) {
            const previousConfigure = node.onConfigure;
            node.onConfigure = function (...args) {
                const result = previousConfigure?.apply(this, args);
                const topK = this.widgets?.find(widget => widget.name === "top_k")?.value;
                if (Number.isInteger(topK) && topK !== 4097) {
                    preview.value = `Saved Top K=${topK}. For silence-prone takes, set Top K=4097.\n`
                        + "저장된 이전 값입니다. 현재 노드 값을 바꾸고 저장하세요. Updating files does not change an open canvas.";
                }
                return result;
            };
        }
        const onExecuted = node.onExecuted;
        node.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            preview.value = message.text?.[0] ?? "";
            this.setDirtyCanvas(true, true);
        };
    },
    loadedGraphNode(node) {
        labelNode(node);
    },
});
