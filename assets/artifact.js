/* bulletproof artifact review layer.
   Plain classic script (no modules) so it works from file:// with no server.
   Provides: reading controls (theme / size / typeface / width), text
   highlighting, anchored comments, free-standing notes, and an approval
   verdict exported as JSON for the agent to consume.

   Usage in a document's <head>:
     <link rel="stylesheet" href="../assets/artifact.css">
     <script src="../assets/artifact.js" defer
             data-doc="design.html" data-slug="my-feature"></script>
*/
(function () {
  'use strict';

  var script = document.currentScript ||
    document.querySelector('script[src$="artifact.js"]');
  var DOC = (script && script.dataset.doc) || location.pathname.split('/').pop() || 'document.html';
  var SLUG = (script && script.dataset.slug) || '';
  var KEY = 'bp:' + SLUG + ':' + DOC;

  var state = { verdict: '', note: '', items: [], prefs: {} };
  var seq = 0;
  var storageOK = true;

  /* ---------------- storage ---------------- */
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var d = JSON.parse(raw);
        state.verdict = d.verdict || '';
        state.note = d.note || '';
        state.items = Array.isArray(d.items) ? d.items : [];
      }
      var p = localStorage.getItem('bp:prefs');
      if (p) state.prefs = JSON.parse(p) || {};
    } catch (e) { storageOK = false; }
  }
  function save() {
    if (!storageOK) return;
    try {
      localStorage.setItem(KEY, JSON.stringify({
        verdict: state.verdict, note: state.note, items: state.items
      }));
    } catch (e) { storageOK = false; }
  }
  function savePrefs() {
    try { localStorage.setItem('bp:prefs', JSON.stringify(state.prefs)); } catch (e) {}
  }

  /* ---------------- reading preferences ---------------- */
  var root = document.documentElement;
  function applyPrefs() {
    var p = state.prefs;
    if (p.theme) root.setAttribute('data-theme', p.theme); else root.removeAttribute('data-theme');
    root.setAttribute('data-font', p.font || 'serif');
    root.setAttribute('data-width', p.width || 'normal');
    root.style.fontSize = (p.size || 16) + 'px';
  }
  function setPref(k, v) { state.prefs[k] = v; savePrefs(); applyPrefs(); syncBar(); }

  /* ---------------- text position mapping ---------------- */
  // Flatten the document's readable text nodes so a stored quote can be found
  // again after a reload, and so a live selection can be turned into a quote.
  function textNodes() {
    var out = [];
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue) return NodeFilter.FILTER_REJECT;
        var el = n.parentElement;
        while (el) {
          if (el.id === 'bp-bar' || el.id === 'bp-panel' || el.id === 'bp-pop' ||
              el.id === 'bp-print-notes') return NodeFilter.FILTER_REJECT;
          if (el.tagName && el.tagName.toLowerCase() === 'svg') return NodeFilter.FILTER_REJECT;
          el = el.parentElement;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = walker.nextNode())) out.push(n);
    return out;
  }
  function flatten() {
    var nodes = textNodes(), text = '', map = [];
    for (var i = 0; i < nodes.length; i++) {
      map.push({ node: nodes[i], start: text.length });
      text += nodes[i].nodeValue;
    }
    return { text: text, map: map };
  }
  function pointAt(flat, index) {
    for (var i = flat.map.length - 1; i >= 0; i--) {
      if (flat.map[i].start <= index) {
        return { node: flat.map[i].node, offset: index - flat.map[i].start };
      }
    }
    return null;
  }
  function rangeFor(flat, start, end) {
    var a = pointAt(flat, start), b = pointAt(flat, end);
    if (!a || !b) return null;
    var r = document.createRange();
    try {
      r.setStart(a.node, Math.min(a.offset, a.node.nodeValue.length));
      r.setEnd(b.node, Math.min(b.offset, b.node.nodeValue.length));
    } catch (e) { return null; }
    return r;
  }
  function sectionOf(node) {
    var el = node.nodeType === 3 ? node.parentElement : node;
    while (el && el !== document.body) {
      var p = el.previousElementSibling;
      while (p) {
        if (/^H[1-3]$/.test(p.tagName)) return p.textContent.trim();
        p = p.previousElementSibling;
      }
      el = el.parentElement;
    }
    var h = document.querySelector('h1');
    return h ? h.textContent.trim() : '';
  }

  /* ---------------- highlight painting ---------------- */
  function paint(range, item) {
    var nodes = textNodes().filter(function (n) {
      try { return range.intersectsNode(n); } catch (e) { return false; }
    });
    var made = [];
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      var s = (n === range.startContainer) ? range.startOffset : 0;
      var e = (n === range.endContainer) ? range.endOffset : n.nodeValue.length;
      if (e <= s) continue;
      var target = n;
      if (e < target.nodeValue.length) target.splitText(e);
      if (s > 0) target = target.splitText(s);
      var m = document.createElement('mark');
      m.className = 'bp-mark';
      m.dataset.cid = item.id;
      target.parentNode.insertBefore(m, target);
      m.appendChild(target);
      made.push(m);
    }
    if (made.length) made[made.length - 1].dataset.n = item.n;
    made.forEach(function (m) {
      m.addEventListener('click', function () { focusItem(item.id); });
    });
    return made.length > 0;
  }
  function unpaint(id) {
    var marks = document.querySelectorAll('mark.bp-mark[data-cid="' + id + '"]');
    Array.prototype.forEach.call(marks, function (m) {
      var parent = m.parentNode;
      while (m.firstChild) parent.insertBefore(m.firstChild, m);
      parent.removeChild(m);
      parent.normalize();
    });
  }
  function repaintAll() {
    state.items.forEach(function (it) {
      if (it.kind === 'note') return;
      unpaint(it.id);
      it.orphan = true;
      if (!it.quote) return;
      var flat = flatten();
      var from = 0, idx = -1, hit = 0;
      while ((idx = flat.text.indexOf(it.quote, from)) !== -1) {
        if (hit === (it.occurrence || 0)) break;
        hit++; from = idx + 1;
      }
      if (idx === -1) idx = flat.text.indexOf(it.quote);
      if (idx === -1) return;
      var r = rangeFor(flat, idx, idx + it.quote.length);
      if (r && paint(r, it)) it.orphan = false;
    });
  }

  /* ---------------- items ---------------- */
  function nextN() { return ++seq; }
  function addFromSelection(kind) {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    var range = sel.getRangeAt(0);
    var quote = sel.toString().replace(/\s+/g, ' ').trim();
    if (!quote) return null;

    var flat = flatten();
    var occurrence = 0, from = 0, i;
    var abs = -1;
    // best-effort occurrence index: count identical earlier quotes
    while ((i = flat.text.indexOf(quote, from)) !== -1) {
      var r = rangeFor(flat, i, i + quote.length);
      if (r && r.compareBoundaryPoints(Range.START_TO_START, range) === 0) { abs = i; break; }
      occurrence++; from = i + 1;
    }
    if (abs === -1) occurrence = 0;

    var item = {
      id: 'c' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5),
      n: nextN(), kind: kind, quote: quote, occurrence: occurrence,
      section: sectionOf(range.startContainer), body: '', created: new Date().toISOString()
    };
    if (!paint(range, item)) return null;
    sel.removeAllRanges();
    state.items.push(item);
    save(); render();
    if (kind === 'comment') focusItem(item.id, true);
    return item;
  }
  function addNote() {
    var item = {
      id: 'n' + Date.now().toString(36), n: nextN(), kind: 'note',
      quote: '', section: '', body: '', created: new Date().toISOString()
    };
    state.items.push(item); save(); render(); focusItem(item.id, true);
  }
  function removeItem(id) {
    unpaint(id);
    state.items = state.items.filter(function (i) { return i.id !== id; });
    save(); render();
  }
  function focusItem(id, edit) {
    openPanel(true);
    var card = document.querySelector('.bp-c[data-id="' + id + '"]');
    if (!card) return;
    card.scrollIntoView({ block: 'nearest' });
    Array.prototype.forEach.call(document.querySelectorAll('mark.bp-mark'), function (m) {
      m.classList.toggle('bp-active', m.dataset.cid === id);
    });
    var ta = card.querySelector('textarea');
    if (edit && ta) ta.focus();
  }

  /* ---------------- UI ---------------- */
  var bar, panel, pop;
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function btn(label, title, onClick, cls) {
    var b = el('button', 'bp-btn' + (cls ? ' ' + cls : ''), label);
    b.type = 'button'; if (title) b.title = title;
    b.addEventListener('click', onClick);
    return b;
  }

  function buildBar() {
    bar = el('div'); bar.id = 'bp-bar';
    bar.appendChild(el('span', 'bp-title', DOC + (SLUG ? '  ·  ' + SLUG : '')));

    bar.appendChild(btn('A\u2212', 'Smaller text', function () {
      setPref('size', Math.max(13, (state.prefs.size || 16) - 1));
    }));
    bar.appendChild(btn('A+', 'Larger text', function () {
      setPref('size', Math.min(24, (state.prefs.size || 16) + 1));
    }));
    bar.appendChild(btn('Serif', 'Typeface', function () {
      setPref('font', (state.prefs.font || 'serif') === 'serif' ? 'sans' : 'serif');
    }, 'bp-font'));
    bar.appendChild(btn('Width', 'Column width', function () {
      var order = ['narrow', 'normal', 'wide'];
      var cur = order.indexOf(state.prefs.width || 'normal');
      setPref('width', order[(cur + 1) % order.length]);
    }, 'bp-width'));
    bar.appendChild(btn('Theme', 'Light / dark / auto', function () {
      var order = ['auto', 'light', 'dark'];
      var cur = order.indexOf(state.prefs.theme || 'auto');
      var next = order[(cur + 1) % order.length];
      setPref('theme', next === 'auto' ? '' : next);
    }, 'bp-theme'));

    bar.appendChild(btn('Review', 'Show comments & approval (R)', function () { openPanel(); }, 'bp-review'));
    document.body.appendChild(bar);
  }

  function buildPop() {
    pop = el('div'); pop.id = 'bp-pop';
    pop.appendChild(btn('Highlight', 'Highlight selection', function () {
      addFromSelection('highlight'); hidePop();
    }));
    pop.appendChild(btn('Comment', 'Comment on selection', function () {
      addFromSelection('comment'); hidePop();
    }));
    pop.style.display = 'none';
    document.body.appendChild(pop);
  }
  function showPop() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return hidePop();
    if (!sel.toString().trim()) return hidePop();
    var r = sel.getRangeAt(0).getBoundingClientRect();
    if (!r || (!r.width && !r.height)) return hidePop();
    pop.style.display = 'flex';
    var top = r.top + window.scrollY - pop.offsetHeight - 8;
    if (top < window.scrollY + 40) top = r.bottom + window.scrollY + 8;
    pop.style.top = top + 'px';
    pop.style.left = Math.max(8, r.left + window.scrollX + r.width / 2 - pop.offsetWidth / 2) + 'px';
  }
  function hidePop() { if (pop) pop.style.display = 'none'; }

  function buildPanel() {
    panel = el('div'); panel.id = 'bp-panel';
    document.body.appendChild(panel);
  }
  function openPanel(force) {
    var open = force ? true : !panel.classList.contains('open');
    panel.classList.toggle('open', open);
    document.body.classList.toggle('bp-panel-open', open);
  }

  function render() {
    if (!panel) return;
    panel.innerHTML = '';

    var head = el('div', 'bp-sec');
    head.style.marginTop = '0';
    head.appendChild(el('h4', null, 'Comments & notes'));
    var row = el('div', 'bp-row');
    row.appendChild(btn('+ Note', 'Add a note not tied to a selection', addNote));
    row.appendChild(btn('Clear all', 'Remove every comment, highlight and note', function () {
      if (!state.items.length || !window.confirm('Remove all comments and highlights?')) return;
      state.items.slice().forEach(function (i) { unpaint(i.id); });
      state.items = []; save(); render();
    }));
    head.appendChild(row);
    panel.appendChild(head);

    if (!state.items.length) {
      panel.appendChild(el('p', 'bp-empty', 'Select any text to highlight or comment.'));
    }
    state.items.forEach(function (it) {
      var c = el('div', 'bp-c' + (it.orphan ? ' bp-orphan' : ''));
      c.dataset.id = it.id;
      var del = el('button', 'bp-del', '\u00d7');
      del.type = 'button'; del.title = 'Delete';
      del.addEventListener('click', function () { removeItem(it.id); });
      c.appendChild(del);
      c.appendChild(el('span', 'bp-n', '#' + it.n + ' '));
      c.appendChild(document.createTextNode(
        it.kind === 'note' ? 'note' : it.kind === 'highlight' ? 'highlight' : 'comment'));
      c.appendChild(el('div', 'bp-where',
        (it.section || '') + (it.orphan ? '  ·  text not found in document' : '')));
      if (it.quote) {
        var q = el('blockquote', null, it.quote.length > 220 ? it.quote.slice(0, 220) + '\u2026' : it.quote);
        c.appendChild(q);
      }
      if (it.kind !== 'highlight' || it.body) {
        var ta = el('textarea');
        ta.rows = 2; ta.value = it.body || '';
        ta.placeholder = it.kind === 'note' ? 'Note\u2026' : 'What should change?';
        ta.addEventListener('input', function () { it.body = ta.value; save(); });
        c.appendChild(ta);
      } else {
        c.appendChild(btn('Add comment', 'Turn this highlight into a comment', function () {
          it.kind = 'comment'; save(); render(); focusItem(it.id, true);
        }));
      }
      c.addEventListener('click', function () { focusItem(it.id); });
      panel.appendChild(c);
    });

    var v = el('div', 'bp-sec');
    v.appendChild(el('h4', null, 'Decision'));
    var vrow = el('div', 'bp-row');
    [['approve', 'Approve'],
     ['approve-with-comments', 'Approve w/ comments'],
     ['changes-requested', 'Request changes']].forEach(function (pair) {
      var b = btn(pair[1], null, function () {
        state.verdict = (state.verdict === pair[0]) ? '' : pair[0];
        save(); render();
      });
      b.dataset.verdict = pair[0];
      if (state.verdict === pair[0]) b.classList.add('on');
      vrow.appendChild(b);
    });
    v.appendChild(vrow);
    var note = el('textarea'); note.id = 'bp-note'; note.rows = 2;
    note.placeholder = 'Overall note to the agent (optional)';
    note.value = state.note;
    note.addEventListener('input', function () { state.note = note.value; save(); });
    v.appendChild(note);
    panel.appendChild(v);

    var ex = el('div', 'bp-sec');
    ex.appendChild(el('h4', null, 'Hand back to the agent'));
    var erow = el('div', 'bp-row');
    erow.appendChild(btn('Copy JSON', 'Copy the review for pasting into the chat', copyJSON));
    erow.appendChild(btn('Download review.json', 'Save into .ai/<slug>/', downloadJSON));
    ex.appendChild(erow);
    var out = el('textarea'); out.id = 'bp-out'; out.readOnly = true; out.value = json();
    ex.appendChild(out);
    if (!storageOK) {
      ex.appendChild(el('p', 'bp-empty',
        'This browser blocks local storage for file:// pages — export before closing the tab.'));
    }
    panel.appendChild(ex);
    syncBar();
  }

  function syncBar() {
    if (!bar) return;
    var f = bar.querySelector('.bp-font');
    if (f) f.textContent = (state.prefs.font || 'serif') === 'serif' ? 'Serif' : 'Sans';
    var t = bar.querySelector('.bp-theme');
    if (t) t.textContent = state.prefs.theme ? (state.prefs.theme === 'dark' ? 'Dark' : 'Light') : 'Auto';
    var w = bar.querySelector('.bp-width');
    if (w) w.textContent = 'Width: ' + (state.prefs.width || 'normal');
    var r = bar.querySelector('.bp-review');
    if (r) r.textContent = 'Review' + (state.items.length ? ' (' + state.items.length + ')' : '');
  }

  /* ---------------- export ---------------- */
  function json() {
    return JSON.stringify({
      doc: DOC, slug: SLUG,
      generated: new Date().toISOString(),
      verdict: state.verdict || 'pending',
      note: state.note || '',
      items: state.items.map(function (i) {
        return {
          n: i.n, kind: i.kind, section: i.section || '',
          quote: i.quote || '', body: i.body || '',
          anchored: i.kind === 'note' ? true : !i.orphan
        };
      })
    }, null, 2);
  }
  function copyJSON() {
    var text = json();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(fallback);
    } else { fallback(); }
    function fallback() {
      var out = document.getElementById('bp-out');
      if (out) { out.focus(); out.select(); try { document.execCommand('copy'); } catch (e) {} }
    }
  }
  function downloadJSON() {
    var blob = new Blob([json()], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'review.json';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /* ---------------- print endnotes ---------------- */
  function buildPrintNotes() {
    var old = document.getElementById('bp-print-notes');
    if (old) old.remove();
    if (!state.items.length) return;
    var box = el('section'); box.id = 'bp-print-notes';
    box.appendChild(el('h2', null, 'Review notes'));
    var ol = el('ol');
    state.items.forEach(function (i) {
      var li = el('li');
      li.appendChild(el('strong', null, '#' + i.n + ' ' + (i.section || i.kind) + ' — '));
      li.appendChild(document.createTextNode(i.body || '(highlight)'));
      if (i.quote) li.appendChild(el('blockquote', null, i.quote));
      ol.appendChild(li);
    });
    box.appendChild(ol);
    if (state.verdict) box.appendChild(el('p', null, 'Decision: ' + state.verdict + '. ' + state.note));
    document.body.appendChild(box);
  }

  /* ---------------- boot ---------------- */
  function init() {
    load();
    state.items.forEach(function (i) { if (i.n > seq) seq = i.n; });
    applyPrefs();
    buildBar(); buildPanel(); buildPop();
    repaintAll(); render(); syncBar();

    document.addEventListener('mouseup', function (e) {
      if (pop && pop.contains(e.target)) return;
      setTimeout(showPop, 10);
    });
    document.addEventListener('mousedown', function (e) {
      if (pop && !pop.contains(e.target)) hidePop();
    });
    document.addEventListener('keydown', function (e) {
      if (e.target && /^(TEXTAREA|INPUT)$/.test(e.target.tagName)) return;
      if (e.key === 'r' || e.key === 'R') { openPanel(); }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'h' || e.key === 'H')) {
        e.preventDefault(); addFromSelection('highlight'); hidePop();
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'c' || e.key === 'C')) {
        e.preventDefault(); addFromSelection('comment'); hidePop();
      }
    });
    window.addEventListener('beforeprint', buildPrintNotes);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
