# Third-party components

The Python bridge and launcher are MIT licensed. Model weights, CUDA libraries,
and audio.cpp executables are not included in this repository.

`specs/fish_drama3.json` is copied unmodified from
[audio.cpp](https://github.com/0xShug0/audio.cpp), commit
`ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f`.
Copyright 2026 ShugoAI LLC. It is licensed under Apache-2.0;
the full license is in `licenses/audio.cpp-LICENSE`.

Drama3 GGUF weights are provided separately by
[Jmica/Drama-3-GGUF](https://huggingface.co/Jmica/Drama-3-GGUF).
Consult that repository's LICENSE and NOTICE for the model's terms.
The bridge's MIT license does not apply to the weights or third-party runtimes.
