from .nodes import Drama3GGUFClone, Drama3GGUFGenerate, Drama3GGUFReferenceText

NODE_CLASS_MAPPINGS = {"Drama3GGUFGenerate": Drama3GGUFGenerate, "Drama3GGUFClone": Drama3GGUFClone,
                       "Drama3GGUFReferenceText": Drama3GGUFReferenceText}
NODE_DISPLAY_NAME_MAPPINGS = {"Drama3GGUFGenerate": "Drama 3 GGUF · Generate Audio",
                              "Drama3GGUFClone": "Drama 3 GGUF · Voice Clone",
                              "Drama3GGUFReferenceText": "Drama 3 GGUF · Reference Transcript"}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
