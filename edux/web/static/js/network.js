// The concept network on the student's page (decision 0029), from the design preview synapse-concept-network.html:
// every idea in the course, sized by importance, grouped by topic, linked as the course pack links them, and coloured by
// the student's level. Levels only, never a probability (decision 0024): each level sits at a fixed point on the ramp.
(function () {
  "use strict";
  const LV = { secure: "Secure", developing: "Developing", review: "Needs review", new: "New", taught: "Taught in class, not yet checked", none: "Not started" };
  const AT = { new: 0.1, review: 0.35, developing: 0.55, secure: 0.95 }; // where each level sits on the needs-work-to-secure ramp
  const RED = [214, 60, 44], YEL = [242, 194, 48], GRN = [47, 158, 90];
  const mix = (c1, c2, t) => c1.map((v, i) => Math.round(v + (c2[i] - v) * t));
  const colOf = (p) => { const t = Math.min(1, Math.max(0, (p - 0.1) / 0.85)); const c = t < 0.5 ? mix(RED, YEL, t / 0.5) : mix(YEL, GRN, (t - 0.5) / 0.5); return "rgb(" + c + ")"; };
  const colour = (n) => (n.level in AT ? colOf(AT[n.level]) : null);
  const SVGNS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, text, parent) {  // text is always set as text, so a name or a note can never become markup
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, v));
    if (text != null) node.textContent = text;
    if (parent) parent.appendChild(node);
    return node;
  }
  function svgEl(tag, attrs, parent) {
    const node = document.createElementNS(SVGNS, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, v));
    if (parent) parent.appendChild(node);
    return node;
  }

  function mount(host, data) {
    host.textContent = "";
    const N = data.nodes.map((n) => ({ ...n })), byId = Object.fromEntries(N.map((n) => [n.id, n]));
    const E = data.edges.filter((e) => byId[e.a] && byId[e.b]).map((e) => ({ ...e, s: byId[e.a], t2: byId[e.b] }));
    const SEC = Object.fromEntries(data.bands.map((b) => [b.id, b.name]));
    const root = el("div", { class: "cn" }, null, host);
    const taught = N.some((n) => n.level === "taught");
    const top = el("header", { class: "top" }, null, root), intro = el("div", null, null, top);
    el("h3", null, "How " + data.course + " fits together", intro);
    el("p", null, N.length + " ideas. Bigger circles matter more for the exam; colour shows how well you know each one. Hover over or tap an idea; drag to rearrange.", intro);
    const legend = el("div", { class: "legend" }, null, top);
    const grad = el("span", { class: "grad" }, null, legend);
    el("b", null, "Needs work", grad); el("i", null, null, grad); el("b", null, "Secure", grad);
    function key(label, w, h, shape) {
      const span = el("span", null, null, legend), icon = svgEl("svg", { width: w, height: h, "aria-hidden": "true" }, span);
      svgEl(shape[0], shape[1], icon); span.appendChild(document.createTextNode(label));
    }
    key("Not started", 14, 14, ["circle", { cx: 7, cy: 7, r: 6, fill: "#bdbcb6" }]);
    if (taught) key("Taught in class, not yet checked", 14, 14, ["circle", { cx: 7, cy: 7, r: 5.5, fill: "#bdbcb6", stroke: "#f2f1ec", "stroke-width": 1.5, "stroke-dasharray": "2 2" }]);
    key("Builds on", 26, 8, ["path", { d: "M1 4H25", stroke: "#c9c8c2", "stroke-width": 1.5 }]);
    key("Works the same way", 26, 8, ["path", { d: "M1 4H25", stroke: "#c9c8c2", "stroke-width": 1.5, "stroke-dasharray": "5 4" }]);
    key("Easy to mix up", 26, 8, ["path", { d: "M1 4H25", stroke: "#ff7a5c", "stroke-width": 2, "stroke-dasharray": "1.5 4", "stroke-linecap": "round" }]);
    const stageEl = el("div", { class: "stage" }, null, root);
    svgEl("svg", { class: "net", role: "img" }, stageEl);
    el("div", { class: "tip", "aria-live": "polite" }, null, stageEl);
    el("p", { class: "foot" }, "Circle size is Synapse's importance score for each idea (exam weight and how much else depends on it). Levels come from answers only, never from chat.", root);
    const svg = root.querySelector("svg.net"), stage = root.querySelector(".stage"), tip = root.querySelector(".tip");
    svg.setAttribute("aria-label", "Network of the ideas in " + data.course);
    if (!N.length) return { select() {} };

    const imps = N.map((n) => n.imp), lo = Math.min(...imps), hi = Math.max(...imps), span = hi - lo || 1;
    N.forEach((n) => { n.r = 7 + 19 * Math.sqrt((n.imp - lo) / span); n.lw = n.short.length * 6.6; });
    const impWord = (n) => (n.imp >= lo + span * 0.66 ? "High" : n.imp >= lo + span * 0.33 ? "Medium" : "Lower");
    // seeded layout: the same picture every time
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const secIds = data.bands.map((b) => b.id), C = {};
    secIds.forEach((s, i) => { const a = -Math.PI / 2 + (i * Math.PI * 2) / secIds.length; C[s] = { x: Math.cos(a) * 300, y: Math.sin(a) * 230 }; });
    N.forEach((n) => { const c = C[n.band] || { x: 0, y: 0 }; n.x = c.x + (rnd() - 0.5) * 200; n.y = c.y + (rnd() - 0.5) * 200; n.vx = 0; n.vy = 0; });
    function tick(alpha) {
      for (let i = 0; i < N.length; i++) for (let j = i + 1; j < N.length; j++) {
        const a = N[i], b = N[j]; const dx = b.x - a.x, dy = b.y - a.y, d2 = dx * dx + dy * dy || 1, d = Math.sqrt(d2);
        const f = (-5200 / d2) * alpha; a.vx += (dx / d) * f; a.vy += (dy / d) * f; b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
        const minX = Math.max((a.lw + b.lw) / 2 + 14, a.r + b.r + 14), minY = a.r + b.r + 30;
        if (Math.abs(dx) < minX && Math.abs(dy) < minY) {
          const px = minX - Math.abs(dx), py = minY - Math.abs(dy);
          if (py < px) { const s = Math.sign(dy) || 1; a.vy -= s * py * 0.25; b.vy += s * py * 0.25; } else { const s = Math.sign(dx) || 1; a.vx -= s * px * 0.12; b.vx += s * px * 0.12; }
        }
      }
      E.forEach((e) => { const a = e.s, b = e.t2, dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || 1, L = e.t === "confusable" ? 190 : 140, k = ((d - L) / d) * 0.06 * alpha;
        a.vx += dx * k; a.vy += dy * k; b.vx -= dx * k; b.vy -= dy * k; });
      N.forEach((n) => { const c = C[n.band] || { x: 0, y: 0 }; n.vx += (c.x - n.x) * 0.008 * alpha; n.vy += (c.y - n.y) * 0.008 * alpha; n.vx -= n.x * 0.002 * alpha; n.vy -= n.y * 0.002 * alpha;
        if (!n.fixed) { n.x += n.vx; n.y += n.vy; } n.vx *= 0.6; n.vy *= 0.6; });
    }
    for (let i = 0; i < 1200; i++) tick(1 - i / 1300);

    let vb;
    function fit() {
      const xs = N.flatMap((n) => [n.x - n.r - 10, n.x + n.r + n.lw / 2 + 10]), ys = N.flatMap((n) => [n.y - n.r - 30, n.y + n.r + 26]);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
      vb = [x0, y0, x1 - x0, y1 - y0]; svg.setAttribute("viewBox", vb.join(" "));
    }
    function build() {
      E.forEach((e, i) => {
        const l = document.createElementNS(SVGNS, "line"); l.setAttribute("class", "e"); l.dataset.i = i;
        const st = e.t === "confusable" ? { stroke: "var(--cn-red)", "stroke-width": 2.2, "stroke-dasharray": "1.5 5", "stroke-linecap": "round" }
          : e.t === "analogous" ? { stroke: "var(--cn-soft)", "stroke-width": 1.5, "stroke-dasharray": "6 5" } : { stroke: "var(--cn-soft)", "stroke-width": 1.5 };
        Object.entries(st).forEach(([k, v]) => l.setAttribute(k, v)); svg.appendChild(l);
      });
      N.forEach((n) => {
        const g = document.createElementNS(SVGNS, "g"); g.setAttribute("class", "n"); g.dataset.id = n.id; g.setAttribute("tabindex", "0");
        g.setAttribute("role", "button"); g.setAttribute("aria-label", n.name + ": " + LV[n.level] + (n.note ? ", " + n.note : ""));
        const c = document.createElementNS(SVGNS, "circle"); c.setAttribute("class", "dot"); c.setAttribute("r", n.r);
        const fill = colour(n);
        if (fill) { c.setAttribute("fill", fill); c.setAttribute("stroke", "rgb(0 0 0/.25)"); c.setAttribute("stroke-width", "1"); }
        else { c.setAttribute("fill", "#bdbcb6"); if (n.level === "taught") { c.setAttribute("stroke", "var(--cn-ink)"); c.setAttribute("stroke-width", "1.5"); c.setAttribute("stroke-dasharray", "3 3"); } }
        const t = document.createElementNS(SVGNS, "text"); t.setAttribute("class", "lbl"); t.setAttribute("text-anchor", "middle"); t.setAttribute("y", n.r + 16); t.textContent = n.short;
        g.appendChild(c); g.appendChild(t); svg.appendChild(g);
      });
    }
    function draw() {
      svg.querySelectorAll(".e").forEach((l) => { const e = E[l.dataset.i]; l.setAttribute("x1", e.s.x); l.setAttribute("y1", e.s.y); l.setAttribute("x2", e.t2.x); l.setAttribute("y2", e.t2.y); });
      svg.querySelectorAll(".n").forEach((g) => { const n = byId[g.dataset.id]; g.setAttribute("transform", "translate(" + n.x + "," + n.y + ")"); });
    }
    fit(); build(); draw();

    const nb = (id) => E.filter((e) => e.a === id || e.b === id);
    function showTip(n, ev) {
      const L = nb(n.id), rel = (t) => L.filter((e) => e.t === t || (t === "prerequisite" && e.t === "causal")).map((e) => byId[e.a === n.id ? e.b : e.a].short);
      const parts = [["Builds on / leads to", rel("prerequisite")], ["Works the same way as", rel("analogous")], ["Easy to mix up with", rel("confusable")]].filter((p) => p[1].length);
      tip.textContent = "";
      el("h4", null, n.name, tip);
      el("div", { class: "meta" }, (SEC[n.band] || "") + (n.concept ? " · " + n.concept : ""), tip);
      const chip = el("span", { class: "chip lvl" }, LV[n.level] || n.level, tip);
      const fill = colour(n);
      if (fill) chip.style.background = fill; else chip.setAttribute("class", "chip unseen");
      el("span", { class: "chip plain" }, impWord(n) + " importance", tip);
      if (n.test) el("span", { class: "chip" }, n.test, tip);
      if (n.note) el("p", { class: "links" }, n.note, tip);
      if (n.q) el("span", { class: "q" }, n.q, el("p", null, null, tip));
      if (n.d) el("p", null, n.d, tip);
      parts.forEach((p) => { const line = el("p", { class: "links" }, null, tip); el("b", null, p[0] + ":", line); line.appendChild(document.createTextNode(" " + p[1].join(", "))); });
      placeTip(ev); tip.classList.add("show");
      const on = new Set([n.id]); L.forEach((e) => { on.add(e.a); on.add(e.b); }); svg.classList.add("dim");
      svg.querySelectorAll(".n").forEach((g) => g.classList.toggle("on", on.has(g.dataset.id)));
      svg.querySelectorAll(".e").forEach((l) => { const e = E[l.dataset.i]; l.classList.toggle("on", e.a === n.id || e.b === n.id); });
    }
    function placeTip(ev) {
      const r = stage.getBoundingClientRect(); let x = ev.clientX - r.left + 18, y = ev.clientY - r.top + 18;
      if (x + 310 > r.width) x = ev.clientX - r.left - 318;
      if (y + tip.offsetHeight > r.height) y = Math.max(8, r.height - tip.offsetHeight - 8);
      tip.style.left = Math.max(8, x) + "px"; tip.style.top = y + "px";
    }
    function hideTip() { tip.classList.remove("show"); svg.classList.remove("dim"); }
    let drag = null, raf = 0, heat = 0;
    const toSvg = (ev) => { const r = svg.getBoundingClientRect(), s = Math.max(vb[2] / r.width, vb[3] / r.height), ox = vb[0] + (vb[2] - r.width * s) / 2, oy = vb[1] + (vb[3] - r.height * s) / 2; return { x: ox + (ev.clientX - r.left) * s, y: oy + (ev.clientY - r.top) * s }; };
    const loop = () => { if (heat > 0) { tick(0.25); draw(); heat--; raf = requestAnimationFrame(loop); } else raf = 0; };
    svg.addEventListener("pointerover", (ev) => { const g = ev.target.closest(".n"); if (g && !drag) showTip(byId[g.dataset.id], ev); });
    svg.addEventListener("pointermove", (ev) => {
      if (drag) { const p = toSvg(ev); drag.x = p.x; drag.y = p.y; heat = 40; if (!raf) loop(); placeTip(ev); return; }
      const g = ev.target.closest(".n"); if (g) placeTip(ev);
    });
    svg.addEventListener("pointerout", (ev) => { if (!drag && ev.target.closest(".n") && !(ev.relatedTarget && ev.relatedTarget.closest && ev.relatedTarget.closest(".n"))) hideTip(); });
    svg.addEventListener("pointerdown", (ev) => { const g = ev.target.closest(".n"); if (!g) return; drag = byId[g.dataset.id]; drag.fixed = true; svg.setPointerCapture(ev.pointerId); });
    svg.addEventListener("pointerup", () => { if (drag) { drag.fixed = false; drag = null; hideTip(); } });
    svg.addEventListener("focusin", (ev) => { const g = ev.target.closest(".n"); if (g) { const b = g.getBoundingClientRect(); showTip(byId[g.dataset.id], { clientX: b.right, clientY: b.top }); } });
    svg.addEventListener("focusout", hideTip);
    return {
      select(id) { const g = svg.querySelector('.n[data-id="' + CSS.escape(id) + '"]'); if (g) g.focus(); },
    };
  }

  window.SynapseNetwork = { mount };
})();
