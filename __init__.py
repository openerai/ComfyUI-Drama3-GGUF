from .nodes import (Drama3GGUFAudioControls, Drama3GGUFClone, Drama3GGUFGenerate,
                    Drama3GGUFReferenceText, Drama3GGUFScript)

NODE_CLASS_MAPPINGS = {"Drama3GGUFGenerate": Drama3GGUFGenerate, "Drama3GGUFClone": Drama3GGUFClone,
                       "Drama3GGUFReferenceText": Drama3GGUFReferenceText,
                       "Drama3GGUFScript": Drama3GGUFScript, "Drama3GGUFAudioControls": Drama3GGUFAudioControls}
NODE_DISPLAY_NAME_MAPPINGS = {"Drama3GGUFGenerate": "Drama 3 GGUF · Generate Audio",
                              "Drama3GGUFClone": "Drama 3 GGUF · Voice Clone",
                              "Drama3GGUFReferenceText": "Drama 3 GGUF · Reference Transcript",
                              "Drama3GGUFScript": "Drama 3 GGUF · Script & Direction",
                              "Drama3GGUFAudioControls": "Drama 3 GGUF · Audio Controls (Local)"}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
