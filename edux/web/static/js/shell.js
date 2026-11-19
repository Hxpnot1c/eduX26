// Shared by every page: the level key, and the sign-in line (who the key says you are).
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";

  function disc(kind) {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 20 20");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("class", "disc " + kind);
    const el = (name, attrs) => {
      const node = document.createElementNS(NS, name);
      for (const k in attrs) node.setAttribute(k, attrs[k]);
      svg.appendChild(node);
    };
    if (kind === "none") { el("circle", { class: "dot", cx: 10, cy: 10, r: 2.2 }); return svg; }
    if (kind === "developing") el("path", { class: "half", d: "M10 2.5 A7.5 7.5 0 0 0 10 17.5 Z" });
    el("circle", { class: "ring", cx: 10, cy: 10, r: 7.5 });
    if (kind === "review") el("circle", { class: "mark", cx: 10, cy: 10, r: 2.6 }); // new's colours, marked: learnt once, now fading
    if (kind === "developing") el("path", { class: "half", d: "M10 2.5 A7.5 7.5 0 0 0 10 17.5 Z" });
    return svg;
  }

  const LEVELS = [
    ["new", "new"],
    ["review", "needs review"],
    ["developing", "developing"],
    ["secure", "secure"],
    ["taught", "taught in class, not yet checked"],
    ["none", "no answers yet"],
  ];

  function buildKey() {
    document.querySelectorAll("[data-level-key]").forEach(function (list) {
      list.classList.add("key");
      LEVELS.forEach(function (pair) {
        const li = document.createElement("li");
        li.appendChild(disc(pair[0]));
        li.appendChild(document.createTextNode(pair[1]));
        list.appendChild(li);
      });
    });
  }

  async function signIn() {
    const line = document.querySelector("[data-signin]");
    if (!line) return;
    const wants = line.getAttribute("data-signin"); // "student", "teacher" or "any"
    const state = line.querySelector(".status");
    const form = line.querySelector("form");
    const forget = line.querySelector("[data-forget]");
    const show = (text, strong) => {       // plain text, with one bold word if given: never HTML
      state.textContent = "";
      if (!strong) { state.textContent = text; return; }
      const [before, after] = text.split("{}");
      state.appendChild(document.createTextNode(before));
      const b = document.createElement("strong"); b.textContent = strong; state.appendChild(b);
      state.appendChild(document.createTextNode(after));
    };
    if (!Synapse.key()) {
      show(line.getAttribute("data-nokey") || "Open the link you were given. It ends in {} and signs you in on this tab only.", "#key=…");
      if (forget) forget.hidden = true;
      return;
    }
    try {
      const who = await Synapse.get("/api/whoami");
      if (wants !== "any" && who.role !== wants) {
        show("This key is for a " + who.role + ", and this page is for a " + wants + ".");
      } else {
        show("Signed in as a {} on this tab only.", who.role);
        document.dispatchEvent(new CustomEvent("synapse:signed-in", { detail: who }));
      }
      if (forget) forget.hidden = false;
    } catch (e) {
      show("That key was not recognised. Check the link you were given.");
      if (forget) forget.hidden = false;
    }
    if (forget) forget.addEventListener("click", function () { Synapse.forget(); location.reload(); });
  }

  window.SynapseUI = { disc: disc, words: Object.fromEntries(LEVELS) };
  buildKey();
  signIn();
})();
