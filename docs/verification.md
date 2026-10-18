# Verification record

Recorded on 2026-10-18 for the initial 0.1.0 source release.
These results describe executed checks, not universal hardware compatibility.

## Actual ComfyUI inference

The installed node and the generic `Drama3_GGUF_TTS.json` workflow were exercised
through ComfyUI's queue API with a real audio.cpp server, not a mock server.

| Item | Observed result |
| --- | --- |
| OS | Windows |
| GPU | NVIDIA GeForce RTX 3080 Ti, 12 GiB VRAM |
| System RAM | 32 GiB installed |
| ComfyUI / Python | 0.41.0 / 3.12.9 |
| PyTorch | 2.10.0, CUDA 13.0 build |
| audio.cpp | `ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f`, CUDA backend |
| Model | Jmica Drama-3-GGUF, `drama-3-backbone-8bit-experts-Q2_K.gguf` |
| Input | `안녕하세요. 오늘도 좋은 하루 보내세요.` |
| Request settings | seed 123, maximum 12 seconds, automatic model selection |
| Queue result | Success; FLAC output, 44,100 Hz, 3.855 seconds |
| Measured wall time | 60.52 seconds, including managed server/model startup |
| Signal RMS | 0.2782; output was not silent |
| Applied Windows limits | 4 GiB working set, 10 GiB private memory |
| Sampled peak server RSS | Approximately 4.00 GiB |
| Minimum sampled system available RAM | Approximately 3.30 GiB |

The launcher reported that Windows hard memory limits were applied. Sampling
does not measure every transient allocation or VRAM usage. Timing and available
RAM depend on concurrent applications, storage, backend build, and model settings.
This checks successful audio production; it is not a perceptual speech-quality score.

### Repeated UI run and local RAM tuning

A subsequent run from the ComfyUI browser hit the available-RAM guard with the
4 GiB cache target: sampled available RAM fell to approximately 2.87 GiB, below
the configured 3 GiB threshold. The launcher stopped its server as intended.
This demonstrates that a target based on total RAM alone cannot account for
other running applications.

Only this installation's private configuration was then changed to
`memory.working_set_gib=3`; the 3 GiB available-RAM threshold and public defaults
were retained. A new browser run with blank `server_url` and `model_id=auto`
completed successfully: 44,100 Hz FLAC, 3.8545 seconds of audio, and 57.479 seconds
of execution including server startup. Windows hard limits were applied, with
approximately 3.00 GiB peak server RSS and 5.01 GiB minimum sampled available RAM.
This is a successful short repeat, not a long-running stability guarantee.

The tested model was separately downloaded from revision
`17a5b40c5dc2c2be986f5371a7e650108b828e29`, with SHA-256
`041be86fbb53bf4002d59bf7d5f0c99c321e0b21f5aa3b53fec380eec6f892d3`.
No model, generated audio, personal configuration, or backend binary is distributed here.

## Client and runtime checks

A separate, clean Python virtual environment on Windows installed
`requirements.txt`, NumPy, and Ruff. All 14 unittest cases and `ruff check .` passed.

The checks cover relocated configuration paths, automatic/explicit RAM settings,
missing explicit configuration, managed localhost restrictions, ambiguous and
unrelated model selection, external mode without process startup, managed process
and model/configuration identity, inline reference encoding and size/transcript
validation, cross-process launcher locking, reused-PID rejection, and termination
of a real child process through a Windows Job Object.

The HTTP audio/reference round-trip test uses an actual loopback HTTP connection
to a test fixture; it does **not** perform model inference or prove voice cloning.
The Windows build helper was parsed successfully. The existing pinned CUDA backend
was used for real inference; a fresh backend build was not repeated for this release.

