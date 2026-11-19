// The course map page: your course if you are signed in, otherwise the public example course (if the server allows it).
(async function () {
  "use strict";
  const host = document.getElementById("map"), status = document.getElementById("map-status");
  async function load() {
    if (Synapse.key()) {
      try { return [await Synapse.get("/api/map"), "your course"]; }
      catch (e) { if (e.status !== 401 && e.status !== 404) throw e; }
    }
    return [await Synapse.get("/api/public/map"), "the public example course"];
  }
  try {
    const [data, which] = await load();
    status.textContent = "Showing " + which + ": " + data.course.name + ". Structure only; no student information.";
    const q = new URLSearchParams(location.search);       // ?view=path|list and ?select=<id>: a link to a particular view
    const view = ["map", "path", "list"].includes(q.get("view")) ? q.get("view") : "map";
    const graph = SynapseGraph.mount(host, data, { view: view });
    if (q.get("select")) graph.select(q.get("select"));
  } catch (e) {
    status.textContent = "There is no map you can see yet. Open the link you were given to sign in.";
  }
})();
