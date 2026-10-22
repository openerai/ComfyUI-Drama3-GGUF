# Acting, sampling and audio controls

## Script & Direction

Put new dialogue in New speech text and natural-language acting directions in Direction, without brackets. Script & Direction prepends `[direction]`. Basic workflows without this node accept those brackets directly in the generation text.

Delivery applies a paired tag to the whole short sentence. For individual words, leave Delivery=none and write tags manually: `Today is a <emphasis>new</emphasis> beginning.` or `<whisper>Please be quiet.</whisper>`. Place sound directions such as `[sighs]` at their intended position. These instructions do not guarantee acting or voice quality; compare short examples first. Keep reference transcripts limited to the words actually spoken in the recording.

### Emotion examples

The delivery presets are not an exhaustive emotion list. Use natural language for emotions; start with Delivery=none.

- Joy: `bright and happy, with a slight smile in the voice`
- Sadness: `quietly sad, holding back tears`
- Restrained anger: `low and firm, suppressing anger`
- Embarrassment: `hesitate briefly, then speak cautiously`
- A change of emotion: `anxious at first, relieved at the end`

Inline directions are also possible: `[surprised] Really? [relieved] What a relief.` They are acting instructions, not a guaranteed set of fixed emotion commands or a numeric intensity control.

The default native chunker uses 200 characters and does not carry a long paired tag's scope across chunks. When Delivery is selected, Script & Direction rejects inputs over 200 characters including tags/directions. Split long manually tagged passages into short sentences. [Official syntax](https://docs.fish.audio/features/text-to-speech/drama-3)

## Generation and sampling

Start with Temperature=1.0 / Top P=0.9 / Top K=4097. Change one setting at a time. Very low temperature can produce silence or repetition. This runtime rejects Top P=0 and Top K=0. Temperature=0 is not fully deterministic in every repetition-handling path. A fixed seed helps comparisons within the same configuration, but changing quantization or backend/offload can change output.

4097 includes end-of-speech and all semantic candidates, matching the official demo's all-candidates setting. Old saved values are preserved. Read the generation node's Raw output check before normalization; low signal and a budget notice are reasons to listen, not proof of missing speech. Do not treat a volume increase or a shorter budget as a general cure for failed generation. See the [controlled comparison](verification.md#sampling-and-output-diagnostics-0111).

Max seconds is a budget for each text chunk. New nodes default to 12; saved workflows start at **47 seconds per chunk**. This is adjustable and not the total output-duration limit. The model-based input ceiling is 12,173 seconds, derived from 262,144 context positions and the codec rate; it is not an output-duration or quality guarantee. Prompts, references and history also use context.

Managed context starts at `fish_drama3.context_length=4096`. Explicit older values in config.json are preserved until edited. Merge changes without removing paths, backend or memory settings. Stop the managed server with `python run_server.py --stop` so the next request applies them. More context needs more memory. `request_timeout_seconds=0` disables the HTTP read wait; default is 600 seconds. A timeout does not cancel server inference, so check status before retrying.

## Audio Controls (Local)

- Speed=1.0 preserves tempo; 1.2 is faster, 0.8 slower. FFmpeg atempo preserves pitch.
- Volume dB: 0 preserves gain; -6 reduces it, +3 increases it.
- Normalize loudness uses local EBU R128 processing. Target LUFS defaults to -16 here, not a promise of Fish web-app parity or an exact result on every short clip.
- Processing order: tempo → normalization → gain → 0.98 peak limiter. Additional gain changes final loudness after normalization.

Non-neutral processing requires FFmpeg on PATH or ffmpeg_path in config.json. Neutral 1x / 0dB / normalization-off passes samples through unchanged. Sample rate/channels are preserved; one audio batch is supported. Changing only audio controls can reuse generated audio from the same graph. Running an ASR branch separately can clear ComfyUI's generation cache.

## Fish web-app differences

These are local post-processing controls, not native speed controls or a clone of Fish cloud. Cloud number/date normalization, automatic tagging and S2.1 tag-compatibility mode are not implemented. Spell difficult numbers or units the way they should be pronounced. The examined web app exposed volume/speed for Drama3 and additional normalization/tag options for S2.1 Pro; these are distinct models and services.
