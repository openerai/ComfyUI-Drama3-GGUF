import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import numpy as np
import requests
import soundfile

ROOT = Path(__file__).resolve().parents[1]
package = types.ModuleType("drama3_under_test")
package.__path__ = [str(ROOT)]
sys.modules[package.__name__] = package
configuration = importlib.import_module(package.__name__ + ".configuration")
client = importlib.import_module(package.__name__ + ".client")
sys.path.insert(0, str(ROOT))
runtime = importlib.import_module("run_server")


class FakeAudioServer(BaseHTTPRequestHandler):
    received = None

    def log_message(self, *args):
        pass

    def do_GET(self):
        assert self.path == "/v1/models"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"data": [{"id": "custom-quant", "family": "fish_drama3"}]}).encode())

    def do_POST(self):
        assert self.path == "/v1/audio/speech"
        type(self).received = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        buffer = io.BytesIO()
        soundfile.write(buffer, np.sin(np.arange(1600) * 0.1) * 0.2, 16000, format="WAV")
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.end_headers()
        self.wfile.write(buffer.getvalue())


class PortableClientTests(unittest.TestCase):
    def test_config_paths_survive_a_different_installation_directory(self):
        with tempfile.TemporaryDirectory(prefix="drama3 moved ") as temporary:
            root = Path(temporary)
            (root / "weights.gguf").write_bytes(b"GGUF")
            (root / "server.exe").write_bytes(b"test fixture, never executed")
            path = root / "config.json"
            path.write_text(json.dumps({"mode": "managed", "executable": "server.exe", "model_path": "weights.gguf"}))
            config = configuration.load_config(path)
            native = configuration.managed_server_config(config)
            self.assertEqual(native["models"][0]["path"], str(root / "weights.gguf"))
            self.assertEqual(native["model_spec_override"], str(ROOT / "specs/fish_drama3.json"))

    def test_ram_policy_scales_and_explicit_settings_win(self):
        self.assertEqual(configuration.memory_limits({}, 16 * 1024**3)["working_set_gib"], 2)
        self.assertEqual(configuration.memory_limits({}, 32 * 1024**3)["working_set_gib"], 4)
        self.assertEqual(configuration.memory_limits({}, 64 * 1024**3)["working_set_gib"], 8)
        self.assertEqual(configuration.memory_limits({"memory": {"working_set_gib": 3}}, 64 * 1024**3)["working_set_gib"], 3)
        with self.assertRaises(ValueError):
            configuration.memory_limits({"memory": {"working_set_gib": float("nan")}})

    def test_explicit_missing_config_does_not_fall_back_to_another_server(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(FileNotFoundError):
                configuration.load_config(Path(temporary) / "not-found.json")

    def test_managed_mode_rejects_remote_launch_target(self):
        with self.assertRaises(ValueError):
            configuration.managed_server_config({"server_url": "http://192.0.2.10:8035"})

    def test_ambiguous_models_need_an_explicit_choice(self):
        models = {"data": [{"id": "q2", "family": "fish_drama3"}, {"id": "q4", "family": "fish_drama3"}]}
        with self.assertRaises(RuntimeError):
            client.select_model(models)
        self.assertEqual(client.select_model(models, "q4"), "q4")
        with self.assertRaises(RuntimeError):
            client.select_model(models, "missing")

    def test_external_mode_does_not_launch_a_process_when_disconnected(self):
        config = {"mode": "external", "server_url": "http://127.0.0.1:8035"}
        with patch.object(client, "get_models", side_effect=requests.ConnectionError), patch.object(client.subprocess, "Popen") as spawn:
            with self.assertRaises(RuntimeError):
                client.ensure_server(config, config["server_url"])
            spawn.assert_not_called()

    def test_unrelated_model_is_never_auto_selected(self):
        unknown = {"data": [{"id": "unrelated-text-model"}]}
        with self.assertRaises(RuntimeError):
            client.select_model(unknown)
        unrelated = {"data": [{"id": "other-tts", "family": "kokoro_tts"}]}
        with self.assertRaises(RuntimeError):
            client.select_model(unrelated, "other-tts")

    def test_managed_mode_does_not_adopt_an_unowned_server(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "server.exe").write_bytes(b"not executed")
            (root / "weights.gguf").write_bytes(b"GGUF")
            config = {"mode": "managed", "server_url": "http://127.0.0.1:8035", "_path": str(root / "config.json"),
                      "executable": "server.exe", "model_path": "weights.gguf"}
            models = {"data": [{"id": "other-quant", "family": "fish_drama3"}]}
            with patch.object(client, "get_models", return_value=models), patch.object(client.subprocess, "Popen") as spawn:
                with self.assertRaises(RuntimeError):
                    client.ensure_server(config, config["server_url"])
                spawn.assert_not_called()

    def test_managed_identity_rejects_changed_weight_path_and_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "weights.gguf").write_bytes(b"GGUF")
            config = {"mode": "managed", "server_url": "http://127.0.0.1:8035", "_path": str(root / "config.json"),
                      "executable": sys.executable, "model_path": "weights.gguf"}
            directory = configuration.state_directory(config)
            directory.mkdir()
            (directory / "server.json").write_text(json.dumps(configuration.managed_server_config(config)))
            (directory / "server_status.json").write_text(json.dumps({"pid": 123, "create_time": 100.0,
                                                                      "limits": configuration.memory_limits(config)}))
            process = unittest.mock.Mock()
            process.create_time.return_value = 100.0
            process.exe.return_value = sys.executable
            process.cmdline.return_value = [sys.executable, "--config", str(directory / "server.json")]
            document = {"data": [{"id": "drama3", "family": "fish_drama3", "path": str(root / "weights.gguf")}]}
            with patch.object(client.psutil, "Process", return_value=process):
                client.verify_managed_server(config, document)
                document["data"][0]["path"] = str(root / "wrong-quant.gguf")
                with self.assertRaises(RuntimeError):
                    client.verify_managed_server(config, document)
                document["data"][0]["path"] = str(root / "weights.gguf")
                config["threads"] = 32
                with self.assertRaises(RuntimeError):
                    client.verify_managed_server(config, document)

    def test_http_audio_roundtrip_and_inline_reference(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAudioServer)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            reference = client.reference_payload(np.zeros((1000, 1), dtype=np.float32), 16000, "Reference words.")
            audio, rate = client.generate({"mode": "external", "server_url": url}, "안녕하세요.", 7, 65, reference=reference)
            self.assertEqual((len(audio), rate), (1600, 16000))
            self.assertEqual(FakeAudioServer.received["model"], "custom-quant")
            self.assertEqual(FakeAudioServer.received["input"], "안녕하세요.")
            self.assertEqual(FakeAudioServer.received["voice_ref"]["type"], "base64")
            self.assertNotIn("path", FakeAudioServer.received["voice_ref"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_reference_requires_transcript_and_stays_under_server_limit(self):
        with self.assertRaises(ValueError):
            client.reference_payload(np.zeros(10), 16000, "")
        with self.assertRaises(ValueError):
            client.reference_payload(np.zeros(3_000_000, dtype=np.float32), 16000, "Too long.")

    def test_launcher_lock_prevents_two_watchdogs(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "lock"
            code = "from pathlib import Path; from run_server import launcher_lock; import sys\nwith launcher_lock(Path(sys.argv[1])) as acquired: print(acquired)"
            with runtime.launcher_lock(path) as acquired:
                self.assertTrue(acquired)
                result = subprocess.run([sys.executable, "-c", code, str(path)], cwd=ROOT, capture_output=True, text=True, timeout=15,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "False")
            with runtime.launcher_lock(path) as acquired:
                self.assertTrue(acquired)

    def test_stop_rejects_a_reused_pid(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            process = unittest.mock.Mock()
            process.create_time.return_value = 200.0
            process.exe.return_value = sys.executable
            process.cmdline.return_value = [sys.executable, "--config", str(directory / "server.json")]
            (directory / "server_status.json").write_text(json.dumps({"pid": 123, "create_time": 100.0, "executable": sys.executable}))
            with patch.object(runtime.psutil, "Process", return_value=process):
                with self.assertRaises(RuntimeError):
                    runtime.stop_server(directory)
            process.terminate.assert_not_called()

    @unittest.skipUnless(os.name == "nt", "Windows Job Object")
    def test_windows_job_terminates_its_child_on_close(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        job = None
        try:
            job = runtime.WindowsMemoryJob(child, {"private_limit_gib": 1, "working_set_gib": 0.25})
            job.close()
            self.assertIsNotNone(child.wait(timeout=5))
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
            if job:
                job.close()


if __name__ == "__main__":
    unittest.main()
