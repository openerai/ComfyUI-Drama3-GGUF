import { app } from "../../scripts/app.js";
import { guideNodes, restoreGuideLanguage, setGuideLanguage } from "./guide-language.js?v=0.1.9";

let toolbar;
let select;

function updateToolbar() {
    const graph = app.rootGraph;
    const nodes = guideNodes(graph);
    if (!toolbar) {
        toolbar = document.createElement("label");
        toolbar.className = "drama3-guide-language";
        toolbar.style.cssText = "position:fixed;left:220px;top:65px;z-index:40;"
            + "display:flex;align-items:center;gap:8px;padding:6px 10px;"
            + "background:#222;border:1px solid #555;border-radius:7px;color:#fff;font:13px sans-serif;";
        const label = document.createElement("span");
        label.textContent = "Guide language";
        select = document.createElement("select");
        select.setAttribute("aria-label", "Drama3 guide language / 설명 언어");
        select.style.cssText = "background:#34383f;color:#fff;border:1px solid #777;"
            + "border-radius:4px;padding:3px 6px;font:13px sans-serif;";
        for (const [value, text] of [["ko", "한국어"], ["en", "English"]]) {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = text;
            select.append(option);
        }
        select.addEventListener("change", event => {
            event.stopPropagation();
            setGuideLanguage(app.rootGraph, select.value);
        });
        toolbar.addEventListener("keydown", event => event.stopPropagation());
        toolbar.append(label, select);
        document.body.append(toolbar);
    }
    toolbar.style.display = nodes.length ? "flex" : "none";
    const about = nodes.find(node => node.properties.drama3Guide.role === "about") ?? nodes[0];
    if (about) select.value = about.properties.drama3Guide.locale;
}

app.registerExtension({
    name: "Drama3GGUF.GuideLanguage",
    setup() {
        restoreGuideLanguage(app.rootGraph);
        updateToolbar();
    },
    afterConfigureGraph() {
        restoreGuideLanguage(app.rootGraph);
        updateToolbar();
    },
});
