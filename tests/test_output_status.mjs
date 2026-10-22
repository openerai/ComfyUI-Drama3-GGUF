import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

function extension() {
    let registered;
    const source = readFileSync(new URL("../web/drama3.js", import.meta.url), "utf8")
        .replace(/^import .*;\r?$/gm, "");
    vm.runInNewContext(source, {
        app: { registerExtension(value) { registered = value; } },
        ComfyWidgets: { STRING(node, name) {
            const widget = { name, value: "", options: {}, element: {} };
            node.widgets.push(widget);
            return { widget };
        } },
    });
    return registered;
}

test("generation and clone show execution diagnostics without adding serialized inputs", () => {
    const ext = extension();
    for (const comfyClass of ["Drama3GGUFGenerate", "Drama3GGUFClone"]) {
        let previousCalled = false;
        const node = { comfyClass, widgets: [{ name: "text", value: "Keep my words" }],
            setDirtyCanvas() {}, onExecuted() { previousCalled = true; } };
        ext.nodeCreated(node);
        const status = node.widgets.find(widget => widget.name === "generation_status");
        assert.equal(status.serialize, false);
        assert.equal(status.options.serialize, false);
        assert.equal(status.element.readOnly, true);
        node.onExecuted({ text: ["Low signal level; listen before using."] });
        assert.equal(status.value, "Low signal level; listen before using.");
        assert.equal(previousCalled, true);
        assert.equal(node.widgets[0].value, "Keep my words");
    }
});

test("reference transcript preview still works and unrelated nodes are untouched", () => {
    const ext = extension();
    const node = { comfyClass: "Drama3GGUFReferenceText", widgets: [], setDirtyCanvas() {} };
    ext.nodeCreated(node);
    node.onExecuted({ text: ["The actual transcript"] });
    assert.equal(node.widgets[0].name, "used_reference_text");
    assert.equal(node.widgets[0].value, "The actual transcript");
    const ordinary = { comfyClass: "SaveAudioAdvanced", widgets: [] };
    ext.nodeCreated(ordinary);
    assert.equal(ordinary.widgets.length, 0);
});

test("opening an old graph warns about its saved sampling without changing dialogue or Top K", () => {
    const node = { comfyClass: "Drama3GGUFGenerate", widgets: [
        { name: "top_k", value: 30 }, { name: "text", value: "My original words" }],
        onConfigure() { return "previous callback"; }, setDirtyCanvas() {} };
    extension().nodeCreated(node);
    assert.equal(node.onConfigure({}), "previous callback");
    assert.match(node.widgets.find(w => w.name === "generation_status").value, /Saved Top K=30/);
    assert.equal(node.widgets[0].value, 30);
    assert.equal(node.widgets[1].value, "My original words");
});

test("distributed examples use all candidates without enabling optional FFmpeg processing", () => {
    for (const name of ["TTS", "Voice_Clone", "Voice_Clone_Auto_Transcript"]) {
        const workflow = JSON.parse(readFileSync(new URL(`../example_workflows/Drama3_GGUF_${name}.json`, import.meta.url)));
        const generation = workflow.nodes.find(node => ["Drama3GGUFGenerate", "Drama3GGUFClone"].includes(node.type));
        assert.equal(generation.widgets_values.at(-1), 4097);
        const controls = workflow.nodes.find(node => node.type === "Drama3GGUFAudioControls");
        assert.equal(controls.widgets_values[2], false);
    }
});
