import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { runInNewContext } from "node:vm";
import { detailGuideNodes, guideLanguages, restoreGuideLanguage, setGuideDetails,
    setGuideLanguage } from "../web/guide-language.js";

function note(role = "setup") {
    return {type: "MarkdownNote", title: "한국어 제목", widgets: [{name: "text", value: "한국어 설명"}],
        properties: {drama3Guide: {role, locale: "ko", translations: {
            ko: {title: "한국어 제목", text: "한국어 설명"}, en: {title: "English title", text: "English guide"},
            ja: {title: "日本語の見出し", text: "日本語の説明"}, zh: {title: "中文标题", text: "中文说明"}}}}};
}

test("switches all marked guides without changing speech or ordinary notes", () => {
    const first = note(), second = note("hardware");
    const speech = {type: "Drama3GGUFGenerate", widgets: [{name: "text", value: "Keep my dialogue"}]};
    const ordinary = {type: "MarkdownNote", widgets: [{name: "text", value: "My personal note"}]};
    const untouched = JSON.stringify([speech, ordinary]);
    const graph = {_nodes: [first, second, speech, ordinary]};
    setGuideLanguage(graph, "en");
    assert.equal(first.widgets[0].value, "English guide");
    assert.equal(second.title, "English title");
    assert.equal(JSON.stringify([speech, ordinary]), untouched);
    setGuideLanguage(graph, "ko");
    assert.equal(first.widgets[0].value, "한국어 설명");
});

test("preserves edited text across toggles and restores saved language", () => {
    const original = note();
    const graph = {_nodes: [original]};
    original.widgets[0].value = "Edited Korean guide";
    setGuideLanguage(graph, "en");
    const saved = JSON.parse(JSON.stringify(original));
    restoreGuideLanguage({_nodes: [saved]});
    assert.equal(saved.widgets[0].value, "English guide");
    setGuideLanguage({_nodes: [saved]}, "ko");
    assert.equal(saved.widgets[0].value, "Edited Korean guide");
});

test("preserves a visible edit saved without toggling first, including an empty body", () => {
    for (const text of ["My saved edit", ""]) {
        const edited = note();
        edited.widgets[0].value = text;
        const reloaded = JSON.parse(JSON.stringify(edited));
        const graph = {_nodes: [reloaded]};
        restoreGuideLanguage(graph);
        assert.equal(reloaded.widgets[0].value, text);
        setGuideLanguage(graph, "en");
        setGuideLanguage(graph, "ko");
        assert.equal(reloaded.widgets[0].value, text);
    }
});

test("language selection is local to each graph", () => {
    const first = {_nodes: [note()]}, second = {_nodes: [note()]};
    setGuideLanguage(first, "en");
    assert.equal(first._nodes[0].properties.drama3Guide.locale, "en");
    assert.equal(second._nodes[0].properties.drama3Guide.locale, "ko");
});

test("rejects unsupported locales without mutation", () => {
    const graph = {_nodes: [note()]};
    const before = JSON.stringify(graph);
    setGuideLanguage(graph, "fr");
    assert.equal(JSON.stringify(graph), before);
});

test("Japanese and Chinese survive saving, reopening and edits in either language", () => {
    let graph = {_nodes: [note()]};
    for (const [locale, body] of [["ja", "日本語の説明"], ["zh", "中文说明"]]) {
        setGuideLanguage(graph, locale);
        assert.equal(graph._nodes[0].widgets[0].value, body);
        graph._nodes[0].widgets[0].value = body + " edited";
        graph = JSON.parse(JSON.stringify(graph));
        restoreGuideLanguage(graph);
        assert.equal(graph._nodes[0].properties.drama3Guide.locale, locale);
        setGuideLanguage(graph, "en");
        setGuideLanguage(graph, locale);
        assert.equal(graph._nodes[0].widgets[0].value, body + " edited");
    }
});

test("older and mixed workflows offer only translations present in every marked note", () => {
    const old = note();
    delete old.properties.drama3Guide.translations.ja;
    delete old.properties.drama3Guide.translations.zh;
    const graph = {_nodes: [note(), old]};
    assert.deepEqual(guideLanguages(graph).map(([locale]) => locale), ["ko", "en"]);
    const before = JSON.stringify(graph);
    setGuideLanguage(graph, "ja");
    assert.equal(JSON.stringify(graph), before);
    setGuideLanguage(graph, "en");
    assert.equal(old.widgets[0].value, "English guide");
    assert.deepEqual(guideLanguages({_nodes: []}), []);
});

test("distributed workflow notes contain all four languages and localized guide links", () => {
    for (const name of ["TTS", "Voice_Clone", "Voice_Clone_Auto_Transcript"]) {
        const workflow = JSON.parse(readFileSync(new URL(`../example_workflows/Drama3_GGUF_${name}.json`, import.meta.url)));
        const notes = workflow.nodes.filter(node => node.properties?.drama3Guide);
        assert.equal(notes.length, 5);
        for (const node of notes) {
            const guide = node.properties.drama3Guide;
            assert.deepEqual(Object.keys(guide.translations).sort(), ["en", "ja", "ko", "zh"]);
            assert.equal(node.widgets_values[0], guide.translations[guide.locale].text);
            for (const translation of Object.values(guide.translations)) {
                assert.ok(translation.title.trim());
                assert.ok(translation.text.trim());
            }
        }
        const about = notes.find(node => node.properties.drama3Guide.role === "about").properties.drama3Guide;
        assert.ok(about.translations.ja.text.includes("docs/model_setup_JA.md"));
        assert.ok(about.translations.zh.text.includes("docs/model_setup_ZH.md"));
    }
});

