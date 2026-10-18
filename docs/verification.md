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

## Automatic reference transcript and labels (0.1.2)

The optional auto-transcript workflow was tested in the same Windows/ComfyUI
installation with the already installed Qwen3-ASR 0.6B model and the ASR nodes
from ComfyUI-Drama3. No ASR implementation or weights were copied into this
package. The manual clone example is unchanged and needs no ASR dependency.

- A reference-only request completed in 8.41 seconds of observed request wall
  time. The detected Korean transcript matched the previously checked 7.75-second
  reference segment. Both ASR and Voice Clone receive Preview Audio's same output.
- The subsequent full graph used the cached transcript and completed a fresh
  clone generation: 127.585 seconds of Comfy execution, with 5.15483 seconds of
  finite, non-silent 44,100 Hz FLAC output. This is not a benchmark of a single
  cold-start ASR-plus-clone request.
- Immediately after cloning, changing the ASR token cap forced another ASR
  inference while the native server still held its model. It succeeded in
  6.33 seconds of observed request wall time and recovered the same transcript.
  Four samples of that phase observed total GPU use up to 11,423 MiB and
  available system RAM down to about 4.11 GiB. This verifies one repeat on this
  PC, not that every ASR/model combination can coexist in VRAM.
- A browser Run Branch on Reference Transcript displayed the recognized text
  without running Voice Clone. Blank Correction uses ASR; a nonblank full
  correction replaces it. Empty recognition without a correction is rejected.
  Changing audio/trim requires clearing any old manual correction and reviewing
  again, as stated in the node tooltip and both READMEs.
- The real frontend displayed distinct bilingual labels for the reference
  transcript and new speech text, with the original input/API names preserved.
  `UNKNOWN` fallback widgets are not relabeled to hide missing node definitions.
- After displaying a private transcript and saving through the frontend, the
  Reference Transcript node stored only its blank Correction. The generated
  preview text was absent from both widget values and the saved workflow text.
  Both `widget.serialize` and `widget.options.serialize` are disabled on that
  display widget; a saved reference filename or an intentional correction still
  belongs to the user's workflow.

All 25 unit tests, Ruff, and the JavaScript syntax check passed locally. Gravitas
independent review identified the separate frontend workflow/API serialization
flags; both were fixed before publication. The readonly preview uses the
frontend's `read_only` option; its Correction field is the editable input.
Real ASR/clone inference on other hardware and long-running repeats remain
unverified.

## Direction, sampling and local audio controls (0.1.3)

