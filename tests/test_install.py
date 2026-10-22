import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check_install
import install_workflows
sys.path.pop(0)


class InstallTests(unittest.TestCase):
    def test_wrong_python_without_site_packages_reports_missing_dependencies_without_traceback(self):
        result = subprocess.run([sys.executable, "-S", str(ROOT / "check_install.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing psutil", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_copy_includes_auto_transcript_and_preserves_user_changes_on_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "workflows"
            install_workflows.install(destination)
            self.assertEqual({path.name for path in destination.iterdir()}, set(install_workflows.WORKFLOWS))
            edited = destination / install_workflows.WORKFLOWS[0]
            edited.write_text("my saved work")
            install_workflows.install(destination)
            self.assertEqual(edited.read_text(), "my saved work")

    def test_workflow_check_distinguishes_old_schema_and_new_default_without_modifying_it(self):
        workflow = {"nodes": [
            {"id": 1, "type": "Drama3GGUFGenerate", "widgets_values": [""] * 9 + [30]},
            {"id": 13, "type": "Qwen3ASRLoader"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "old.json"
            path.write_text(json.dumps(workflow))
            before = path.read_bytes()
            issues = check_install.check_workflow(path)
            self.assertEqual(len(issues), 2)
            self.assertIn("Top K=30", issues[0])
            self.assertIn("old ASR ID", issues[1])
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual(check_install.check_workflow(ROOT / "example_workflows/Drama3_GGUF_TTS.json"), [])

    def test_converted_asr_metadata_is_distinct_from_raw_hf_safetensors(self):
        with tempfile.TemporaryDirectory() as directory:
            for converted in (False, True):
                path = Path(directory) / f"{converted}.safetensors"
                metadata = {"qwen3_asr_config": "{}"} if converted else {"format": "pt"}
                header = json.dumps({"__metadata__": metadata}).encode()
                path.write_bytes(struct.pack("<Q", len(header)) + header)
                self.assertEqual(check_install.converted_asr_file(path), converted)


if __name__ == "__main__":
    unittest.main()
