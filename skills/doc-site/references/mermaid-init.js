/**
 * Mermaid initializer for MkDocs Material + pymdownx.superfences.
 *
 * pymdownx.superfences renders mermaid blocks as:
 *   <pre class="mermaid"><code>...diagram source...</code></pre>
 *
 * Mermaid.js expects the source directly inside the container (no <code> wrapper).
 * This script unwraps <code> tags, then calls mermaid.run() to render SVGs.
 *
 * Loaded as type="module" so it can import mermaid ESM.
 */
import mermaid from "https://unpkg.com/mermaid@10.9.1/dist/mermaid.esm.min.mjs";

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "loose",
});

function renderDiagrams() {
  var els = document.querySelectorAll("pre.mermaid");
  if (!els.length) return;

  els.forEach(function (pre) {
    var code = pre.querySelector("code");
    if (code) {
      pre.textContent = code.textContent;
    }
  });

  mermaid.run({ nodes: els });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderDiagrams);
} else {
  renderDiagrams();
}

/* MkDocs Material instant navigation support */
if (typeof document$ !== "undefined") {
  document$.subscribe(function () {
    renderDiagrams();
  });
}
