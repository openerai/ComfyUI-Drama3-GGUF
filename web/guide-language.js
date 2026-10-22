export const GUIDE_LANGUAGES = [
    ["ko", "한국어"], ["en", "English"], ["ja", "日本語"], ["zh", "中文（简体）"],
];

export function guideNodes(graph) {
    return (graph?._nodes ?? []).filter(node => node.type === "MarkdownNote"
        && node.properties?.drama3Guide?.translations);
}

export function guideLanguages(graph) {
    const nodes = guideNodes(graph);
    return nodes.length ? GUIDE_LANGUAGES.filter(([locale]) => nodes.every(
        node => node.properties.drama3Guide.translations[locale])) : [];
}

export function detailGuideNodes(graph) {
    return guideNodes(graph).filter(node => node.properties.drama3Guide.detail === true);
}

export function setGuideDetails(graph, expanded) {
    graph.beforeChange?.();
    for (const node of detailGuideNodes(graph)) {
        // LiteGraph collapse() toggles; its argument forces permission, not the target state.
        if (Boolean(node.flags?.collapsed) === expanded) node.collapse(true);
    }
    graph.afterChange?.();
}

function textWidget(node) {
    return node.widgets?.find(widget => widget.name === "text");
}

function renderGuide(node, locale) {
    const guide = node.properties.drama3Guide;
    const translation = guide.translations[locale];
    const widget = textWidget(node);
    if (!translation || !widget) return;
    widget.value = translation.text;
    node.title = translation.title;
    guide.locale = locale;
    node.setDirtyCanvas?.(true, true);
}

export function setGuideLanguage(graph, locale) {
    if (!guideLanguages(graph).some(([value]) => value === locale)) return;
    const nodes = guideNodes(graph);
    graph.beforeChange?.();
    for (const node of nodes) {
        const guide = node.properties.drama3Guide;
        const widget = textWidget(node);
        // Preserve edits to the currently displayed guide when switching away.
        if (widget && guide.translations[guide.locale]) {
            guide.translations[guide.locale].text = widget.value;
        }
        renderGuide(node, locale);
    }
    graph.afterChange?.();
}

export function restoreGuideLanguage(graph) {
    for (const node of guideNodes(graph)) {
        const guide = node.properties.drama3Guide;
        const locale = GUIDE_LANGUAGES.some(([value]) => value === guide.locale)
            && guide.translations[guide.locale] ? guide.locale : "ko";
        const widget = textWidget(node);
        // The saved visible body includes edits made without using the selector.
        if (widget && typeof widget.value === "string") guide.translations[locale].text = widget.value;
        renderGuide(node, locale);
    }
}
