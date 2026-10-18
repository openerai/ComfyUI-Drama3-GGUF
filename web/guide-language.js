export function guideNodes(graph) {
    return (graph?._nodes ?? []).filter(node => node.type === "MarkdownNote"
        && node.properties?.drama3Guide?.translations);
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
    if (locale !== "ko" && locale !== "en") return;
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
        const locale = guide.locale === "en" ? "en" : "ko";
        const widget = textWidget(node);
        // The saved visible body includes edits made without using the selector.
        if (widget && typeof widget.value === "string") guide.translations[locale].text = widget.value;
        renderGuide(node, locale);
    }
}
