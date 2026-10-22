import { app } from "../../scripts/app.js";
import { guideNodes, guideLanguages, restoreGuideLanguage, setGuideLanguage,
    detailGuideNodes, setGuideDetails } from "./guide-language.js?v=0.2.1";

let toolbar;
let select;
let details;

const detailLabels = { ko: "자세한 설명 접기/펼치기", en: "Toggle detailed help",
    ja: "詳しい説明を開閉", zh: "展开/收起详细说明" };

function updateToolbar() {
    const graph = app.rootGraph;
    const nodes = guideNodes(graph);
    if (!toolbar) {
        toolbar = document.createElement("div");
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
        select.addEventListener("change", event => {
            event.stopPropagation();
            setGuideLanguage(app.rootGraph, select.value);
            updateToolbar();
        });
        details = document.createElement("button");
        details.type = "button";
        details.style.cssText = "background:#34383f;color:#fff;border:1px solid #777;"
            + "border-radius:4px;padding:4px 8px;font:13px sans-serif;cursor:pointer;";
        details.addEventListener("click", event => {
            event.stopPropagation();
            const nodes = detailGuideNodes(app.rootGraph);
            setGuideDetails(app.rootGraph, nodes.every(node => node.flags?.collapsed));
        });
        toolbar.addEventListener("keydown", event => event.stopPropagation());
        toolbar.append(label, select, details);
        document.body.append(toolbar);
    }
    select.replaceChildren(...guideLanguages(graph).map(([value, text]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = text;
        return option;
    }));
    toolbar.style.display = nodes.length ? "flex" : "none";
    const about = nodes.find(node => node.properties.drama3Guide.role === "about") ?? nodes[0];
    if (about) select.value = about.properties.drama3Guide.locale;
    details.hidden = !detailGuideNodes(graph).length;
    details.textContent = detailLabels[select.value] ?? detailLabels.en;
    details.setAttribute("aria-label", details.textContent);
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