GitHub Actions [run 39092405264](https://github.com/openerai/ComfyUI-Drama3-GGUF/actions/runs/39092405264)
passed on Windows, Linux, and macOS for code commit `a504e07`.
The first CI run exposed a test assertion comparing temporary-directory aliases
as raw strings (Windows short paths and macOS `/var` symlinks). The assertion was
corrected to compare canonical resolved paths. Runtime behavior did not change.
These jobs do not install ComfyUI or run a model. The Windows-only Job Object
test is skipped on other operating systems. See the [Actions page](https://github.com/openerai/ComfyUI-Drama3-GGUF/actions)
for the actual status of subsequent commits.

## Independent review

The Gravitas verification skill was used with a separate reviewer who inspected
the implementation, workflow, documentation, and executed boundary checks.
Two issues found during review were fixed before publication:

- Automatic model selection could accept a model without a confirmed Drama3 family.
  It now requires `fish_drama3`; known other families are also rejected for explicit IDs.
- Managed mode could connect to an unrelated server already using the configured
  port. It now verifies the process creation time, executable, configuration, memory
  settings, and server-reported model before reusing a managed server.

Regression tests cover both cases. The reviewer found no additional publication-blocking
defects in the revised version. This review is not a certification or a guarantee.

## Not yet verified

- Real inference on GPUs other than the listed RTX 3080 Ti, or on 16 GiB RAM systems.
- Real CPU, Vulkan, Metal, Linux, or macOS inference.
- Other GGUF quantizations, long-form reliability, concurrent requests, or performance at scale.
- Perceptual voice similarity, and cloning quality across speakers or languages.

The shared workflow contains no GPU model, RAM capacity, user directory, or fixed
quantization filename. Each installation supplies its backend/model/memory settings.
That portability is configuration behavior, not evidence that every machine can run Drama3.

## Voice clone workflow checks (0.1.1)

The additional clone workflow was reviewed independently through Gravitas and
checked against the pinned audio.cpp speech protocol and Drama3 session code.
Both reference audio and its transcript are now required by `Drama3GGUFClone`.
The existing TTS node rejects a transcript without audio. Multiple audio batches,
empty/silent references, NaN/Inf, invalid sample rates, and references over the
default 15-second limit are rejected before an HTTP generation request.

All 22 client/runtime/input-boundary unit tests and Ruff passed locally on Windows,
including configuration of the streaming execution mode.
The node boundary tests isolate ComfyUI/Torch imports; they are not model inference.
A real ComfyUI submission with a missing reference returned HTTP 400 before inference.

The complete Load Audio → Trim Audio Duration → Preview Audio → Voice Clone →
Save Audio graph was installed in ComfyUI. In the actual frontend, right-clicking
only Reference Preview and choosing Run Branch produced a successful history entry
whose selected output IDs were only `["12"]`. The clone and output-save branches
were not executed. The trimmed reference player showed approximately 7 seconds.

A user-selected Korean reference was transcribed locally with the already installed
Qwen3-ASR 0.6B model. A 7.75-second segment ending with a complete sentence was selected.
The recording, its path, and its transcript are not included in this repository.

Initial full-generation attempts on the listed 12 GiB GPU failed with CUDA allocation
errors, including allocation of a 511.88 MiB codec decode graph. Ordinary TTS success
does not prove that a reference-conditioned request fits the same resource settings.
An offline retry with 16 CPU expert layers still failed when allocating a
624.95 MiB codec decode graph. Increasing the process memory limit was not needed
for the successful streaming test below.

### Completed reference-conditioned generation

Using the same model and pinned backend, the full clone graph completed with
local `run_mode=streaming`. The pinned server runs the streaming model internally,
decodes one codec frame at a time, and returns a final WAV to the existing HTTP
client. This avoids allocating the offline whole-utterance codec decode graph;
it is not an SSE client or live playback implementation.

The successful installation used CUDA, 4 threads, disk experts, an expert cache
of 8, 16 CPU expert layers, a 1024-token context, and `codec_backend=same`.
The Windows limits remained a 3 GiB working set, 10 GiB private commit, and
3 GiB minimum available system RAM. These are test conditions, not shared
workflow requirements or recommendations for every PC.

- The 7.75-second private Korean reference and its locally extracted transcript
  were supplied to the dedicated clone node. The target was a different sentence.
- The full ComfyUI request succeeded in 110.81 seconds of request wall time
  and saved 5.15483 seconds of 44,100 Hz FLAC audio. Samples were finite
  and non-silent (RMS 0.10266).
- Twenty-five samples taken approximately four seconds apart recorded 9,850 MiB
  peak total GPU use, 9.773 GiB peak server private commit, 3.00 GiB peak server
  RSS, and 5.684 GiB minimum available system RAM. Sampling can miss short peaks;
  total GPU use includes other processes.
- Local Qwen3-ASR 0.6B recovered the target sentence, differing only in word
  spacing. This checks speech content, not voice identity or perceptual quality.
- Running the same graph in the browser reused the generated audio cache and
  displayed the reference and generated-audio players. This was not a second
  independent inference or a long-running stability test.

This establishes one successful reference-conditioned Korean request on the
listed PC. Voice resemblance still needs listening assessment. No recording,
personal transcript, private path, or generated audio is published here.
