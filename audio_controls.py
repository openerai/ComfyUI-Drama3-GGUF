"""Local FFmpeg output processing; these settings are not Drama3 model options."""
import io
import math
from numbers import Integral
import shutil
import subprocess

import numpy as np
import soundfile

from .configuration import resolve_path


def adjust_audio(audio, sample_rate, speed=1.0, volume_db=0.0, normalize_loudness=False, target_lufs=-16.0, *, config=None):
    values = ((speed, 0.5, 2.0, "speed"), (volume_db, -20, 20, "volume_db"),
              (target_lufs, -30, -10, "target_lufs"))
    for value, minimum, maximum, name in values:
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be finite and between {minimum} and {maximum}.")
    if not isinstance(sample_rate, Integral) or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer.")
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim != 2 or not all(audio.shape) or not np.isfinite(audio).all():
        raise ValueError("Use nonempty, finite audio shaped [samples, channels].")
    if speed == 1 and volume_db == 0 and not normalize_loudness:
        return audio, sample_rate
    config = config or {}
    executable = (str(resolve_path(config, config["ffmpeg_path"])) if config.get("ffmpeg_path")
                  else shutil.which("ffmpeg"))
    if not executable:
        raise RuntimeError("Audio Controls needs FFmpeg on PATH, or ffmpeg_path in this installation's config.json.")
    filters = []
    if speed != 1:
        filters.append(f"atempo={speed:.8g}")
    if normalize_loudness:
        filters.append(f"loudnorm=I={target_lufs:.8g}:TP=-1.5:LRA=11")
    if volume_db != 0:
        filters.append(f"volume={volume_db:.8g}dB")
    filters.append("alimiter=limit=0.98:level=0:latency=1")
    buffer = io.BytesIO()
    soundfile.write(buffer, audio, int(sample_rate), format="WAV", subtype="FLOAT")
    try:
        result = subprocess.run(
            [executable, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", "pipe:0", "-af", ",".join(filters),
             "-ar", str(sample_rate), "-c:a", "pcm_f32le", "-f", "wav", "pipe:1"],
            input=buffer.getvalue(), capture_output=True, timeout=120,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"Audio Controls could not run FFmpeg: {error}") from error
    if result.returncode:
        raise RuntimeError("FFmpeg audio processing failed: " + result.stderr.decode("utf-8", errors="replace")[-1200:])
    output, rate = soundfile.read(io.BytesIO(result.stdout), dtype="float32", always_2d=True)
    if rate != sample_rate or output.shape[1] != audio.shape[1] or not output.size or not np.isfinite(output).all():
        raise RuntimeError("FFmpeg returned invalid audio or changed the sample rate/channel count.")
    return output, rate
