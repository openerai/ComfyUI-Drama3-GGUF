import importlib
from pathlib import Path
import shutil
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np

package = types.ModuleType("drama3_audio_under_test")
package.__path__ = [str(Path(__file__).resolve().parents[1])]
sys.modules[package.__name__] = package
controls = importlib.import_module(package.__name__ + ".audio_controls")


class AudioControlTests(unittest.TestCase):
    def test_neutral_settings_do_not_need_ffmpeg_or_change_samples(self):
        audio = np.full((100, 2), 0.1, dtype=np.float32)
        with patch.object(controls.subprocess, "run") as run:
            output, rate = controls.adjust_audio(audio, 22050)
        run.assert_not_called()
        np.testing.assert_array_equal(output, audio)
        self.assertEqual(rate, 22050)

    def test_invalid_controls_or_audio_fail_before_spawning(self):
        audio = np.full((100, 1), 0.1, dtype=np.float32)
        with patch.object(controls.subprocess, "run") as run:
            for options in ({"speed": float("nan")}, {"speed": 0}, {"volume_db": 21}, {"target_lufs": -50}):
                with self.subTest(options=options), self.assertRaises(ValueError):
                    controls.adjust_audio(audio, 16000, **options)
            for invalid in (np.empty((0, 1)), np.full((10, 1), np.inf), np.zeros((1, 2, 3))):
                with self.assertRaises(ValueError):
                    controls.adjust_audio(invalid, 16000)
        run.assert_not_called()

    def test_non_neutral_settings_report_missing_ffmpeg(self):
        with patch.object(controls.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "FFmpeg"):
                controls.adjust_audio(np.ones((100, 1), dtype=np.float32) * 0.1, 16000, speed=1.1)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not installed on this test host")
    def test_real_tempo_and_gain_preserve_pitch_rate_and_stereo(self):
        rate = 22050
        time = np.arange(rate * 2) / rate
        audio = np.column_stack([np.sin(2 * np.pi * 440 * time) * 0.1, np.sin(2 * np.pi * 660 * time) * 0.06]).astype(np.float32)
        output, returned_rate = controls.adjust_audio(audio, rate, speed=1.25, volume_db=-6)
        self.assertEqual(returned_rate, rate)
        self.assertEqual(output.shape[1], 2)
        self.assertAlmostEqual(len(output) / rate, 1.6, delta=0.06)
        frequencies = np.fft.rfftfreq(len(output), 1 / rate)
        peak = frequencies[np.abs(np.fft.rfft(output[:, 0])).argmax()]
        self.assertAlmostEqual(peak, 440, delta=3)
        self.assertAlmostEqual(np.sqrt(np.mean(output[:, 0] ** 2)) / np.sqrt(np.mean(audio[:, 0] ** 2)), 10 ** (-6 / 20), delta=0.03)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not installed on this test host")
    def test_real_loudness_processing_restores_rate_and_limits_peaks(self):
        rate = 24000
        time = np.arange(rate * 3) / rate
        audio = (np.sin(2 * np.pi * 330 * time) * 0.002).astype(np.float32)[:, None]
        output, returned_rate = controls.adjust_audio(audio, rate, normalize_loudness=True, target_lufs=-16, volume_db=20)
        self.assertEqual(returned_rate, rate)
        self.assertEqual(output.shape[1], 1)
        self.assertAlmostEqual(len(output) / rate, 3, delta=0.03)
        self.assertTrue(np.isfinite(output).all())
        self.assertLessEqual(float(np.max(np.abs(output))), 0.981)
        self.assertGreater(float(np.sqrt(np.mean(output ** 2))), 0.05)


if __name__ == "__main__":
    unittest.main()
