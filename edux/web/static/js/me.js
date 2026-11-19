// The student's page: their own record, from /api/me, with the concept network coloured by their levels (decision 0029).
(function () {
  "use strict";
  function h(name, text, parent, cls) {
    const node = document.createElement(name);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }
  const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);
  const day = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
  const rows = {};
  document.querySelectorAll("[data-fill]").forEach((el) => { rows[el.getAttribute("data-fill")] = el; });

  function itemList(into, items, build, empty) {
    into.textContent = "";
    if (!items.length) { h("p", empty, into, "nothing"); return; }
    const ul = h("ul", null, into, "items");
    items.forEach((it) => build(h("li", null, ul), it));
  }

  function copy(button, source) {       // source is a string, or a function that returns the text to copy at the moment of the click
    button.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(typeof source === "function" ? source() : source); button.textContent = "Copied"; }
      catch (e) { button.textContent = "Select the text above and copy it"; }
      setTimeout(() => { button.textContent = "Copy"; }, 2500);
    });
  }

  function paint(data) {
    document.getElementById("me").hidden = false;
    if (data.network) {
      const net = SynapseNetwork.mount(rows.map, data.network);  // the concept network (decision 0029)
      const q = new URLSearchParams(location.search);
      if (q.get("select")) net.select(q.get("select"));
    } else {
      h("p", "Your course map could not be found.", rows.map, "nothing");
    }

    rows.next.textContent = "";
    h("p", "Where a little practice moves you most, in order.", rows.next, "muted");
    const nextHost = h("div", null, rows.next);
    itemList(nextHost, data.next, (li, f) => {
      li.appendChild(SynapseUI.disc(f.level));
      const head = h("div", null, li, "head");
      h("strong", f.name, head); h("span", SynapseUI.words[f.level] || f.level, head, "muted");
    }, "Nothing stands out yet: answer a few questions and this fills in.");

    itemList(rows.reviews, data.reviews, (li, r) => {
      li.appendChild(SynapseUI.disc(r.level));
      const head = h("div", null, li, "head");
      h("strong", r.name, head); h("span", r.when, head, "muted");
      h("span", r.why, li, "sub");
    }, "Nothing is due for a check.");

    const coming = rows.coming; coming.textContent = "";
    if (!data.coming_up.assessments.length) h("p", "No tests or assignments are set. Tell your chatbot about one and it will appear here.", coming, "nothing");
    data.coming_up.assessments.forEach((a) => {
      const p = h("p", null, coming);
      h("strong", a.name, p); p.appendChild(document.createTextNode(" · " + a.kind.replace("_", " ") + " · " + day(a.date) + " · " + (a.days_left === 1 ? "tomorrow" : "in " + a.days_left + " days")));
    });
    const plan = data.coming_up.plan;
    if (plan) {
      h("h3", "A suggested plan for " + plan.assessment.name, coming);
      const ul = h("ul", null, coming, "plain-list");
      plan.sessions.forEach((s) => h("li", day(s.date) + " · " + s.kind + ": " + s.parts.map((p) => p.name).join(", "), ul));
      if (plan.note) h("p", plan.note, coming, "muted");
    }

    const lit = rows.literacy; lit.textContent = "";
    h("p", cap(data.ai_literacy.note) + ". It shows how much you have practised, not how good you are.", lit);
    const dl = h("dl", null, lit, "skills");
    data.ai_literacy.skills.forEach((s) => {
      h("dt", s.name + ": " + s.level, dl);
      h("dd", s.checks ? "from " + s.checks + " check" + (s.checks === 1 ? "" : "s") + " over " + s.over_days + " day" + (s.over_days === 1 ? "" : "s") : "no checks yet", dl);
    });

    if (data.calibration) { rows.sure.closest(".row").hidden = false; rows.sure.textContent = data.calibration.line; }

    const rec = rows.record; rec.textContent = "";
    const facts = h("ul", null, rec, "facts");
    [[data.record.answers, "answers recorded"], [data.record.chats, "chats noted"], [data.record.first ? new Date(data.record.first + "T12:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "none yet", "first answer"]].forEach(([n, label]) => {
      const li = h("li", null, facts); h("strong", String(n), li); h("span", label, li);
    });
    const keeps = h("ul", null, rec, "plain-list");
    data.setup.keeps.forEach((k) => h("li", k, keeps));
    h("h3", "Not sure a level is right?", rec);
    h("p", "Ask your chatbot to check you. Pick the part and copy the message.", rec);
    const pick = h("select", null, rec); pick.setAttribute("aria-label", "Part to be checked on");
    data.parts.forEach((p) => { const o = h("option", p.name, pick); o.value = p.name; });
    const msg = h("pre", null, rec, "copy"), btn = h("button", "Copy", rec, "quiet"); btn.type = "button";
    const text = () => "I'm not sure my level on \"" + pick.value + "\" is right. Please check my understanding of it with a short question.";
    msg.textContent = text(); pick.addEventListener("change", () => { msg.textContent = text(); });
    copy(btn, text);

    const set = rows.setup; set.textContent = "";
    h("p", "Add Synapse as a connector with the link you were given, then paste this into your chatbot's custom instructions.", set);
    h("pre", data.setup.prompt, set, "copy"); const cbtn = h("button", "Copy", set, "quiet"); cbtn.type = "button";
    copy(cbtn, data.setup.prompt);
  }

  document.addEventListener("synapse:signed-in", async () => {
    try {
      paint(await Synapse.get("/api/me"));
    } catch (e) {
      const s = document.querySelector("[data-signin] .status");
      if (s) s.textContent = "Your page could not be loaded: " + e.message;
    }
  });
})();