function detailNote(collapsed = true) {
    const node = note();
    node.properties.drama3Guide.detail = true;
    node.flags = {collapsed};
    // Native LiteGraph collapse(force) toggles; force bypasses collapsible permission.
    node.collapse = function(force) {
        assert.equal(force, true);
        this.flags.collapsed = !this.flags.collapsed;
    };
    return node;
}

test("details toggle only marked help and accept mixed or repeated target states", () => {
    const first = detailNote(), second = detailNote(false);
    const ordinary = note("about"), speech = {type: "Drama3GGUFGenerate", flags: {}, widgets: ["My dialogue"]};
    const before = JSON.stringify([ordinary, speech]);
    const graph = {_nodes: [first, second, ordinary, speech]};
    assert.equal(detailGuideNodes(graph).length, 2);
    for (const expanded of [true, true, false, false, true]) {
        setGuideDetails(graph, expanded);
        assert.equal(first.flags.collapsed, !expanded);
        assert.equal(second.flags.collapsed, !expanded);
    }
    assert.equal(JSON.stringify([ordinary, speech]), before);
});

test("saved fold state survives language switching and restoring", () => {
    const graph = {_nodes: [detailNote(), detailNote(false)]};
    setGuideLanguage(graph, "ja");
    const saved = JSON.parse(JSON.stringify(graph));
    restoreGuideLanguage(saved);
    assert.deepEqual(saved._nodes.map(node => node.flags.collapsed), [true, false]);
    assert.ok(saved._nodes.every(node => node.properties.drama3Guide.locale === "ja"));
});

test("examples have one download panel, short steps and three folded details", () => {
    const catalog = JSON.parse(readFileSync(new URL("../model_catalog.json", import.meta.url)));
    for (const name of ["TTS", "Voice_Clone", "Voice_Clone_Auto_Transcript"]) {
        const workflow = JSON.parse(readFileSync(new URL(`../example_workflows/Drama3_GGUF_${name}.json`, import.meta.url)));
        const notes = workflow.nodes.filter(node => node.properties?.drama3Guide);
        const details = notes.filter(node => node.properties.drama3Guide.detail);
        assert.deepEqual(details.map(node => node.properties.drama3Guide.role).sort(), ["guide", "hardware", "setup"]);
        assert.ok(details.every(node => node.flags.collapsed === true));
        for (const node of notes) {
            const guide = node.properties.drama3Guide;
            if (!guide.detail) assert.equal(Boolean(node.flags.collapsed), false);
            for (const translation of Object.values(guide.translations)) {
                if (guide.role === "workflow") assert.ok(translation.text.length < 900);
                const links = [...translation.text.matchAll(/https:\/\/huggingface\.co\/[^\s)]+\.(?:gguf|safetensors)/g)];
                if (guide.role === "about") assert.equal(links.length, 6);
                else assert.equal(links.length, 0, `duplicate download links in ${guide.role}`);
                for (const [url] of links) {
                    assert.ok(catalog.models.some(model => url.includes(model.revision) && url.endsWith(model.filename)));
                }
            }
        }
    }
});

test("toolbar toggles details, localizes and hides controls for older graphs", () => {
    function element(tag) {
        return {tag, style: {}, events: {}, children: [], attributes: {},
            setAttribute(name, value) {this.attributes[name] = value;},
            addEventListener(name, callback) {this.events[name] = callback;},
            append(...children) {this.children.push(...children);},
            replaceChildren(...children) {this.children = children;}};
    }
    const document = {createElement: element, body: element("body")};
    let extension;
    const app = {rootGraph: {_nodes: [note("about"), detailNote()]},
        registerExtension(value) {extension = value;}};
    const source = readFileSync(new URL("../web/guide-controls.js", import.meta.url), "utf8")
        .replace(/import[\s\S]*?from\s+"[^"\n]+";/g, "");
    runInNewContext(source, {app, document, guideLanguages, detailGuideNodes,
        guideNodes: graph => graph._nodes.filter(node => node.properties?.drama3Guide),
        restoreGuideLanguage, setGuideLanguage, setGuideDetails});
    extension.setup();
    const toolbar = document.body.children[0];
    const [, select, button] = toolbar.children;
    assert.equal(button.hidden, false);
    assert.match(button.textContent, /자세한 설명/);
    const event = {stopPropagation() {}};
    button.events.click(event);
    assert.equal(app.rootGraph._nodes[1].flags.collapsed, false);
    button.events.click(event);
    assert.equal(app.rootGraph._nodes[1].flags.collapsed, true);
    select.value = "en";
    select.events.change(event);
    assert.equal(button.textContent, "Toggle detailed help");
    app.rootGraph = {_nodes: [note()]};
    extension.afterConfigureGraph();
    assert.equal(button.hidden, true);
    app.rootGraph = {_nodes: []};
    extension.afterConfigureGraph();
    assert.equal(toolbar.style.display, "none");
});