The actual anonymous Fish web app was inspected on 2026-10-18. With Drama3
selected, its settings showed volume and speed. S2.1 Pro additionally showed
loudness normalization, text normalization and tag compatibility. The supplied
screenshot had S2.1 Pro selected. The Drama3 tag menu and
[official guide](https://docs.fish.audio/features/text-to-speech/drama-3)
support natural-language bracket directions and the paired tags whisper,
emphasis, soft, fast, slow, stress and forceful. This implementation passes
those directions/tags to the local backend; it does not call Fish's cloud API.

All 32 unit tests and Ruff passed locally on Windows, including real FFmpeg
tests of pitch-preserving 1.25x tempo, stereo channel preservation, dB gain,
normalization, limiting and original sample-rate restoration. JavaScript syntax
checking passed. DSP tests that need FFmpeg are skipped when it is unavailable;
the portable CI jobs are not model inference tests. An independent Gravitas
reviewer inspected the new code and ran all five audio-control tests with FFmpeg.
Nondefault sampling values and literal direction/tag text were also checked
through a loopback HTTP fixture; that fixture is not actual model inference.

The installed ComfyUI then completed a fresh real TTS request on the same PC,
model and streaming backend described above. Script & Direction supplied
`[차분하고 또렷한 안내 말투로] 안녕하세요. <emphasis>오늘도</emphasis> 좋은 하루 보내세요.`
with sampling defaults 1.0 / 0.9 / 30. Generate fed both a raw preview and the
new Audio Controls node, then Save Audio. The real request completed in 75.507
seconds of Comfy execution, about 76.14 seconds of observed request/poll wall time.

| Actual output | Duration | Sample rate | Sample peak |
| --- | --- | --- | --- |
| Raw generated audio | 4.73687 s | 44,100 Hz | — |
| Speed 1.2, normalization on, -16 LUFS target, gain -3 dB | 3.95345 s | 44,100 Hz | 0.59476 |
| Speed 0.8, normalization off, gain -6 dB | 5.90202 s | 44,100 Hz | 0.38641 |

All three files were reopened and their samples were finite and non-silent.
Local Qwen3-ASR 0.6B recovered the intended spoken sentence from the raw output,
without the acting direction or tag syntax, in 5.5 seconds of observed ASR
inference time. This is an ASR content check, not a listening assessment.
The second full-graph request changed only Audio Controls. Its history listed
Script and Generate as cached, with no new model generation. Comfy execution
took 0.142 seconds; observed request/poll wall time was about 2 seconds. The
independent reviewer reopened the files, recalculated durations and inspected
the history cache entries. This confirms tag-containing TTS and local output
processing, not a listening assessment of the acting/emphasis effect, a fresh
clone-path test with the new controls, or equivalence to Fish cloud processing.

The first attempt hit the 3 GiB available-RAM guard. After closing the completed
research tab, only this installation's working-set target was reduced from
3 to 2 GiB before the successful retry. The 3 GiB available-RAM threshold and
automatic 10 GiB private-memory cap were retained; the derived RSS guard became
stricter. These private settings are test conditions, not public defaults or a
recommendation for every PC. Concurrent applications still affect whether a
request fits memory.

The actual frontend displayed distinct labels for direction, delivery, the
three sampling inputs and four audio controls. Korean Guide notes were added
to all three example workflows, with inline tag examples rendered as code so
Markdown does not hide the angle brackets. Existing node IDs and input names
were preserved, and optional sampling widgets were appended after existing
widgets. See the [control guide](controls_KO.md) for short-script/chunk limits
and the cloud-only features that are not implemented.

## Model-based generation budget and failure messages (0.1.4)

The device-specific 24-second widget maximum was removed from both Generate and
Voice Clone. The checkpoint's
[official configuration](https://huggingface.co/fishaudio/drama-3/blob/main/config.json)
sets `max_position_embeddings=262144`; the pinned native generator checks the
same maximum. Its Fish DAC uses 44,100 samples/second and 2,048 samples/frame.
The input ceiling is therefore floor(262144 / (44100 / 2048)) = 12,173 seconds.
This is a theoretical context-budget bound per text chunk, not a verified speech
duration or a quality guarantee. Prompt, references and history share the space.

Seconds now use the exact codec ratio and round up to whole frames: 12 seconds
reserves 259 frames instead of the previous approximate 258, and 60 seconds
reserves 1,292. Default widget value remains 12 seconds. A managed request that
cannot fit even without a prompt is rejected before model startup; external
servers are not blocked using this installation's local context setting.
Native capacity failures are also explained without guessing prompt token counts.

All 37 unit tests and Ruff passed locally. An independent Gravitas reviewer
compared the implementation to the pinned native checks and independently ran
the five additional boundary/error tests. They cover duration/frame bounds,
managed versus external capacity, node schemas, timeout configuration, and
capacity/memory/busy error distinctions. A read timeout does not cancel server
inference; no automatic retry is added. Configuration can extend the default
600-second read wait or explicitly disable it with 0; connection timeouts remain
separate.

The installed ComfyUI was restarted with an empty queue after saving workflow
recovery copies. Its actual node definitions advertised 12,173 seconds for both
generation nodes. A 60-second queue submission passed schema validation, then
returned the expected clear context error in about 1.02 seconds: 1,292 requested
frames versus this server's unchanged 1,024-position context. It did not start
model inference for that rejected request.
In a freshly opened frontend tab, the actual Clone spinbutton exposed
`aria-valuemax=12173`, accepted 60, and was restored to 12 before saving.

A separate fresh default-budget TTS request completed in about 72.8 seconds of
observed request/poll wall time and saved finite, non-silent 44,100 Hz FLAC audio
of 12.02794 seconds (259 codec frames). This verifies audio production and rounded
duration budgeting, not listening quality or utterance completeness. The private
configuration was byte-identical before and after these checks: no context,
backend, memory limit or timeout setting was automatically expanded.

Long-form generation near the theoretical ceiling, other hardware, and its
perceptual quality remain unverified. Each deployment chooses its context and
resource settings; the shared workflow does not impose this PC's settings.

## Longer default context and actual long-form generation (0.1.5)

The managed default context and its preflight check now share a 4096-position
default. Explicit context values in existing configurations are preserved, as
are the memory defaults. The managed example and English/Korean guides explain
how to merge long-form settings without replacing other session options.
All 37 unit tests, Ruff and the whitespace check passed. An independent Gravitas
review also exercised explicit-context preservation and checked the final diff.

A local Windows CUDA ComfyUI request used a 441-character Korean acting script,
seed 123, default sampling, no reference, and a 47-second budget per text chunk.
It completed successfully in approximately 589 seconds of observed request/poll
time and saved 74.67537 seconds of mono 44,100 Hz FLAC audio. Reopening the file
confirmed finite, non-silent samples (RMS 0.1011, peak 0.8758). The native log
recorded three completed chunks of 745, 724 and 139 codec frames, with no
`max_tokens reached` warning; their sum matches the saved duration.

This run explicitly used context 4096, disk experts with 8 cache slots, 16 CPU
expert layers, codec on the CUDA backend, and no HTTP read timeout. Its local
Windows limits were working set 2 GiB, private commit 12 GiB and minimum available
RAM 3 GiB. These are observed test settings, not shared defaults or requirements.
Sampled minimum available RAM was 4.56 GiB and the process lifetime private peak
was about 10.03 GiB. The available-RAM guard did not stop this successful run.

Earlier attempts with context 4096 were stopped by the available-RAM guard or
failed to allocate the second chunk's tower prefill graph under a 10 GiB private
limit. A later sample showed free VRAM alongside a private peak close to that
limit. The successful run after adjusting the private limit demonstrates why
context, resident RAM, private commit and VRAM must be checked separately.

Local Qwen3-ASR recognized speech across the full output and its final sentence.
Some words differed in recognition; this is not a listening-quality assessment
or a guarantee of exact pronunciation, acting, longer scripts or other hardware.
The private script, audio, configuration and local paths are not published.

## Saved long-form workflow defaults (0.1.6)

The three distributed workflows now save a 47-second generation budget per text
chunk and include a Korean long-form note. The six existing local variants were
updated separately with recovery copies. Named widget values, when present,
match the positional values. A file comparison against those copies found only
the intended budget and note changes; scripts, references, links and layout
were preserved. The local private configuration was unchanged.

The updated auto-transcript Clone workflow was reopened through ComfyUI's
workflow browser. Both its node and properties panel displayed 47, and the new
note was present. An already-open workflow can retain its old values, so users
should reopen the saved file. This file/UI check does not claim a new long-form
Clone inference run; the 74.7-second test above used ordinary TTS with the same
47-second per-chunk budget. A newly added node still defaults to 12 seconds,
and its model-based input ceiling remains 12,173 seconds.

## Model download and hardware notes (0.1.7)

All three distributed workflows include two additional core MarkdownNote nodes:
Setup and Hardware. Their Korean guide links to the standalone GGUF packages,
lists file sizes checked against the publisher's metadata on 2026-10-18, and
separates optional automatic-transcription weights and nodes from ordinary TTS
and manual cloning. Hardware tiers are explicitly untested starting suggestions,
not measured minimum requirements. The guide distinguishes file size, resident
RAM, private commit and VRAM, and explains CPU offload, streaming codec processing,
context, restart and timeout settings without changing installation configuration.

The six local workflow variants were also updated with recovery copies. Comparing
the nine actual saved files against those copies, after removing the two new
notes and restoring last_node_id, recovered exactly the original JSON. Existing
scripts, references, nodes, links, layout and generation budgets were preserved.
The private config hash was unchanged. All 37 unit tests, Ruff, whitespace and
public-data/portable-settings checks passed. An independent Gravitas review
checked the sources, final notes and preservation comparison.

A fresh ComfyUI preview loaded a byte-identical copy of the saved automatic
Clone Controls graph. Both new notes rendered as tables and clickable links.
No new node package or server restart is needed for these core notes. This
documentation-only change did not run new inference or validate additional
hardware tiers; the earlier long-form test used streaming on one Windows CUDA
configuration.

## Visible left-hand start guide (0.1.8)

The initial view now includes an additional About note on the left of the graph.
It shows model links, a Model Storage Location folder tree, engine/configuration
setup and usage steps. The text distinguishes basic workflows with direct text
inputs from variants with Script & Direction, and optional ASR from ordinary TTS.
The existing Setup, Hardware and acting notes remain available.

The three public and six local files were compared with recovery copies. Apart
from the new unconnected core note, last_node_id and initial viewport, their
JSON is unchanged, including every existing node position, input and link.
Private configuration was preserved. An independent Gravitas check found and
resolved the basic-versus-Controls instruction difference before publication.
A fresh ComfyUI preview of the final TTS graph displayed the left note and folder
tree immediately, without panning or locating a node. The adjusted margin keeps
the note clear of the left toolbar. This presentation change ran no inference.
