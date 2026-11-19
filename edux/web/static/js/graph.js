// The course graph as SVG (decision 0024). Two drawings of the same data and a plain list as the accessible alternative:
//   map  - containment: topics hold concepts hold parts, each part a disc sized by importance.
//   path - the prerequisite chain, left to right.
//   list - a table; the same information, readable by a screen reader.
// Colour is only ever a part's level (from an optional overlay) and ring and fill repeat it. Edge type is line style.
// All text from the API is set with textContent, never as HTML.
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const SLOT_W = 124, SLOT_H = 96, CELL_PAD = 14, CELL_GAP = 14, TOPIC_GAP = 36, COLLAPSE_OVER = 12;

  const RELATION = {
    "prerequisite:out": "Comes before", "prerequisite:in": "Needs first", "analogous:out": "Works like", "analogous:in": "Works like",
    "confusable:out": "Often confused with", "confusable:in": "Often confused with", "causal:out": "Leads to", "causal:in": "Comes from",
  };
  const LEVEL_WORDS = {
    new: "new", developing: "developing", secure: "secure", taught: "taught in class, not yet checked", none: "no answers yet",
  };

  function svgEl(name, attrs, parent) {
    const node = document.createElementNS(NS, name);
    for (const k in attrs || {}) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }
  function htmlEl(name, text, parent, cls) {
    const node = document.createElement(name);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }
  function lines(text, width) {            // at most two lines, broken at spaces, with an ellipsis if cut
    const words = String(text).split(/\s+/), out = [""];
    for (const w of words) {
      const cur = out[out.length - 1];
      if ((cur + " " + w).trim().length <= width) out[out.length - 1] = (cur + " " + w).trim();
      else if (out.length < 2) out.push(w);
      else { out[1] = (out[1] + "…").slice(0, width); break; }
    }
    return out;
  }
  const radius = (n) => 9 + 15 * Math.sqrt(Math.max(0, Math.min(1, n.importance || 0)));

  function mount(container, data, options) {
    options = options || {};
    const nodes = new Map(data.nodes.map((n) => [n.id, n]));
    const kids = new Map();
    data.nodes.forEach((n) => { if (n.parent) (kids.get(n.parent) || kids.set(n.parent, []).get(n.parent)).push(n); });
    const parts = data.nodes.filter((n) => n.level === "part");
    const state = { view: options.view || "map", selected: null, overlay: options.overlay || {}, expanded: new Set(), order: [], pos: new Map() };

    const bar = htmlEl("div", null, container, "viewbar");
    const stage = htmlEl("div", null, container, "stage");
    const panel = htmlEl("div", null, container, "panel");
    panel.setAttribute("aria-live", "polite");
    const buttons = {};
    [["map", "Map"], ["path", "Path"], ["list", "List"]].forEach(([id, label]) => {
      const b = htmlEl("button", label, bar, "quiet");
      b.type = "button";
      b.addEventListener("click", () => { state.view = id; draw(); });
      buttons[id] = b;
    });

    function level(id) { return (state.overlay[id] && state.overlay[id].level) || "plain"; }

    function related(id) {                  // links touching this node, its concept or its topic
      const own = new Set([id]);
      let p = nodes.get(id);
      while (p && p.parent) { own.add(p.parent); p = nodes.get(p.parent); }
      return data.edges.filter((e) => own.has(e.from) || own.has(e.to)).map((e) => {
        const out = own.has(e.from);
        return { edge: e, other: out ? e.to : e.from, key: e.type + ":" + (out ? "out" : "in") };
      });
    }

    // --- drawing a part -----------------------------------------------------------------------------------------
    function drawPart(parent, n, x, y, size) {
      const g = svgEl("g", { class: "node disc " + level(n.id), tabindex: -1, role: "button", "data-id": n.id, transform: `translate(${x},${y})` }, parent);
      const r = size || radius(n), ov = state.overlay[n.id];
      g.setAttribute("aria-label", n.name + ", " + ((ov && ov.label) || LEVEL_WORDS[level(n.id)]) + (ov && ov.note ? ", " + ov.note : ""));
      if (ov && typeof ov.fade === "number") g.setAttribute("opacity", String(ov.fade));
      svgEl("circle", { class: "ring", r: r, cx: 0, cy: 0 }, g);
      if (level(n.id) === "developing") svgEl("path", { class: "half", d: `M0 ${-r} A${r} ${r} 0 0 0 0 ${r} Z` }, g);
      lines(n.name, 17).forEach((t, i) => { if (t) svgEl("text", { y: r + 14 + i * 14, "text-anchor": "middle" }, g).textContent = t; });
      g.addEventListener("click", () => select(n.id));
      g.addEventListener("keydown", (ev) => keys(ev, n.id));
      g.addEventListener("focus", () => highlight(n.id));
      g.addEventListener("blur", () => highlight(state.selected));
      g.addEventListener("mouseenter", () => highlight(n.id));
      g.addEventListener("mouseleave", () => highlight(state.selected));
      state.order.push(n.id);
      state.pos.set(n.id, { x: x, y: y, r: r });
      return g;
    }

    function drawCollapsed(parent, concept, x, y) {  // a big concept: one disc whose ring shows how its parts are spread
      const ps = kids.get(concept.id) || [], g = svgEl("g", { class: "node collapsed", tabindex: -1, role: "button", transform: `translate(${x},${y})`, "data-id": concept.id }, parent);
      g.setAttribute("aria-label", concept.name + ", " + ps.length + " parts, press to open");
      svgEl("circle", { class: "ring plain", r: 30 }, g);
      const counts = { new: 0, developing: 0, secure: 0, taught: 0, none: 0, plain: 0 };
      ps.forEach((p) => { counts[level(p.id)] += 1; });
      let a0 = -Math.PI / 2;
      ["new", "developing", "secure"].forEach((lv) => {
        if (!counts[lv]) return;
        const a1 = a0 + (counts[lv] / ps.length) * 2 * Math.PI, big = a1 - a0 > Math.PI ? 1 : 0;
        const pt = (a) => `${(30 * Math.cos(a)).toFixed(2)} ${(30 * Math.sin(a)).toFixed(2)}`;
        svgEl("path", { class: "seg " + lv, d: `M${pt(a0)} A30 30 0 ${big} 1 ${pt(a1 - 0.0001)}` }, g);
        a0 = a1;
      });
      svgEl("text", { class: "count", y: 5, "text-anchor": "middle" }, g).textContent = String(ps.length);
      lines(concept.name, 17).forEach((t, i) => { if (t) svgEl("text", { y: 48 + i * 14, "text-anchor": "middle" }, g).textContent = t; });
      const open = () => { state.expanded.add(concept.id); draw(); };
      g.addEventListener("click", open);
      g.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); open(); } else keys(ev, concept.id); });
      state.order.push(concept.id);
      state.pos.set(concept.id, { x: x, y: y, r: 30 });
    }

    // --- the two drawings ---------------------------------------------------------------------------------------
    function layoutMap(svg, width) {
      let y = 0;
      const gMain = svgEl("g", {}, svg), gEdges = svgEl("g", { class: "edges" }, svg);
      data.nodes.filter((n) => n.level === "topic").forEach((topic) => {
        svgEl("text", { class: "topic", x: 0, y: y + 22 }, gMain).textContent = topic.name;
        y += 40;
        let x = 0, rowH = 0;
        (kids.get(topic.id) || []).forEach((concept) => {
          const ps = kids.get(concept.id) || [];
          const collapsed = ps.length > COLLAPSE_OVER && !state.expanded.has(concept.id);
          const cols = collapsed ? 1 : Math.max(1, Math.min(ps.length, Math.floor((width - 2 * CELL_PAD) / SLOT_W), 6));
          const rows = collapsed ? 1 : Math.ceil(ps.length / cols);
          const titleW = (concept.name.length + (concept.spec_ref ? concept.spec_ref.length + 2 : 0)) * 6.6 + 2 * CELL_PAD;
          const cw = Math.min(width, Math.max(cols * SLOT_W + 2 * CELL_PAD, titleW)), ch = (collapsed ? 120 : rows * SLOT_H) + 30 + 2 * CELL_PAD;
          if (x > 0 && x + cw > width) { x = 0; y += rowH + CELL_GAP; rowH = 0; }
          svgEl("rect", { class: "cell", x: x, y: y, width: cw, height: ch }, gMain);
          const title = svgEl("text", { class: "concept", x: x + CELL_PAD, y: y + CELL_PAD + 10 }, gMain);
          title.textContent = concept.name + (concept.spec_ref ? "  " + concept.spec_ref : "");
          if (collapsed) drawCollapsed(gMain, concept, x + cw / 2, y + 30 + CELL_PAD + 40);
          else ps.forEach((p, i) => drawPart(gMain, p, x + CELL_PAD + (i % cols) * SLOT_W + SLOT_W / 2, y + 30 + CELL_PAD + Math.floor(i / cols) * SLOT_H + 28));
          state.pos.set(concept.id, state.pos.get(concept.id) || { x: x + cw / 2, y: y, r: 0 });
          x += cw + CELL_GAP; rowH = Math.max(rowH, ch);
        });
        y += rowH + TOPIC_GAP;
      });
      svg.setAttribute("viewBox", `0 0 ${width} ${Math.max(y, 80)}`);
      return gEdges;
    }

    function layoutPath(svg, width) {
      const pre = data.edges.filter((e) => e.type === "prerequisite" && nodes.get(e.from).level === "part" && nodes.get(e.to).level === "part");
      const layer = new Map(parts.map((p) => [p.id, 0]));
      for (let pass = 0; pass < parts.length; pass++) {      // longest chain of prerequisites decides the column
        let moved = false;
        pre.forEach((e) => { if (layer.get(e.to) < layer.get(e.from) + 1) { layer.set(e.to, layer.get(e.from) + 1); moved = true; } });
        if (!moved) break;
      }
      const linked = new Set(); pre.forEach((e) => { linked.add(e.from); linked.add(e.to); });
      const loose = parts.filter((p) => !linked.has(p.id));
      const cols = []; parts.filter((p) => linked.has(p.id)).forEach((p) => (cols[layer.get(p.id)] = cols[layer.get(p.id)] || []).push(p));
      const index = new Map(parts.map((p, i) => [p.id, i]));
      const place = (id) => cols[layer.get(id)].findIndex((q) => q.id === id);   // a part's row in its column
      for (let sweep = 0; sweep < 4; sweep++) cols.forEach((col) => {            // barycentre: sit near what you are linked to
        if (!col) return;
        const rank = new Map();
        col.forEach((p) => {
          const near = pre.filter((e) => e.to === p.id || e.from === p.id).map((e) => (e.to === p.id ? e.from : e.to));
          rank.set(p.id, near.length ? near.reduce((sum, id) => sum + place(id), 0) / near.length : index.get(p.id));
        });
        col.sort((a, b) => rank.get(a.id) - rank.get(b.id) || index.get(a.id) - index.get(b.id));
      });
      const gMain = svgEl("g", {}, svg), gEdges = svgEl("g", { class: "edges always" }, svg);
      const colW = Math.max(150, Math.min(220, (width - 80) / Math.max(1, cols.length))), tall = Math.max(...cols.map((c) => (c ? c.length : 0)), 1);
      cols.forEach((col, c) => (col || []).forEach((p, i) => drawPart(gMain, p, 40 + c * colW + colW / 2 - 20, 50 + i * SLOT_H)));
      let bottom = 20 + (pre.length ? tall * SLOT_H : 0), wide = Math.max(width, 80 + cols.length * colW);
      if (loose.length) {
        svgEl("text", { class: "concept", x: 0, y: bottom + 10 }, gMain).textContent = pre.length ? "Not linked into a path" : "No prerequisite links in this course yet";
        const per = Math.max(1, Math.floor(wide / SLOT_W));
        loose.forEach((p, i) => drawPart(gMain, p, SLOT_W / 2 + (i % per) * SLOT_W, bottom + 52 + Math.floor(i / per) * SLOT_H));
        bottom += 52 + Math.ceil(loose.length / per) * SLOT_H;
      }
      svg.setAttribute("viewBox", `0 0 ${wide} ${bottom + 10}`);
      return gEdges;
    }

    // --- links, selection, keyboard -----------------------------------------------------------------------------
    function drawEdges(layer, id, always) {
      layer.textContent = "";
      const shown = always ? data.edges.filter((e) => e.type === "prerequisite") : id ? related(id).map((r) => r.edge) : [];
      const anchor = (nid) => state.pos.get(nid) || state.pos.get((nodes.get(nid) || {}).parent);
      shown.forEach((e) => {
        const a = anchor(e.from), b = anchor(e.to);
        if (!a || !b) return;
        const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1, ra = a.r ? a.r + 5 : 0, rb = b.r ? b.r + 6 : 0;
        const x1 = a.x + (dx / len) * ra, y1 = a.y + (dy / len) * ra, x2 = b.x - (dx / len) * rb, y2 = b.y - (dy / len) * rb;
        let nx = -dy / len, ny = dx / len;
        if (ny > 0 || (ny === 0 && nx < 0)) { nx = -nx; ny = -ny; }      // bow upwards, or to the right when level
        const bow = Math.min(46, len / 6 + 8), mx = (x1 + x2) / 2 + nx * bow, my = (y1 + y2) / 2 + ny * bow;
        const d = `M${x1} ${y1} Q${mx} ${my} ${x2} ${y2}`;
        svgEl("path", { class: "edge " + e.type, d: d }, layer);
        if (e.type === "causal") svgEl("path", { class: "edge causal inner", d: d }, layer);
        if (e.type === "prerequisite") svgEl("circle", { class: "terminus", cx: x2, cy: y2, r: 3 }, layer);
        if (e.type === "confusable") svgEl("text", { class: "neq", x: mx, y: my - 4, "text-anchor": "middle" }, layer).textContent = "≠";
      });
    }

    let edgeLayer = null;
    function highlight(id) {
      const near = new Set(id ? [id].concat(related(id).map((r) => r.other)) : []);
      stage.classList.toggle("dimmed", !!id);
      stage.querySelectorAll(".node").forEach((g) => g.classList.toggle("near", near.has(g.getAttribute("data-id"))));
      if (edgeLayer) drawEdges(edgeLayer, id, state.view === "path" && !id);
    }

    function select(id) {
      state.selected = id;
      stage.querySelectorAll(".node").forEach((g) => g.classList.toggle("selected", g.getAttribute("data-id") === id));
      highlight(id);
      const n = nodes.get(id);
      panel.textContent = "";
      if (!n) { htmlEl("p", "Select a part to see what it needs first and what it is related to. The arrow keys move between parts.", panel, "muted"); return; }
      htmlEl("h3", n.name, panel);
      const facts = [n.level === "part" ? "A part" + (n.part_type ? " · " + n.part_type : "") : n.level === "concept" ? "A concept" : "A topic"];
      if (n.spec_ref) facts.push("Specification " + n.spec_ref);
      htmlEl("p", facts.join(" · "), panel, "muted");
      if (n.description) htmlEl("p", n.description, panel);
      const ov = state.overlay[n.id];
      if (ov) htmlEl("p", (ov.label || LEVEL_WORDS[ov.level]) + (ov.note ? " · " + ov.note : ""), panel, "levelline");
      if (n.level === "part") htmlEl("p", n.mark_points + " mark points · " + n.misconceptions + " common wrong ideas", panel, "muted");
      if (n.level === "concept") (kids.get(n.id) || []).forEach((p) => link(panel, p.id, "Part", p.name));
      related(id).forEach((r) => link(panel, r.other, RELATION[r.key], (nodes.get(r.other) || {}).name, r.edge.note));
    }
    function link(parent, id, label, name, note) {
      const row = htmlEl("div", null, parent, "related");
      htmlEl("span", label, row, "muted");
      const b = htmlEl("button", name, row, "quiet"); b.type = "button";
      b.addEventListener("click", () => { select(id); const g = stage.querySelector(`[data-id="${id}"]`); if (g) g.focus(); });
      if (note) htmlEl("small", note, row, "note");
    }

    function keys(ev, id) {
      const i = state.order.indexOf(id), step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[ev.key];
      if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(id); return; }
      if (ev.key === "Escape") { select(null); return; }
      if (!step) return;
      ev.preventDefault();
      const next = state.order[(i + step + state.order.length) % state.order.length], from = stage.querySelector(`[data-id="${id}"]`), to = stage.querySelector(`[data-id="${next}"]`);
      if (from) from.tabIndex = -1;
      if (to) { to.tabIndex = 0; to.focus(); }
    }

    // --- the list: the same data, as a table ---------------------------------------------------------------------
    function drawList() {
      const table = htmlEl("table", null, stage, "list");
      htmlEl("caption", "Every part of the course, with what it needs first and what it is related to", table);
      const head = htmlEl("tr", null, htmlEl("thead", null, table));
      ["Topic", "Concept", "Part", "Type", "Needs first", "Related to"].forEach((h) => { const th = htmlEl("th", h, head); th.scope = "col"; });
      const body = htmlEl("tbody", null, table);
      parts.forEach((p) => {
        const concept = nodes.get(p.parent) || {}, topic = nodes.get(concept.parent) || {}, row = htmlEl("tr", null, body);
        htmlEl("td", topic.name || "", row); htmlEl("td", concept.name || "", row);
        const cell = htmlEl("th", null, row); cell.scope = "row";
        const b = htmlEl("button", p.name, cell, "quiet"); b.type = "button"; b.addEventListener("click", () => select(p.id));
        htmlEl("td", p.part_type || "", row);
        const rel = related(p.id);
        htmlEl("td", rel.filter((r) => r.key === "prerequisite:in").map((r) => (nodes.get(r.other) || {}).name).join("; ") || "nothing", row);
        htmlEl("td", rel.filter((r) => r.key !== "prerequisite:in" && r.key !== "prerequisite:out").map((r) => RELATION[r.key].toLowerCase() + " " + (nodes.get(r.other) || {}).name).join("; "), row);
      });
    }

    function draw() {
      Object.keys(buttons).forEach((id) => buttons[id].setAttribute("aria-pressed", String(id === state.view)));
      stage.textContent = ""; stage.classList.remove("dimmed");
      state.order = []; state.pos = new Map();
      if (state.view === "list") { edgeLayer = null; drawList(); select(state.selected); return; }
      const width = Math.max(300, Math.floor(stage.clientWidth || container.clientWidth || 960));
      const svg = svgEl("svg", { role: "group", "aria-label": "Map of the course. Use the arrow keys to move between parts and Enter to read about one." }, stage);
      svg.setAttribute("width", String(width));
      edgeLayer = state.view === "path" ? layoutPath(svg, width) : layoutMap(svg, width);
      const first = stage.querySelector(".node"); if (first) first.tabIndex = 0;
      highlight(state.selected); if (state.selected) select(state.selected);
    }

    let timer = null, lastWidth = stage.clientWidth;
    window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(() => { if (stage.clientWidth !== lastWidth) { lastWidth = stage.clientWidth; if (state.view !== "list") draw(); } }, 150); });
    select(null);
    draw();
    return { setView: (v) => { state.view = v; draw(); }, setOverlay: (o) => { state.overlay = o || {}; draw(); }, select, state };
  }

  window.SynapseGraph = { mount };
})();
