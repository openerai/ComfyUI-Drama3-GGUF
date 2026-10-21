import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
package = types.ModuleType("drama3_asr_under_test")
package.__path__ = [str(ROOT)]
sys.modules[package.__name__] = package
backend = importlib.import_module(package.__name__ + ".asr_backend")
folders = types.ModuleType("folder_paths")
folders.models_dir = "/comfy/models"
folders.folder_names_and_paths = {"asr": (["/shared/models/asr"], set())}
folders.supported_pt_extensions = {".safetensors"}
folders.add_model_folder_path = Mock()
folders.get_filename_list = Mock(return_value=["qwen3_asr_0.6b_bf16.safetensors"])
folders.get_folder_paths = Mock(return_value=["/comfy/custom_nodes"])
folders.get_full_path_or_raise = Mock(return_value="/shared/models/asr/qwen3_asr_0.6b_bf16.safetensors")
with patch.dict(sys.modules, {"folder_paths": folders}):
    nodes = importlib.import_module(package.__name__ + ".asr_nodes")


class ASRIntegrationBoundaryTests(unittest.TestCase):
    def test_optional_source_is_not_needed_for_schema_and_extra_model_paths_are_preserved(self):
        with patch.object(nodes, "load_backend") as load:
            schema = nodes.Drama3GGUFASRLoader.INPUT_TYPES()
        load.assert_not_called()
        self.assertIn("qwen3_asr_0.6b_bf16.safetensors", schema["required"]["model_name"][0])
        self.assertIn("/shared/models/asr", folders.folder_names_and_paths["asr"][0])
        self.assertEqual(nodes.Drama3GGUFASRLoader.RETURN_TYPES, ("DRAMA3_GGUF_ASR_MODEL",))
        self.assertEqual(nodes.Drama3GGUFASRTranscribe.INPUT_TYPES()["required"]["model"][0],
                         "DRAMA3_GGUF_ASR_MODEL")
        self.assertNotIn("return_timestamps", nodes.Drama3GGUFASRTranscribe.INPUT_TYPES()["required"])

    def test_missing_source_has_actionable_error_without_importing_another_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, "Plain TTS and manual cloning"):
                backend.find_backend([directory])

    def test_native_source_loads_with_relative_imports_without_executing_node_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            for index in (1, 2):
                repo = Path(directory) / str(index) / "ComfyUI-Drama3"
                native = repo / "qwen3_asr"
                native.mkdir(parents=True)
                (repo / "__init__.py").write_text("raise RuntimeError('Must not register extension')")
                (native / "__init__.py").write_text("")
                (native / "model.py").write_text(f"MARKER = {index}\n")
                (native / "asr.py").write_text("from .model import MARKER\n")
                found = backend.find_backend([repo.parent])
                self.assertEqual(backend.load_backend(found).MARKER, index)

    def test_loader_resolves_converted_file_through_comfy_paths(self):
        implementation = Mock()
        with patch.object(nodes, "load_config", return_value={}), \
                patch.object(nodes, "find_backend", return_value=Path("/native/qwen3_asr")), \
                patch.object(nodes, "load_backend", return_value=implementation):
            result = nodes.Drama3GGUFASRLoader().load("qwen3_asr_0.6b_bf16.safetensors")[0]
        implementation.load_qwen3_asr.assert_called_once_with(
            "/shared/models/asr/qwen3_asr_0.6b_bf16.safetensors")
        self.assertIs(result["model"], implementation.load_qwen3_asr.return_value)

    def test_transcription_forwards_the_same_segment_and_never_requests_timestamps(self):
        transcribe = Mock(return_value=("Reference words.", "English"))
        waveform = np.ones((1, 2, 1600), dtype=np.float32)
        model = {"model": object(), "transcribe": transcribe}
        result = nodes.Drama3GGUFASRTranscribe().transcribe(
            model, {"waveform": waveform, "sample_rate": 16000}, "auto", "Names", 128)
        self.assertEqual(result, ("Reference words.", "English"))
        args = transcribe.call_args.args
        self.assertIs(args[0], model["model"])
        np.testing.assert_array_equal(args[1], waveform[0])
        self.assertEqual(args[2:], (16000, None, "Names", 128))
        self.assertEqual(transcribe.call_args.kwargs, {})
        transcribe.return_value = (" ", "English")
        with self.assertRaisesRegex(ValueError, "No reference speech"):
            nodes.Drama3GGUFASRTranscribe().transcribe(model, {"waveform": waveform, "sample_rate": 16000})

    def test_distributed_auto_graph_uses_unique_ids_and_the_same_audio_for_clone(self):
        path = ROOT / "example_workflows/Drama3_GGUF_Voice_Clone_Auto_Transcript.json"
        graph = json.loads(path.read_text(encoding="utf-8"))
        by_id = {node["id"]: node for node in graph["nodes"]}
        self.assertEqual(by_id[13]["type"], "Drama3GGUFASRLoader")
        self.assertEqual(by_id[14]["type"], "Drama3GGUFASRTranscribe")
        self.assertEqual(next(link for link in graph["links"] if link[0] == 5)[-1], "DRAMA3_GGUF_ASR_MODEL")


if __name__ == "__main__":
    unittest.main()
