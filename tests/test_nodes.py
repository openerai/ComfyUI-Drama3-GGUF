"""Fast input-boundary checks; real ComfyUI/Torch inference is checked separately."""
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
package = types.ModuleType("drama3_nodes_under_test")
package.__path__ = [str(ROOT)]
sys.modules[package.__name__] = package
comfy = types.ModuleType("comfy")
management = types.ModuleType("comfy.model_management")
management.unload_all_models = Mock()
management.soft_empty_cache = Mock()
comfy.model_management = management
with patch.dict(sys.modules, {"comfy": comfy, "comfy.model_management": management, "torch": types.ModuleType("torch")}):
    nodes = importlib.import_module(package.__name__ + ".nodes")


class CloneInputTests(unittest.TestCase):
    def setUp(self):
        self.config = patch.object(nodes, "load_config", return_value={"mode": "external", "server_url": "http://127.0.0.1:8035"})
        self.config.start()
        self.addCleanup(self.config.stop)

    def test_clone_requires_reference_without_changing_tts_schema(self):
        clone = nodes.Drama3GGUFClone.INPUT_TYPES()
        self.assertIn("reference_audio", clone["required"])
        self.assertIn("reference_text", clone["required"])
        self.assertIn("reference_audio", nodes.Drama3GGUFGenerate.INPUT_TYPES()["optional"])

    def test_clone_missing_audio_or_transcript_never_submits_tts(self):
        with patch.object(nodes.client, "generate") as generate:
            for audio, transcript in ((None, "Reference words."), (object(), "")):
                with self.assertRaises(ValueError):
                    nodes.Drama3GGUFClone().clone(audio, transcript, "New words.", 123, 12)
            generate.assert_not_called()

    def test_old_tts_transcript_without_audio_does_not_silently_generate(self):
        with patch.object(nodes.client, "generate") as generate:
            with self.assertRaisesRegex(ValueError, "Connect reference_audio"):
                nodes.Drama3GGUFGenerate().generate("New words.", 123, 12, reference_text="Reference words.")
            generate.assert_not_called()

    def test_multiple_references_are_not_silently_truncated_to_first_batch(self):
        audio = {"waveform": np.zeros((2, 1, 100)), "sample_rate": 16000}
        with patch.object(nodes.client, "generate") as generate:
            with self.assertRaisesRegex(ValueError, "one reference"):
                nodes.Drama3GGUFClone().clone(audio, "Reference words.", "New words.", 123, 12)
            generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
