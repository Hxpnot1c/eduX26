// The teacher's page: classes, never one student. Everything comes from /api/teacher/class/<id>, which withholds any
// cell under five students; this page only draws what it is given.
(function () {
  "use strict";
  function h(name, text, parent, cls) {
    const node = document.createElement(name);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }
  const day = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
  const rows = {};
  document.querySelectorAll("[data-fill]").forEach((el) => { rows[el.getAttribute("data-fill")] = el; });
  let mapData = null, graph = null, currentClass = null;

  function legend(into) {
    into.textContent = "";
    into.classList.add("key");
    [["new", "few at developing yet"], ["developing", "about half at developing or secure"], ["secure", "most at developing or secure"], ["none", "fewer than 5 students have answered: nothing shown"]].forEach(([kind, text]) => {
      const li = h("li", null, into); li.appendChild(SynapseUI.disc(kind)); li.appendChild(document.createTextNode(text));
    });
  }

  function list(into, items, build, empty) {
    into.textContent = "";
    if (!items.length) { h("p", empty, into, "nothing"); return; }
    const ul = h("ul", null, into, "items");
    items.forEach((it) => build(h("li", null, ul), it));
  }

  function paint(data) {
    document.getElementById("class-body").hidden = false;
    rows.seeded.hidden = !data.seeded;
    rows.size.textContent = data.class.size + " students in " + data.class.name + ". Anything resting on fewer than " + data.min_cell + " students is not shown.";

    rows.map.textContent = "";
    if (!data.enough) {
      h("p", "This class has fewer than " + data.min_cell + " students, so no map is shown. Showing so few students could point at one of them.", rows.map, "nothing");
    } else {
      graph = SynapseGraph.mount(rows.map, mapData, { overlay: data.overlay });
    }

    const cov = rows.coverage; cov.textContent = "";
    if (!data.coverage.taught.length) h("p", "No coverage has been set for this class. Use the command line: coverage set.", cov, "nothing");
    list(h("div", null, cov), data.coverage.taught, (li, c) => {
      li.appendChild(SynapseUI.disc("taught"));
      const head = h("div", null, li, "head"); h("strong", c.name, head); h("span", (c.spec_ref ? c.spec_ref + " · " : "") + "taught " + day(c.taught_on), head, "muted");
    }, "");
    if (data.coverage.not_yet.length) {
      h("h3", "Not yet covered", cov);
      h("p", data.coverage.not_yet.map((c) => c.name + (c.spec_ref ? " (" + c.spec_ref + ")" : "")).join("; "), cov, "muted");
    }

    list(rows.wrong, data.wrong_ideas, (li, w) => {
      li.appendChild(document.createElement("span"));
      const head = h("div", null, li, "head"); h("strong", w.wrong_idea, head);
      h("span", w.students + " students · " + w.part, li, "sub");
      h("span", "The right idea: " + w.correction, li, "sub");
    }, data.enough ? "No wrong idea is held by " + data.min_cell + " or more students at the moment." : "Not shown for so small a class.");

    list(rows.coming, data.assessments, (li, a) => {
      li.appendChild(document.createElement("span"));
      const head = h("div", null, li, "head"); h("strong", a.name, head); h("span", a.kind.replace("_", " ") + " · " + day(a.date), head, "muted");
      const remove = h("button", "Remove", li, "quiet"); remove.type = "button"; remove.setAttribute("aria-label", "Remove " + a.name);
      remove.addEventListener("click", () => act("assessments/remove", { id: a.id }, null));
    }, "No tests or assignments are set for this class.");

    list(rows.changes, data.recent_changes, (li, c) => {
      li.appendChild(document.createElement("span"));
      const head = h("div", null, li, "head"); h("strong", c.who + " " + c.action, head); h("span", day(c.when), head, "muted");
      h("span", c.detail, li, "sub");
    }, "No changes have been made here yet.");

    const help = rows.help; help.textContent = "";
    if (!data.help_seeking) h("p", "Not enough students have written in to show this without pointing at individuals.", help, "nothing");
    else {
      const r = Math.round(data.help_seeking.recent * 100), b = Math.round(data.help_seeking.before * 100);
      h("p", "Over the last " + data.help_seeking.days + " days, " + r + "% of the class's messages asked to be shown the answer, against " + b + "% before that" + (data.help_seeking.direction ? " (" + data.help_seeking.direction + ")." : "."), help);
      h("p", "A rise can mean a hard topic as much as a habit. It is a prompt to look at the teaching, not a finding about students.", help, "muted");
    }
  }

  function concepts() {           // the course's concepts, grouped under their topics, for the checkboxes
    const topics = new Map(mapData.nodes.filter((n) => n.level === "topic").map((n) => [n.id, n.name]));
    return mapData.nodes.filter((n) => n.level === "concept").map((n) => ({ id: n.id, label: n.name + (n.spec_ref ? " (" + n.spec_ref + ")" : ""), topic: topics.get(n.parent) }));
  }

  function checkboxes() {
    document.querySelectorAll("[data-checks]").forEach((box) => {
      if (box.childElementCount) return;
      concepts().forEach((c) => {
        const label = h("label", null, box), input = h("input", null, label);
        input.type = "checkbox"; input.value = c.id; label.appendChild(document.createTextNode(c.label));
      });
    });
  }

  async function act(path, body, form) {
    const said = form ? form.querySelector("[data-said]") : null;
    if (said) { said.className = "said"; said.textContent = "Saving…"; }
    try {
      paint(await Synapse.post("/api/teacher/class/" + encodeURIComponent(currentClass) + "/" + path, body));
      const fresh = form ? document.querySelector('[data-form="' + form.getAttribute("data-form") + '"] [data-said]') : null;
      if (fresh) { fresh.className = "said"; fresh.textContent = "Done."; }
      if (form) { form.reset(); form.querySelectorAll("input[type=checkbox]").forEach((b) => { b.checked = false; }); }
    } catch (e) {
      const where = said || document.querySelector("[data-signin] .status");
      if (where) { where.className = "said bad"; where.textContent = e.message; }
    }
  }

  function wireForms() {
    document.querySelectorAll("form[data-form]").forEach((form) => {
      if (form.dataset.wired) return;
      form.dataset.wired = "1";
      form.addEventListener("submit", (ev) => {
        ev.preventDefault();
        const picked = Array.from(form.querySelectorAll("input[type=checkbox]:checked")).map((b) => b.value);
        if (form.getAttribute("data-form") === "coverage") act("coverage", { sections: picked, taught_on: form.elements.taught_on.value || undefined }, form);
        else act("assessments", { name: form.elements.name.value, kind: form.elements.kind.value, date: form.elements.date.value, topics: picked }, form);
      });
    });
  }

  async function show(id) {
    currentClass = id;
    try { paint(await Synapse.get("/api/teacher/class/" + encodeURIComponent(id))); checkboxes(); wireForms(); }
    catch (e) { const s = document.querySelector("[data-signin] .status"); if (s) s.textContent = "That class could not be loaded: " + e.message; }
  }

  document.addEventListener("synapse:signed-in", async (ev) => {
    const classes = ev.detail.classes || [];
    legend(document.getElementById("class-key"));
    if (!classes.length) { rows.pick.textContent = "No classes are assigned to you yet. Ask whoever runs Synapse for your school."; return; }
    try { mapData = await Synapse.get("/api/map"); } catch (e) { mapData = null; }
    if (!mapData) { rows.pick.textContent = "The course map could not be loaded."; return; }
    rows.pick.textContent = "";
    const select = h("select", null, rows.pick); select.setAttribute("aria-label", "Class");
    classes.forEach((c) => { const o = h("option", c.name, select); o.value = c.id; });
    select.addEventListener("change", () => show(select.value));
    show(select.value);
  });
})();
