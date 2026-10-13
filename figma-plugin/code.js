// Design Agent Hub local Figma plugin.
// It creates native editable nodes in the currently open Figma document.
// Only process a spec explicitly submitted from the plugin UI.

figma.showUI(__html__, { width: 420, height: 620, themeColors: true });

function parseHex(hex) {
  const clean = String(hex || "#FFFFFF").replace("#", "").trim();
  if (!/^[0-9a-fA-F]{6}$/.test(clean)) throw new Error("Colors must use six-digit hex, e.g. #FFFFFF.");
  return {
    r: parseInt(clean.slice(0, 2), 16) / 255,
    g: parseInt(clean.slice(2, 4), 16) / 255,
    b: parseInt(clean.slice(4, 6), 16) / 255,
  };
}

function paint(hex) {
  return { type: "SOLID", color: parseHex(hex) };
}

function safeText(value, max = 500) {
  const text = String(value ?? "").trim();
  if (!text || text.length > max) throw new Error("Text must be non-empty and under " + max + " characters.");
  return text;
}

async function buildDesign(spec) {
  if (!spec || !Array.isArray(spec.frames) || spec.frames.length < 1 || spec.frames.length > 12) {
    throw new Error("Provide 1-12 frames in the spec.");
  }
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Medium" });
  const created = [];

  for (const item of spec.frames) {
    const width = Number(item.width || 1080);
    const height = Number(item.height || 1080);
    if (![width, height].every(Number.isFinite) || width < 100 || height < 100 || width > 4000 || height > 4000) {
      throw new Error("Frame dimensions must be between 100 and 4000 pixels.");
    }
    const frame = figma.createFrame();
    frame.name = safeText(item.name || "Design Frame", 100);
    frame.resize(width, height);
    frame.x = Number.isFinite(Number(item.x)) ? Number(item.x) : created.length * (width + 80);
    frame.y = Number.isFinite(Number(item.y)) ? Number(item.y) : 0;
    frame.fills = [paint(item.background || "#FFFFFF")];
    frame.clipsContent = true;
    frame.layoutMode = "NONE";
    const elements = Array.isArray(item.elements) ? item.elements : [];
    if (elements.length > 100) throw new Error("Each frame can contain at most 100 elements.");

    for (const el of elements) {
      const x = Math.max(0, Math.min(width - 1, Number(el.x || 0)));
      const y = Math.max(0, Math.min(height - 1, Number(el.y || 0)));
      const w = Math.max(1, Math.min(width, Number(el.width || 100)));
      const h = Math.max(1, Math.min(height, Number(el.height || 40)));
      if (el.type === "text") {
        const node = figma.createText();
        node.name = safeText(el.name || "Text", 100);
        node.fontName = { family: "Inter", style: el.weight === "medium" ? "Medium" : "Regular" };
        node.characters = safeText(el.text, 1000);
        node.fontSize = Math.max(8, Math.min(144, Number(el.fontSize || 24)));
        node.fills = [paint(el.color || "#111827")];
        node.x = x; node.y = y;
        node.resize(w, h);
        frame.appendChild(node);
      } else if (el.type === "rect" || el.type === "ellipse") {
        const node = el.type === "ellipse" ? figma.createEllipse() : figma.createRectangle();
        node.name = safeText(el.name || el.type, 100);
        node.x = x; node.y = y;
        node.resize(w, h);
        node.fills = [paint(el.color || "#E5E7EB")];
        if (el.radius && el.type === "rect") node.cornerRadius = Math.max(0, Math.min(100, Number(el.radius)));
        frame.appendChild(node);
      } else {
        throw new Error("Unsupported element type: " + String(el.type) + ". Use text, rect, or ellipse.");
      }
    }
    created.push(frame);
  }
  figma.currentPage.selection = created;
  figma.viewport.scrollAndZoomIntoView(created);
  return { frames: created.length, nodes: created.reduce((sum, frame) => sum + frame.children.length + 1, 0) };
}

figma.ui.onmessage = async (message) => {
  if (!message || message.type !== "build") return;
  try {
    const result = await buildDesign(message.spec);
    figma.ui.postMessage({ type: "result", ok: true, result });
  } catch (error) {
    figma.ui.postMessage({ type: "result", ok: false, error: String(error && error.message ? error.message : error) });
  }
};
