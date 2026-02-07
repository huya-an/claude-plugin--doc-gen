/**
 * Diagram Viewer — pan/zoom + fullscreen modal for Mermaid.js SVG diagrams.
 *
 * Self-contained: injects its own CSS, no external dependencies.
 * Works with MkDocs Material + pymdownx.superfences Mermaid rendering.
 *
 * After Mermaid.js renders SVGs into .mermaid-raw containers, this script:
 *  1. Wraps each diagram in a styled, scrollable container
 *  2. Adds an expand button overlay
 *  3. On click, opens a fullscreen modal with pan/zoom
 *
 * Include via extra_javascript in mkdocs.yml (after mermaid ESM module).
 */
(function () {
  'use strict';

  /* ── Inject component CSS ────────────────────────────────────── */
  var css = document.createElement('style');
  css.textContent = [
    /* Enhanced diagram container */
    '.mermaid-raw.diagram-enhanced {',
    '  position: relative;',
    '  cursor: grab;',
    '  border: 1px solid var(--md-default-fg-color--lightest, #e0e0e0);',
    '  border-radius: 8px;',
    '  padding: 1rem;',
    '  margin: 1.5em 0;',
    '  background: var(--md-default-bg-color, #fff);',
    '  overflow: hidden;',
    '  min-height: 200px;',
    '  transition: box-shadow 0.2s ease;',
    '}',
    '.mermaid-raw.diagram-enhanced.inline-panning { cursor: grabbing; }',
    '.mermaid-raw.diagram-enhanced:hover {',
    '  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);',
    '}',
    '.mermaid-raw.diagram-enhanced svg {',
    '  transform-origin: 0 0;',
    '}',
    /* Inline zoom level badge */
    '.diagram-zoom-badge {',
    '  position: absolute;',
    '  bottom: 8px;',
    '  left: 12px;',
    '  font-size: 0.7rem;',
    '  color: var(--md-default-fg-color--light, #888);',
    '  background: rgba(255, 255, 255, 0.85);',
    '  padding: 2px 8px;',
    '  border-radius: 4px;',
    '  opacity: 0;',
    '  transition: opacity 0.2s;',
    '  pointer-events: none;',
    '  z-index: 5;',
    '}',
    '.mermaid-raw.diagram-enhanced:hover .diagram-zoom-badge { opacity: 1; }',

    /* Expand button */
    '.diagram-expand-btn {',
    '  position: absolute;',
    '  top: 8px;',
    '  right: 8px;',
    '  z-index: 10;',
    '  width: 32px;',
    '  height: 32px;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  background: rgba(255, 255, 255, 0.92);',
    '  border: 1px solid #ccc;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  opacity: 0;',
    '  transition: opacity 0.2s;',
    '  color: #555;',
    '  padding: 0;',
    '  line-height: 1;',
    '}',
    '.mermaid-raw.diagram-enhanced:hover .diagram-expand-btn { opacity: 1; }',
    '.diagram-expand-btn:hover { background: #f5f5f5; color: #222; }',

    /* "Click to expand" hint */
    '.mermaid-raw.diagram-enhanced::after {',
    '  content: "Click to expand";',
    '  position: absolute;',
    '  bottom: 8px;',
    '  right: 12px;',
    '  font-size: 0.7rem;',
    '  color: var(--md-default-fg-color--light, #888);',
    '  background: rgba(255, 255, 255, 0.85);',
    '  padding: 2px 8px;',
    '  border-radius: 4px;',
    '  opacity: 0;',
    '  transition: opacity 0.2s;',
    '  pointer-events: none;',
    '}',
    '.mermaid-raw.diagram-enhanced:hover::after { opacity: 1; }',

    /* ── Fullscreen modal ── */
    '.diagram-modal {',
    '  position: fixed;',
    '  inset: 0;',
    '  z-index: 10000;',
    '  background: #ffffff;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  opacity: 0;',
    '  transition: opacity 0.2s ease;',
    '}',
    '.diagram-modal.active { opacity: 1; }',

    '.diagram-modal-content {',
    '  width: 100%;',
    '  height: 100%;',
    '  overflow: hidden;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  cursor: grab;',
    '}',
    '.diagram-modal-content.panning { cursor: grabbing; }',
    '.diagram-modal-content svg {',
    '  max-width: none !important;',
    '  max-height: none !important;',
    '  width: auto !important;',
    '  height: auto !important;',
    '  transform-origin: 0 0;',
    '}',

    /* Controls toolbar */
    '.diagram-modal-controls {',
    '  position: fixed;',
    '  top: 16px;',
    '  right: 16px;',
    '  z-index: 10001;',
    '  display: flex;',
    '  gap: 6px;',
    '  align-items: center;',
    '}',
    '.diagram-modal-btn {',
    '  height: 36px;',
    '  min-width: 36px;',
    '  display: inline-flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  background: #f0f0f0;',
    '  border: 1px solid #ccc;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  font-size: 18px;',
    '  color: #333;',
    '  font-weight: 600;',
    '  transition: background 0.15s;',
    '  padding: 0 8px;',
    '  user-select: none;',
    '}',
    '.diagram-modal-btn:hover { background: #e0e0e0; }',
    '.diagram-modal-btn[data-action="reset"] {',
    '  font-size: 13px;',
    '  font-weight: 500;',
    '  padding: 0 14px;',
    '}',
    '.diagram-modal-btn[data-action="close"] {',
    '  margin-left: 8px;',
    '  font-size: 22px;',
    '}',

    /* Zoom level indicator */
    '.diagram-modal-zoom-level {',
    '  color: #666;',
    '  font-size: 13px;',
    '  font-weight: 500;',
    '  margin-right: 4px;',
    '  min-width: 48px;',
    '  text-align: center;',
    '}',

    /* Keyboard hint */
    '.diagram-modal-hint {',
    '  position: fixed;',
    '  bottom: 16px;',
    '  left: 50%;',
    '  transform: translateX(-50%);',
    '  color: #999;',
    '  font-size: 12px;',
    '  z-index: 10001;',
    '  pointer-events: none;',
    '}'
  ].join('\n');
  document.head.appendChild(css);

  /* ── SVG expand icon ─────────────────────────────────────────── */
  var EXPAND_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" ' +
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M8 3H5a2 2 0 0 0-2 2v3"/>' +
    '<path d="M21 8V5a2 2 0 0 0-2-2h-3"/>' +
    '<path d="M3 16v3a2 2 0 0 0 2 2h3"/>' +
    '<path d="M16 21h3a2 2 0 0 0 2-2v-3"/>' +
    '</svg>';

  /* ── Init: wait for Mermaid SVGs, then enhance ───────────────── */
  function init() {
    var attempts = 0;
    var maxAttempts = 50; /* 10 s at 200 ms */

    function check() {
      /* Re-query every poll — mermaid.run() may replace DOM nodes */
      var containers = document.querySelectorAll('.mermaid-raw');
      if (!containers.length) {
        if (++attempts < maxAttempts) setTimeout(check, 200);
        return;
      }

      var ready = true;
      containers.forEach(function (el) {
        if (!el.querySelector('svg')) ready = false;
      });
      if (ready) {
        enhance(containers);
      } else if (++attempts < maxAttempts) {
        setTimeout(check, 200);
      }
    }

    check();
  }

  function enhance(containers) {
    containers.forEach(function (el) {
      if (el.dataset.diagramEnhanced) return;
      el.dataset.diagramEnhanced = 'true';
      el.classList.add('diagram-enhanced');

      var svg = el.querySelector('svg');
      if (!svg) return;

      /* Expand button */
      var btn = document.createElement('button');
      btn.className = 'diagram-expand-btn';
      btn.setAttribute('aria-label', 'View diagram fullscreen');
      btn.title = 'Expand diagram';
      btn.innerHTML = EXPAND_ICON;
      el.appendChild(btn);

      /* Zoom badge */
      var badge = document.createElement('span');
      badge.className = 'diagram-zoom-badge';
      badge.textContent = '100%';
      el.appendChild(badge);

      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        openModal(svg);
      });

      /* ── Inline pan/zoom state ── */
      var iScale = 1;
      var iPanX = 0;
      var iPanY = 0;
      var iPanning = false;
      var iStartX = 0;
      var iStartY = 0;
      var iMoved = false;

      function iApply() {
        svg.style.transform =
          'translate(' + iPanX + 'px, ' + iPanY + 'px) scale(' + iScale + ')';
        badge.textContent = Math.round(iScale * 100) + '%';
      }

      /* Mouse wheel zoom */
      el.addEventListener(
        'wheel',
        function (e) {
          e.preventDefault();
          var factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
          var newScale = Math.max(0.2, Math.min(10, iScale * factor));
          var rect = el.getBoundingClientRect();
          var mx = e.clientX - rect.left;
          var my = e.clientY - rect.top;
          iPanX = mx - (newScale / iScale) * (mx - iPanX);
          iPanY = my - (newScale / iScale) * (my - iPanY);
          iScale = newScale;
          iApply();
        },
        { passive: false }
      );

      /* Mouse drag pan */
      el.addEventListener('mousedown', function (e) {
        if (e.target.closest('.diagram-expand-btn')) return;
        if (e.button !== 0) return;
        iPanning = true;
        iMoved = false;
        iStartX = e.clientX - iPanX;
        iStartY = e.clientY - iPanY;
        el.classList.add('inline-panning');
        e.preventDefault();
      });

      document.addEventListener('mousemove', function (e) {
        if (!iPanning) return;
        iPanX = e.clientX - iStartX;
        iPanY = e.clientY - iStartY;
        iMoved = true;
        iApply();
      });

      document.addEventListener('mouseup', function () {
        if (iPanning) {
          iPanning = false;
          el.classList.remove('inline-panning');
        }
      });

      /* Click to open modal — only if user didn't drag */
      el.addEventListener('click', function (e) {
        if (e.target.closest('.diagram-expand-btn')) return;
        if (iMoved) { iMoved = false; return; }
        var sel = window.getSelection();
        if (sel && sel.toString().length > 0) return;
        openModal(svg);
      });

      /* Double-click to reset inline zoom */
      el.addEventListener('dblclick', function (e) {
        if (e.target.closest('.diagram-expand-btn')) return;
        e.preventDefault();
        iScale = 1;
        iPanX = 0;
        iPanY = 0;
        iApply();
      });
    });
  }

  /* ── Fullscreen modal ────────────────────────────────────────── */
  function openModal(originalSvg) {
    if (!originalSvg) return;

    /* Build DOM */
    var modal = document.createElement('div');
    modal.className = 'diagram-modal';

    var content = document.createElement('div');
    content.className = 'diagram-modal-content';

    var svg = originalSvg.cloneNode(true);
    svg.removeAttribute('id');
    svg.style.cssText = 'transform-origin: 0 0;';

    var zoomLabel = document.createElement('span');
    zoomLabel.className = 'diagram-modal-zoom-level';
    zoomLabel.textContent = '100%';

    var controls = document.createElement('div');
    controls.className = 'diagram-modal-controls';
    controls.innerHTML =
      '<button class="diagram-modal-btn" data-action="in" title="Zoom in">+</button>' +
      '<button class="diagram-modal-btn" data-action="out" title="Zoom out">&minus;</button>' +
      '<button class="diagram-modal-btn" data-action="reset" title="Reset view">Fit</button>';
    controls.appendChild(zoomLabel);

    var closeBtn = document.createElement('button');
    closeBtn.className = 'diagram-modal-btn';
    closeBtn.dataset.action = 'close';
    closeBtn.title = 'Close (Esc)';
    closeBtn.innerHTML = '&times;';
    controls.appendChild(closeBtn);

    var hint = document.createElement('div');
    hint.className = 'diagram-modal-hint';
    hint.textContent = 'Scroll to zoom \u00b7 Drag to pan \u00b7 Esc to close';

    content.appendChild(svg);
    modal.appendChild(controls);
    modal.appendChild(content);
    modal.appendChild(hint);
    document.body.appendChild(modal);

    /* Trigger CSS transition */
    requestAnimationFrame(function () {
      modal.classList.add('active');
    });

    /* Prevent body scroll */
    var prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    /* ── Pan / Zoom state ── */
    var scale = 1;
    var panX = 0;
    var panY = 0;
    var isPanning = false;
    var startX = 0;
    var startY = 0;

    function applyTransform() {
      svg.style.transform =
        'translate(' + panX + 'px, ' + panY + 'px) scale(' + scale + ')';
      zoomLabel.textContent = Math.round(scale * 100) + '%';
    }

    function fitToView() {
      var rect = content.getBoundingClientRect();
      var bb = svg.getBBox ? svg.getBBox() : null;
      var svgW = (bb && bb.width) || parseFloat(svg.getAttribute('width')) || 800;
      var svgH = (bb && bb.height) || parseFloat(svg.getAttribute('height')) || 600;
      var padW = rect.width * 0.9;
      var padH = rect.height * 0.9;
      scale = Math.min(padW / svgW, padH / svgH, 2);
      panX = (rect.width - svgW * scale) / 2;
      panY = (rect.height - svgH * scale) / 2;
      applyTransform();
    }

    fitToView();

    /* ── Zoom helpers ── */
    function zoomBy(factor, point) {
      var newScale = Math.max(0.05, Math.min(20, scale * factor));
      if (point) {
        var rect = content.getBoundingClientRect();
        var mx = point.x - rect.left;
        var my = point.y - rect.top;
        panX = mx - (newScale / scale) * (mx - panX);
        panY = my - (newScale / scale) * (my - panY);
      }
      scale = newScale;
      applyTransform();
    }

    /* ── Control buttons ── */
    controls.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-action]');
      if (!btn) return;
      e.stopPropagation();
      switch (btn.dataset.action) {
        case 'in':    zoomBy(1.3, null); break;
        case 'out':   zoomBy(1 / 1.3, null); break;
        case 'reset': fitToView(); break;
        case 'close': close(); break;
      }
    });

    /* ── Mouse wheel zoom (toward cursor) ── */
    content.addEventListener(
      'wheel',
      function (e) {
        e.preventDefault();
        var factor = e.deltaY < 0 ? 1.12 : 1 / 1.12;
        zoomBy(factor, { x: e.clientX, y: e.clientY });
      },
      { passive: false }
    );

    /* ── Mouse drag pan ── */
    content.addEventListener('mousedown', function (e) {
      if (e.button !== 0) return;
      isPanning = true;
      startX = e.clientX - panX;
      startY = e.clientY - panY;
      content.classList.add('panning');
      e.preventDefault();
    });

    function onMouseMove(e) {
      if (!isPanning) return;
      panX = e.clientX - startX;
      panY = e.clientY - startY;
      applyTransform();
    }

    function onMouseUp() {
      if (isPanning) {
        isPanning = false;
        content.classList.remove('panning');
      }
    }

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    /* ── Touch: single-finger pan + pinch-zoom ── */
    var lastTouchDist = 0;

    content.addEventListener(
      'touchstart',
      function (e) {
        if (e.touches.length === 1) {
          isPanning = true;
          startX = e.touches[0].clientX - panX;
          startY = e.touches[0].clientY - panY;
        } else if (e.touches.length === 2) {
          isPanning = false;
          lastTouchDist = touchDist(e);
        }
      },
      { passive: true }
    );

    content.addEventListener(
      'touchmove',
      function (e) {
        e.preventDefault();
        if (e.touches.length === 1 && isPanning) {
          panX = e.touches[0].clientX - startX;
          panY = e.touches[0].clientY - startY;
          applyTransform();
        } else if (e.touches.length === 2) {
          var d = touchDist(e);
          if (lastTouchDist > 0) zoomBy(d / lastTouchDist, touchMid(e));
          lastTouchDist = d;
        }
      },
      { passive: false }
    );

    content.addEventListener(
      'touchend',
      function () {
        isPanning = false;
        lastTouchDist = 0;
      },
      { passive: true }
    );

    function touchDist(e) {
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      return Math.sqrt(dx * dx + dy * dy);
    }

    function touchMid(e) {
      return {
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2
      };
    }

    /* ── Close ── */
    function close() {
      modal.classList.remove('active');
      document.body.style.overflow = prevOverflow;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.removeEventListener('keydown', onKeyDown);
      setTimeout(function () {
        modal.remove();
      }, 200);
    }

    function onKeyDown(e) {
      if (e.key === 'Escape') close();
    }
    document.addEventListener('keydown', onKeyDown);

    modal.addEventListener('click', function (e) {
      if (e.target === modal) close();
    });
  }

  /* ── Bootstrap ───────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* MkDocs Material instant navigation support */
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function () {
      document
        .querySelectorAll('.mermaid-raw[data-diagram-enhanced]')
        .forEach(function (el) {
          el.removeAttribute('data-diagram-enhanced');
          el.classList.remove('diagram-enhanced');
          var btn = el.querySelector('.diagram-expand-btn');
          if (btn) btn.remove();
        });
      init();
    });
  }
})();
