"""Copy all supplied workflows into a versioned folder, preserving existing user files."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
WORKFLOWS = ("Drama3_GGUF_TTS.json", "Drama3_GGUF_Voice_Clone.json",
             "Drama3_GGUF_Voice_Clone_Auto_Transcript.json")


def comfy_root(value=None):
    path = Path(value).expanduser().resolve() if value else ROOT.parent.parent
    if not (path / "main.py").is_file() or not (path / "custom_nodes").is_dir():
        raise ValueError("Set --comfy-root to the ComfyUI directory containing main.py and custom_nodes.")
    return path


def install(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    for name in WORKFLOWS:
        target = destination / name
        if target.exists():
            results.append(("KEPT existing", target))
        else:
            shutil.copyfile(ROOT / "example_workflows" / name, target)
            results.append(("COPIED", target))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comfy-root", help="ComfyUI installation, not the Desktop application's executable folder")
    parser.add_argument("--workflow-dir", help="Custom user/workflow destination; default is user/default/workflows/Drama3-GGUF-0.2.0")
    args = parser.parse_args()
    destination = Path(args.workflow_dir).expanduser() if args.workflow_dir else (
        comfy_root(args.comfy_root) / "user/default/workflows/Drama3-GGUF-0.2.0")
    for action, path in install(destination):
        print(f"{action}: {path}")
    print("Refresh ComfyUI and OPEN a copied workflow. An already-open canvas keeps its old settings.")


if __name__ == "__main__":
    main()
