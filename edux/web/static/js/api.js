// Sign-in for the pages, and the one place that talks to the API.
// The key arrives in the URL fragment (#key=...), which the browser never sends to a server. It is moved into
// sessionStorage (gone when the tab closes), the fragment is removed from the address bar, and every API call sends it as
// a bearer header. Nothing is stored for longer, and "Forget this device" clears it at once.
(function () {
  "use strict";
  const STORE = "synapse-key";

  function readFragment() {
    const m = /(?:^#|&)key=([^&]+)/.exec(location.hash);
    if (!m) return;
    try { sessionStorage.setItem(STORE, decodeURIComponent(m[1])); } catch (e) { /* storage blocked: the page then works for this load only */ }
    history.replaceState(null, "", location.pathname + location.search);
    window.__synapseKey = decodeURIComponent(m[1]);
  }

  function key() {
    if (window.__synapseKey) return window.__synapseKey;
    try { return sessionStorage.getItem(STORE) || ""; } catch (e) { return ""; }
  }

  async function get(path) {
    const k = key();
    const res = await fetch(path, { headers: k ? { Authorization: "Bearer " + k } : {}, cache: "no-store" });
    if (!res.ok) {
      let message = res.statusText;
      try { message = (await res.json()).error || message; } catch (e) { /* not JSON */ }
      const err = new Error(message);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  async function post(path, body) {
    const k = key();
    const headers = { "Content-Type": "application/json" };
    if (k) headers.Authorization = "Bearer " + k;
    const res = await fetch(path, { method: "POST", headers: headers, body: JSON.stringify(body), cache: "no-store" });
    let data = {};
    try { data = await res.json(); } catch (e) { /* not JSON */ }
    if (!res.ok) { const err = new Error(data.error || res.statusText); err.status = res.status; throw err; }
    return data;
  }

  function forget() {
    window.__synapseKey = "";
    try { sessionStorage.removeItem(STORE); } catch (e) { /* nothing to clear */ }
  }

  readFragment();
  window.Synapse = { key, get, post, forget };
})();
