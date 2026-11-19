// The per-student teacher view (decision 0030): a "Sign in as demo teacher" button when demo mode is on, the class with
// each student's card, and one student's review. Everything comes from /api/teacher/class/<id>/review and
// .../student/<id>, which 404 unless the school turned the view on, or demo mode is on for a synthetic class. No chat or
// message text ever reaches this page. Plain text only: never HTML from data.
(function () {
  "use strict";
  const STORE = "synapse-key";
  function h(name, text, parent, cls) {
    const node = document.createElement(name);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }
  const dayName = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("en-GB", { weekday: "long" });
  const day = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
  const plural = (n, one, many) => n + " " + (n === 1 ? one : (many || one + "s"));
  const LEVELS = ["new", "developing", "secure"];
  const root = document.getElementById("review");
  const classBox = document.getElementById("review-class");
  const studentBox = document.getElementById("review-student");
  let classId = null, data = null, filter = null, search = "";

  async function offerDemo() {
    const box = document.querySelector("[data-demo]");
    if (!box || Synapse.key()) return;
    try { await Synapse.get("/api/demo/teacher"); } catch (e) { return; }   // 404: demo mode is off, or the class is not synthetic
    box.hidden = false;
    box.querySelector("button").addEventListener("click", async () => {
      const said = box.querySelector("[data-said]");
      try {
        const got = await Synapse.post("/api/demo/teacher", {});
        try { sessionStorage.setItem(STORE, got.session); } catch (e) { /* storage blocked: this load only */ }
        window.__synapseKey = got.session;
        location.hash = "";
        location.reload();
      } catch (e) { said.textContent = e.message; }
    });
  }

  function logo(parent) {              // the Synapse logo in the dark band's "S" slot (files from build/synapse-logo)
    const img = h("img", null, parent, "rv-logo");
    img.src = "/static/brand/synapse-icon-192.png"; img.alt = "Synapse"; img.width = 48; img.height = 48;
  }

  function chip(text, parent, cls) { return h("span", text, parent, "chip" + (cls ? " " + cls : "")); }

  function bar(level, parent) {         // a three-step bar: new, developing, secure. Not buttons
    const wrap = h("span", null, parent, "steps");
    wrap.setAttribute("role", "img");
    wrap.setAttribute("aria-label", "Level: " + level + " (new, developing, secure)");
    const reached = LEVELS.indexOf(level);
    LEVELS.forEach((lv, i) => { const s = h("span", null, wrap, "step" + (i <= reached ? " on lv-" + level : "")); s.title = lv; });
    return wrap;
  }

  function paintClass() {
    classBox.textContent = "";
    const head = h("header", null, classBox, "rv-head");
    logo(head);
    const titles = h("div", null, head);
    h("p", "Class view", titles, "eyebrow");
    h("h2", data.class.name, titles, "rv-title");
    const facts = [plural(data.class.size, "student")];
    if (data.test) facts.push("Next: " + data.test.name.toLowerCase() + ", " + day(data.test.date) + ", " + plural(data.test.topics.length, "topic"));
    h("p", facts.join(" · "), titles, "muted");
    const buttons = h("div", null, head, "rv-actions");
    [["Mark topic as taught", "coverage"], ["Set a test", "assessment"]].forEach(([label, form]) => {
      const b = h("button", label, buttons, "quiet"); b.type = "button";
      b.addEventListener("click", () => {
        document.body.classList.add("show-forms");
        const f = document.querySelector('[data-form="' + form + '"]');
        if (f) f.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    const tools = h("div", null, classBox, "rv-tools");
    const chips = h("div", null, tools, "chips"); chips.setAttribute("role", "group"); chips.setAttribute("aria-label", "Filter by topic");
    [{ id: null, name: "All topics" }].concat(data.topics).forEach((t) => {
      const b = h("button", t.name, chips, "chip-btn"); b.type = "button";
      b.setAttribute("aria-pressed", String(filter === t.id));
      b.addEventListener("click", () => { filter = t.id; paintClass(); });
    });
    const label = h("label", null, tools, "search");
    h("span", "Search students", label, "visually-hidden");
    const input = h("input", null, label); input.type = "search"; input.placeholder = "Search students"; input.value = search;
    input.addEventListener("input", () => { search = input.value; paintCards(cards); });

    const grid = h("div", null, classBox, "rv-grid");
    const cards = h("section", null, grid, "rv-cards"); cards.setAttribute("aria-label", "Students");
    paintCards(cards);
    const side = h("div", null, grid, "rv-side");

    if (data.test) {
      const sec = h("section", null, side, "panel");
      h("h3", "Before " + dayName(data.test.date) + "'s test", sec);
      h("p", "The test's topics that most need review.", sec, "muted");
      const ul = h("ul", null, sec, "plain-list");
      data.before_test.filter((b) => !filter || b.topic_id === filter).forEach((b) => {
        const li = h("li", null, ul); h("strong", b.name, li);
        h("span", b.enough ? b.label : "Not enough answers yet", li, "band" + (b.enough ? " lv-" + b.level : ""));
        if (b.common) { const w = h("p", null, li, "sub"); w.appendChild(document.createTextNode("Most common wrong idea: ")); h("mark", b.common.wrong_idea, w); }
      });
      if (!ul.childElementCount) h("li", "Nothing to show for this topic.", ul, "muted");
    }

    const bands = h("section", null, side, "panel");
    h("h3", "Topic bands", bands);
    h("p", "Shown once " + data.min_cell + " students have answered on a topic.", bands, "muted");
    const bl = h("ul", null, bands, "plain-list");
    data.bands.filter((b) => !filter || b.topic_id === filter).forEach((b) => {
      const li = h("li", null, bl); h("strong", b.name, li);
      h("span", b.enough ? b.label : "Not enough answers yet", li, "band" + (b.enough ? " lv-" + b.level : ""));
    });

    const wrong = h("section", null, side, "panel");
    h("h3", "Common wrong ideas", wrong);
    h("p", "Held by more than one student now.", wrong, "muted");
    const wl = h("ul", null, wrong, "plain-list");
    data.wrong_ideas.filter((w) => !filter || w.topic_id === filter).forEach((w) => {
      const li = h("li", null, wl);
      h("mark", w.wrong_idea, li);
      h("p", plural(w.students, "student") + " · " + w.part, li, "sub");
      h("p", "Try next: " + w.try_next, li, "sub");
    });
    if (!wl.childElementCount) h("li", "No wrong idea is held by more than one student right now.", wl, "muted");

    const foot = h("footer", null, classBox, "rv-foot");
    h("p", "Per-student view turned on by the school after its DPIA. Students and parents told. Teachers never see chats.", foot);
    if (data.synthetic) h("p", "This class is synthetic, made up for the demo: these are not real students.", foot, "muted");
  }

  function paintCards(box) {
    box.textContent = "";
    const q = search.trim().toLowerCase();
    const shown = data.students.filter((s) => (!filter || s.topics.includes(filter)) && (!q || s.name.toLowerCase().includes(q)));
    shown.forEach((s) => {
      const card = h("article", null, box, "card");
      const top = h("div", null, card, "card-head");
      h("h3", s.name, top);
      const weak = s.weak.filter((w) => !filter || w.topic_id === filter);
      if (!weak.length) h("p", "Not weak at anything right now", card, "muted");
      else {
        h("p", "Weak at", card, "eyebrow");
        const ul = h("ul", null, card, "weak");
        weak.slice(0, 3).forEach((w) => h("li", w.name, ul));
        if (weak.length > 3) h("li", "+" + (weak.length - 3) + " more", ul, "muted");
      }
      const open = h("a", "Open review", card, "open"); open.href = "#student=" + encodeURIComponent(s.id);
      card.addEventListener("click", (ev) => { if (ev.target !== open) location.hash = "student=" + encodeURIComponent(s.id); });
    });
    if (!shown.length) h("p", "No students match.", box, "muted");
  }

  async function paintStudent(id) {
    studentBox.textContent = "";
    let s;
    try { s = await Synapse.get("/api/teacher/class/" + encodeURIComponent(classId) + "/student/" + encodeURIComponent(id)); }
    catch (e) { h("p", "That review could not be loaded: " + e.message, studentBox, "nothing"); return; }
    const back = h("a", "← Back to " + data.class.name, studentBox, "back"); back.href = "#";
    const head = h("header", null, studentBox, "rv-head");
    logo(head);
    const titles = h("div", null, head);
    h("p", "Student review", titles, "eyebrow");
    h("h2", s.student.name, titles, "rv-title");
    h("p", "Based on " + plural(s.record.answers, "answer") + " over " + plural(s.record.over_days, "day") + ", on the topics below.", titles, "muted");

    const grid = h("div", null, studentBox, "rv-grid");
    const main = h("section", null, grid, "panel");
    const first = s.student.name.split(" ")[0];
    h("h3", "What " + first + " is unsure about", main);
    const ul = h("ul", null, main, "plain-list rows");
    s.unsure.forEach((r) => {
      const li = h("li", null, ul);
      const top = h("div", null, li, "row-head");
      h("strong", r.topic + ": " + r.part, top);
      if (r.in_test) chip("in the test", top, "tag");
      if (r.wrong_idea) { h("mark", r.wrong_idea, li); h("p", r.correction, li, "sub"); }
      h("p", "Try next: " + r.try_next, li, "sub");
      h("p", "Answered " + plural(r.answers, "time") + " over " + plural(r.over_days, "day"), li, "sub muted");
    });
    if (!s.unsure.length) h("li", "Nothing answered is unsure right now.", ul, "muted");
    s.not_checked.forEach((r) => {
      const li = h("li", null, ul, "unchecked");
      const top = h("div", null, li, "row-head");
      h("strong", r.topic + ": " + r.part, top);
      if (r.in_test) chip("in the test", top, "tag");
      h("p", "Not yet checked: taught in class, not answered yet", li, "sub muted");
    });

    const ai = h("section", null, grid, "panel");
    const ah = h("div", null, ai, "row-head");
    h("h3", "AI literacy practice", ah);
    chip("Practice feedback, not a grade", ah, "badge");
    h("p", "Levels come from how " + first + " asks and checks while studying. Synapse keeps no message text, and teachers never see chats.", ai, "muted");
    const al = h("ul", null, ai, "plain-list rows");
    s.ai_literacy.skills.forEach((k) => {
      const li = h("li", null, al);
      const top = h("div", null, li, "row-head"); h("strong", k.name, top); bar(k.level, top);
      const word = k.level.charAt(0).toUpperCase() + k.level.slice(1);
      h("p", k.checks ? word + ", from " + plural(k.checks, "question") + " over " + plural(k.over_days, "day") : "No evidence yet", li, "sub");
      if (k.tip) h("p", "Tip: " + k.tip, li, "sub muted");
    });
    if (s.synthetic) h("p", "This student is synthetic, made up for the demo.", studentBox, "muted rv-foot");
  }

  function route() {
    const m = /^#student=([^&]+)/.exec(location.hash);
    classBox.hidden = !!m; studentBox.hidden = !m;
    if (m) paintStudent(decodeURIComponent(m[1])); else paintClass();
    window.scrollTo(0, 0);
  }

  document.addEventListener("synapse:signed-in", async (ev) => {
    const classes = ev.detail.classes || [];
    for (const c of classes) {
      try { data = await Synapse.get("/api/teacher/class/" + encodeURIComponent(c.id) + "/review"); classId = c.id; break; }
      catch (e) { /* the per-student view is off for this class: the class page stays as it was */ }
    }
    if (!data) return;
    document.body.classList.add("review-on");
    root.hidden = false;
    window.addEventListener("hashchange", route);
    route();
  });
  offerDemo();
})();
