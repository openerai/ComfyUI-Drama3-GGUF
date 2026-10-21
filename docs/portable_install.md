# Portable installation · 범용 설치 (0.2.0)

The Python bridge is tested on Windows, Linux and macOS. Actual audio inference
is verified on the Windows CUDA systems recorded in [verification.md](verification.md).
CPU, Metal and Vulkan need an audio.cpp build that supports Drama3 on that backend;
they are not certified by the bridge's Python tests. No GPU, driver or RAM size
is forced by a shared workflow. A compatible engine and sufficient memory are
still prerequisites. This is not a universal GPU support guarantee.

## 1. Use the Python that runs ComfyUI

Clone into the active installation's `custom_nodes`, then run in that directory:

```sh
git clone https://github.com/openerai/ComfyUI-Drama3-GGUF.git
cd ComfyUI-Drama3-GGUF
python -m pip install -r requirements.txt
```

Replace `python` with ComfyUI's venv Python or portable `python_embeded/python.exe`
as appropriate. Desktop's application folder and its actual ComfyUI installation
can differ: use the folder containing `main.py`, `custom_nodes` and `user`.
Do not replace PyTorch/CUDA to install this bridge.

## 2. Install the TTS engine and one GGUF

Prepare the [pinned audio.cpp build](../README.md#obtain-a-compatible-backend).
Windows CUDA has a checked build helper. For other systems use upstream's build
instructions for the same commit and supported backend, or connect to an external
compatible server. The repository does not distribute a prebuilt engine for every
OS/GPU and does not silently switch backends.

Choose one of the four original [Jmica packages](https://huggingface.co/Jmica/Drama-3-GGUF).
The About note's Q2/Q8 15.88 GiB, Q3/Q8 18.93 GiB, Q4/Q4 21.78 GiB and
Q4/Q8 22.91 GiB labels are disk sizes, not VRAM requirements. The packages include
the tokenizer/configuration/codec; this path does not need the original TTS
checkpoint or a separate codec. [model_catalog.json](../model_catalog.json)
records exact filenames, revisions, byte sizes and SHA256 values checked on 2026-10-21.
Only Q2 has this project's actual inference validation; the other three remain
documented choices, not equally tested recommendations.

For managed mode copy `config.managed.example.json` to `config.json` only on a
new installation and set `executable`, `model_path`, `backend` and any required
`library_dirs`. Relative paths are relative to that config file. External mode
uses the server's model path, not the client's. See the [model guide](model_setup_EN.md).

## 3. Optional automatic reference transcription

Plain TTS and manual cloning skip this step. Automatic cloning uses this
repository's **Drama3 GGUF · ASR Model (Local File)** and **Transcribe Reference**
nodes, with unique `Drama3GGUFASRLoader` / `Drama3GGUFASRTranscribe` IDs and a
`DRAMA3_GGUF_ASR_MODEL` socket. They cannot be overwritten by another extension's
`Qwen3ASRLoader` / `Qwen3ASRTranscribe`. No timestamps or forced aligner are used.

Install the optional native source beside this repository:

```sh
git clone https://github.com/PedroMarinhoDev/ComfyUI-Drama3.git
git -C ComfyUI-Drama3 checkout 67a733a96890637dc27b1914974ad00c569405fb
```

Run these two commands from `custom_nodes`, not inside `ComfyUI-Drama3-GGUF`.
An existing checkout should be inspected before changing its revision; do not
discard its local changes. **No edits to that repository are needed.** The adapter
loads its `qwen3_asr` implementation directly, without relying on its node registry.
No additional `qwen-asr` pip package is required. The native source uses ComfyUI's
existing Torch/Transformers runtime; the validation used ComfyUI 0.42.1.

Download the converted
[qwen3_asr_0.6b_bf16.safetensors](https://huggingface.co/PedroMarinhoDev/Qwen3-ASR-ComfyUI/blob/6ad8c9be026925839479a8d97749068a4202fbe9/qwen3_asr_0.6b_bf16.safetensors)
(1,564,928,184 bytes, about 1.6 GB) into `ComfyUI/models/asr`. This is an ASR file,
not the TTS model. The 1.7B converted file can also be selected; only 0.6B was
executed here. **A raw `Qwen/Qwen3-ASR-*` model directory belongs to a different
loader and is not interchangeable with this converted single file.**

For Desktop/shared storage add the shared `asr` directory to your existing
`extra_model_paths.yaml` (merge; do not replace other entries), for example:

```yaml
shared_asr:
  base_path: /path/to/shared/models
  asr: asr/
```

Use your own directory; forward slashes also work in Windows YAML paths. The
loader preserves registered extra paths. If the optional source has another
folder name, set `asr_backend_path` in private `config.json` to its repository
directory. Restart ComfyUI after changing source, model paths or node code.

## 4. Check and copy all three workflows

From `ComfyUI-Drama3-GGUF`, with ComfyUI's Python:

```sh
python check_install.py
python check_install.py --asr-model /path/to/qwen3_asr_0.6b_bf16.safetensors
python install_workflows.py
```

The second check is only for automatic transcription. Add `--comfy-root /path/to/ComfyUI`
if the checkout is not inside the actual `custom_nodes` folder. `check_install.py`
prints the Python/config/backend/model paths and checks the requested files;
it does not download, generate or start a server. `--probe-server` explicitly
checks `/v1/models`. `--workflow /path/to/file.json` detects saved old Top K and
ASR node IDs. Passing checks is not proof of intelligible speech or sufficient GPU memory.

The copy command installs **all three** examples into
`user/default/workflows/Drama3-GGUF-0.2.0`: TTS, manual Clone, automatic-transcript
Clone. It preserves existing files. For custom/multi-user storage pass
`--workflow-dir /path/to/user/workflows/Drama3-GGUF-0.2.0` instead.

**Restart ComfyUI, reload the frontend, then OPEN the versioned example.** Updating
a file does not update an already-open canvas. New examples use Top K=4097 and
optional normalization remains off. Old saved values are preserved; a loaded
non-4097 value gets an advisory message. Change the visible node's value and
save if upgrading an old graph. Missing custom node recovery must not substitute
another extension's similarly named ASR nodes.

For auto Clone choose a recording, trim a complete speech segment, and run the
Reference Transcript branch first. Inspect the recognized words; use Correction
only for a full corrected transcript of that same segment. Then run the graph.
The same selected audio feeds ASR and cloning. Listen to the final audio to
check the words, ending and voice. A successful job or a waveform is not an
audio-quality score.

## 한국어 핵심 안내

메모의 네 GGUF 후보는 맞으며, 파일 크기는 VRAM 요구량이 아닙니다. Qwen3-ASR 0.6B는
자동 받아쓰기 전용 **변환된 단일 파일**입니다. 원본 Hugging Face 모델 폴더용 로더와
혼용하지 마세요. 위 고정 버전의 ComfyUI-Drama3 소스와 함께 사용하며, 외부 노드 파일을
직접 고치지 않습니다. 이 저장소가 충돌 없는 고유 ASR 노드·소켓을 제공합니다.

실제 ComfyUI를 실행하는 Python으로 `check_install.py`를 실행하고,
`install_workflows.py`로 TTS·수동 복제·자동 받아쓰기 복제 세 파일을 모두 복사하세요.
ComfyUI 재시작·화면 새로고침 후 **Drama3-GGUF-0.2.0 폴더의 파일을 새로 열어야** 합니다.
열려 있던 이전 화면은 자동 변경되지 않습니다. 개인 모델 경로·메모리 설정은 config.json,
공유 ASR 경로는 extra_model_paths.yaml에 둡니다. 자동 다운로드·드라이버 교체·다른 확장
비활성화는 하지 않습니다. 다른 운영체제의 Python 검사 통과와 해당 장비의 실제 추론 검증은 구분합니다.
