"""Fast input-boundary checks; real ComfyUI/Torch inference is checked separately."""
import importlib
import json
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

    def test_both_node_duration_ranges_follow_model_instead_of_a_device_cap(self):
        for cls in (nodes.Drama3GGUFGenerate, nodes.Drama3GGUFClone):
            option = cls.INPUT_TYPES()["required"]["max_seconds"][1]
            self.assertEqual(option["default"], 12)
            self.assertEqual(option["max"], nodes.client.MAX_GENERATION_SECONDS)
        with patch.object(nodes.client, "generate") as generate:
            with self.assertRaises(ValueError):
                nodes.Drama3GGUFGenerate().generate("Words.", 123, float("nan"))
            with patch.object(nodes, "load_config", return_value={"mode": "managed", "server_url": "http://127.0.0.1:8035"}):
                with self.assertRaisesRegex(RuntimeError, "문맥 용량 초과"):
                    nodes.Drama3GGUFGenerate().generate("Words.", 123, 60)
            generate.assert_not_called()

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

    def test_reference_transcript_uses_asr_or_explicit_full_correction(self):
        node = nodes.Drama3GGUFReferenceText()
        self.assertEqual(node.prepare(" recognized words ")["result"], ("recognized words",))
        corrected = node.prepare("wrong words", " exact reference words ")
        self.assertEqual(corrected["result"], ("exact reference words",))
        self.assertEqual(corrected["ui"]["text"], ["exact reference words"])

    def test_script_preserves_inline_tags_and_places_direction_before_new_speech(self):
        node = nodes.Drama3GGUFScript()
        text = "오늘은 <emphasis>중요한</emphasis> 날입니다."
        self.assertEqual(node.prepare(text, "차분하게", "none"), ("[차분하게] " + text,))
        self.assertEqual(node.prepare("조용히 말해요.", "", "whisper"), ("<whisper>조용히 말해요.</whisper>",))
        self.assertEqual(node.prepare(text), (text,))
        with self.assertRaises(ValueError):
            node.prepare("말해요.", "[차분하게]")
        with self.assertRaises(ValueError):
            node.prepare("아" * 180, "조용히" * 15, "whisper")

    def test_empty_recognition_cannot_reach_clone_without_a_correction(self):
        node = nodes.Drama3GGUFReferenceText()
        with self.assertRaisesRegex(ValueError, "No reference speech"):
            node.prepare(" \n", " ")
        self.assertEqual(node.prepare("", "spoken words")["result"], ("spoken words",))

    def test_auto_workflow_transcribes_the_same_selected_audio_used_by_clone(self):
        workflow = json.loads((ROOT / "example_workflows/Drama3_GGUF_Voice_Clone_Auto_Transcript.json").read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in workflow["nodes"]}
        links = {link[0]: link for link in workflow["links"]}
        clone = next(node for node in by_id.values() if node["type"] == "Drama3GGUFClone")
        asr = next(node for node in by_id.values() if node["type"] == "Qwen3ASRTranscribe")
        clone_audio = links[clone["inputs"][0]["link"]][1:3]
        asr_audio = links[asr["inputs"][1]["link"]][1:3]
        self.assertEqual(clone_audio, asr_audio)
        self.assertEqual(by_id[clone_audio[0]]["type"], "PreviewAudio")
        self.assertEqual(links[clone["inputs"][1]["link"]][-1], "STRING")


if __name__ == "__main__":
    unittest.main()
