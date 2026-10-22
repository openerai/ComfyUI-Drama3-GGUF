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

const stackedCollapse = Symbol("drama3StackedCollapse");

function arrangeDetailStack(graph, anchor) {
    const group = anchor.properties.drama3Guide.stack;
    // Only the supplied help column opts in. A note moved to another column stays there.
    const nodes = detailGuideNodes(graph).filter(node => node.properties.drama3Guide.stack === group
        && Math.abs(node.pos[0] - anchor.pos[0]) < 1)
        .sort((a, b) => a.properties.drama3Guide.stackOrder - b.properties.drama3Guide.stackOrder);
    let y = nodes[0].pos[1];
    for (const node of nodes) {
        node.pos = [node.pos[0], y];
        // The title bar exists in both states; opening adds the note's body height.
        y += (node.flags?.collapsed ? 0 : node.size[1]) + 70;
        node.setDirtyCanvas?.(true, true);
    }
}

export function installGuideDetailStack(graph) {
    for (const node of detailGuideNodes(graph)) {
        const guide = node.properties.drama3Guide;
        if (!guide.stack || !Number.isFinite(guide.stackOrder) || node[stackedCollapse]
            || typeof node.collapse !== "function") continue;
        const collapse = node.collapse;
        node.collapse = function(...args) {
            const before = Boolean(this.flags?.collapsed);
            const result = collapse.apply(this, args);
            if (before !== Boolean(this.flags?.collapsed)) arrangeDetailStack(this.graph ?? graph, this);
            return result;
        };
        node[stackedCollapse] = true;
    }
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
