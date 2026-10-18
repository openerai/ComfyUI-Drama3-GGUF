from .nodes import Drama3GGUFClone, Drama3GGUFGenerate

NODE_CLASS_MAPPINGS = {"Drama3GGUFGenerate": Drama3GGUFGenerate, "Drama3GGUFClone": Drama3GGUFClone}
NODE_DISPLAY_NAME_MAPPINGS = {"Drama3GGUFGenerate": "Drama 3 GGUF · Generate Audio",
                              "Drama3GGUFClone": "Drama 3 GGUF · Voice Clone"}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
