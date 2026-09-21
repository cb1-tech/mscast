# -*- coding: utf-8 -*-
import frappe

HTML = """
<div class="mscast-home">
  <div class="greet">
    <div>
      <h1 id="hello">Loading&hellip;</h1>
      <p class="sub" id="asat"></p>
    </div>
    <span class="pill ok" id="mailed">Daily summary emailed 08:30 IST</span>
  </div>

  <section class="kpis" id="kpis" aria-label="Today's position"></section>

  <section class="projects" id="projects" aria-label="Open projects"></section>

  <section class="attention" id="attention" aria-label="Needs attention today"></section>

  <div class="quick" id="quick" aria-label="Start something"></div>

  <h2 class="sr-only">Work areas</h2>
  <div class="cards" id="cards"></div>

  <footer class="foot">
    <span class="dot"></span>
    <span id="footstatus">All services running</span>
    <span class="grow"></span>
    <a href="/app/user" data-dt="User">Users &amp; roles</a>
    <a href="/app/mscast-archival-log" data-dt="MSCAST Archival Log">Backup &amp; archive log</a>
    <a href="/app/query-report/MSCAST%20Daily%20Management%20Summary" data-report="MSCAST Daily Management Summary">Daily summary</a>
    <span class="ver" id="ver"></span>
  </footer>
</div>
"""

STYLE = """
:host { all: initial; }
* { box-sizing: border-box; }
.mscast-home { font-family: 'IBM Plex Sans', system-ui, sans-serif; color: #1b1d21; display: flex; flex-direction: column; gap: 18px; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
a { color: #1f3864; text-decoration: none; }
a:hover { color: #8f3f06; text-decoration: underline; }
h1 { margin: 0; font-family: 'Archivo', system-ui, sans-serif; font-size: 27px; font-weight: 700; color: #17294a; letter-spacing: -0.01em; }
h2 { margin: 0; font-family: 'Archivo', system-ui, sans-serif; font-size: 16px; font-weight: 600; color: #17294a; }
h3 { margin: 0; font-family: 'Archivo', system-ui, sans-serif; font-size: 15px; font-weight: 600; color: #17294a; }
p { margin: 0; }
.greet { display: flex; align-items: flex-end; gap: 18px; flex-wrap: wrap; }
.greet .sub { font-size: 13.5px; color: #5b606b; margin-top: 4px; }
.grow { flex-grow: 1; }
.pill { font-size: 12.5px; font-weight: 500; border-radius: 999px; padding: 7px 13px; white-space: nowrap; }
.pill.ok { color: #14664a; background: #e7f1ec; border: 1px solid #bfd9cd; margin-left: auto; }
.kpis { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 0; background: #fff; border: 1px solid #e3e1db; border-radius: 14px; padding: 6px; }
.kpi { display: flex; flex-direction: column; gap: 5px; padding: 15px 16px; border-radius: 10px; min-height: 44px; }
.kpi:hover { background: #f6f5f2; text-decoration: none; }
.kpi + .kpi { box-shadow: inset 1px 0 0 #ece9e3; }
.kpi .lbl { font-size: 10.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: #5b606b; }
.kpi .val { font-family: 'Archivo', system-ui, sans-serif; font-size: 24px; font-weight: 700; color: #17294a; }
.kpi .note { font-size: 12px; color: #5b606b; }
.kpi .note.warn { color: #8f3f06; }
.kpi .note.good { color: #14664a; }
.projects { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 16px; }
.proj { background: #fff; border: 1px solid #e3e1db; border-radius: 14px; padding: 16px 18px; display: flex; flex-direction: column; gap: 11px; }
.proj .top { display: flex; align-items: flex-start; gap: 10px; }
.proj .cust { font-size: 12.5px; color: #5b606b; margin-top: 2px; }
.proj .due { text-align: right; font-size: 12.5px; color: #5b606b; white-space: nowrap; }
.proj .due b { display: block; font-size: 13.5px; color: #17294a; }
.proj .due.tight b { color: #8f3f06; }
.bar { height: 7px; border-radius: 99px; background: #ece9e3; overflow: hidden; }
.bar i { display: block; height: 100%; background: #1f3864; }
.proj .figs { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.proj .figs div { display: flex; flex-direction: column; gap: 2px; }
.proj .figs .k { font-size: 10.5px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: #5b606b; }
.proj .figs .v { font-size: 14px; font-weight: 500; color: #17294a; font-variant-numeric: tabular-nums; }
.proj .figs .v.draftpcc { color: #8f3f06; }
.attention { background: #fff; border: 1px solid #e3e1db; border-left: 4px solid #b45309; border-radius: 14px; padding: 16px 20px 18px; display: flex; flex-direction: column; gap: 12px; }
.attention .hd { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.attention .hd .n { font-size: 12.5px; color: #5b606b; }
.rows { display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 9px 20px; }
.row { display: flex; align-items: center; gap: 11px; padding: 9px 12px; background: #faf8f4; border: 1px solid #ede9e0; border-radius: 10px; min-height: 44px; color: #1b1d21; }
.row:hover { background: #f4f0e8; text-decoration: none; }
.row .v { min-width: 30px; height: 28px; padding: 0 8px; border-radius: 8px; background: #b45309; color: #fff; font-size: 12.5px; font-weight: 600; display: flex; align-items: center; justify-content: center; white-space: nowrap; }
.row .t { flex-grow: 1; font-size: 13.5px; font-weight: 500; color: #1f3864; }
.row .why { font-size: 11.5px; color: #5b606b; white-space: nowrap; }
.cleared { font-size: 12.5px; color: #5b606b; }
.quick { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
.quick .lbl { font-size: 10.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: #5b606b; margin-right: 4px; }
.qa { display: inline-flex; align-items: center; gap: 7px; min-height: 44px; font-size: 13.5px; font-weight: 500; background: #fff; border: 1px solid #cfccc3; border-radius: 999px; padding: 11px 16px; }
.qa:hover { border-color: #1f3864; text-decoration: none; }
.qa svg { flex-shrink: 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 16px; }
.card { background: #fff; border: 1px solid #e3e1db; border-radius: 14px; padding: 16px 20px 12px; display: flex; flex-direction: column; gap: 9px; }
.card.dark { background: #17294a; border-color: #17294a; }
.card .ch { display: flex; align-items: center; gap: 11px; }
.card .ic { width: 32px; height: 32px; border-radius: 9px; background: #eef1f7; color: #1f3864; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.card.dark .ic { background: #2c4877; color: #fff; }
.card.dark h3 { color: #fff; }
.card .badge { font-size: 11px; font-weight: 600; color: #1f3864; background: #eef1f7; border-radius: 999px; padding: 4px 9px; white-space: nowrap; }
.card .badge.warn { color: #8f3f06; background: #fbf1e8; }
.card.dark .badge { color: #17294a; background: #e6c48a; }
.card .ln { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 8px 0; border-top: 1px solid #f0efea; min-height: 44px; font-size: 14px; }
.card.dark .ln { border-top-color: #2c4877; }
.card.dark .ln a { color: #fff; }
.card .ln .c { font-size: 12px; color: #5b606b; white-space: nowrap; font-variant-numeric: tabular-nums; }
.card.dark .ln .c { color: #aebdd8; }
.card .ln .c.warn { color: #8f3f06; }
.card .ln .c.good { color: #14664a; }
.foot { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; padding: 14px 0 4px; border-top: 1px solid #e3e1db; font-size: 12.5px; color: #5b606b; }
.foot .dot { width: 9px; height: 9px; border-radius: 99px; background: #14664a; }
.foot a { font-size: 13px; }
.foot .ver { font-size: 11.5px; }
@media (max-width: 1100px) { .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); } .kpi + .kpi { box-shadow: none; } }
@media (max-width: 700px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } .proj .figs { grid-template-columns: repeat(2, minmax(0, 1fr)); } h1 { font-size: 22px; } }
"""

SCRIPT = r"""
(function () {
  var F = window.frappe;
  var $r = root_element;

  // --- desk-wide theme, injected once into the document head -------------
  function theme() {
    if (document.getElementById('mscast-fonts') === null) {
      var l = document.createElement('link');
      l.id = 'mscast-fonts'; l.rel = 'stylesheet';
      l.href = 'https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap';
      document.head.appendChild(l);
    }
    if (document.getElementById('mscast-theme')) return;
    var s = document.createElement('style');
    s.id = 'mscast-theme';
    s.textContent = [
      ":root{--primary:#1f3864;--primary-color:#1f3864;--blue-500:#1f3864;--blue-600:#17294a;--blue-700:#17294a;--text-color:#1b1d21;--heading-color:#17294a;--bg-blue:#eef1f7;--border-radius-md:10px;}",
      "body{background:#f6f5f2;font-family:'IBM Plex Sans',system-ui,sans-serif;}",
      "h1,h2,h3,h4,h5,.page-title,.title-text,.widget-title,.ellipsis.title-text{font-family:'Archivo',system-ui,sans-serif;letter-spacing:-0.005em;}",
      ".navbar{background:#1f3864 !important;border-bottom:1px solid #17294a !important;}",
      ".navbar .navbar-brand,.navbar .nav-link,.navbar a,.navbar .dropdown-toggle,.navbar .navbar-home,.navbar span{color:#ffffff !important;}",
      ".navbar .navbar-icon,.navbar svg.icon{filter:brightness(0) invert(1);}",
      "#navbar-search,.navbar .search-bar input,.navbar .awesomplete input{background:#2c4877 !important;border:1px solid #47659a !important;color:#fff !important;}",
      "#navbar-search::placeholder,.navbar input::placeholder{color:#c3cee2 !important;opacity:1;}",
      ".btn-primary,.btn-primary:focus{background-color:#1f3864 !important;border-color:#1f3864 !important;color:#fff !important;}",
      ".btn-primary:hover{background-color:#17294a !important;border-color:#17294a !important;}",
      ".btn-secondary,.btn-default{border:1px solid #cfccc3 !important;}",
      ".page-head{background:#f6f5f2 !important;}",
      ".layout-main-section,.widget,.form-section,.list-row-container,.frappe-card{border-radius:12px;}",
      ".sidebar-item-container .desk-sidebar-item.selected,.standard-sidebar-item.selected{background:#eef1f7 !important;}",
      ".indicator-pill.blue,.indicator-pill.grey{font-variant-numeric:tabular-nums;}",
      ".custom-block-widget-box>.widget-head{display:none !important;}",
      ".custom-block-widget-box{border:none !important;background:transparent !important;padding:0 !important;box-shadow:none !important;}",
      ".workspace-sidebar .standard-sidebar-label{letter-spacing:.08em;text-transform:uppercase;font-size:10.5px;color:#5b606b;}"
    ].join("\n");
    document.head.appendChild(s);
  }
  theme();

  // --- routing ------------------------------------------------------------
  $r.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    try {
      if (a.dataset.newdoc) { e.preventDefault(); F.new_doc(a.dataset.newdoc); return; }
      if (a.dataset.report) { e.preventDefault(); F.set_route('query-report', a.dataset.report); return; }
      if (a.dataset.dt) {
        e.preventDefault();
        var f = a.dataset.filters ? JSON.parse(a.dataset.filters) : {};
        F.set_route('List', a.dataset.dt, f);
        return;
      }
    } catch (err) { /* fall through to the href */ }
  });

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html !== undefined) n.innerHTML = html;
    return n;
  }
  function lnk(cls, label, opts) {
    var a = el('a', cls);
    a.setAttribute('href', opts.href || '#');
    if (opts.dt) { a.dataset.dt = opts.dt; if (opts.filters) a.dataset.filters = JSON.stringify(opts.filters); }
    if (opts.report) a.dataset.report = opts.report;
    if (opts.newdoc) a.dataset.newdoc = opts.newdoc;
    a.innerHTML = label;
    return a;
  }
  function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  var route = {
    list: function (dt, f) { return '/app/' + dt.toLowerCase().replace(/ /g, '-') + (f ? '?' + Object.keys(f).map(function (k) { return k + '=' + encodeURIComponent(f[k]); }).join('&') : ''); },
    rep: function (n) { return '/app/query-report/' + encodeURIComponent(n); }
  };
  var ICON = {
    sales: '<path d="M3 17l5-5 4 3 5-7 4 5"/><path d="M3 21h18"/>',
    proj: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h7"/><path d="M7 13h10"/><path d="M7 17h5"/>',
    design: '<path d="M4 20 20 4"/><path d="M4 14v6h6"/><path d="M14 4h6v6"/>',
    buy: '<path d="M3 6h15l-1.5 8H6.5z"/><path d="M6.5 14 5 4H2"/><circle cx="9" cy="19" r="1.4"/><circle cx="17" cy="19" r="1.4"/>',
    store: '<path d="M12 3 21 7.5v9L12 21 3 16.5v-9z"/><path d="M3 7.5 12 12l9-4.5"/><path d="M12 12v9"/>',
    qc: '<path d="M9 11.5 11.5 14 16 9"/><path d="M12 3l7.5 3v6c0 4.2-3 7.6-7.5 9-4.5-1.4-7.5-4.8-7.5-9V6z"/>',
    acc: '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/><path d="M7 15h4"/>',
    hr: '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><path d="M16 5.5a3 3 0 0 1 0 5.6"/><path d="M18 20c0-2.6-1-4.4-2.6-5.4"/>',
    mis: '<path d="M5 20V10"/><path d="M12 20V4"/><path d="M19 20v-7"/>',
    plus: '<path d="M12 5v14"/><path d="M5 12h14"/>'
  };
  function svg(k, size, stroke) {
    return '<svg width="' + (size || 18) + '" height="' + (size || 18) + '" viewBox="0 0 24 24" fill="none" stroke="' + (stroke || 'currentColor') + '" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICON[k] + '</svg>';
  }

  function render(d) {
    var ind = d.indicators || {};
    function v(k) { return (ind[k] && ind[k].value !== undefined && ind[k].value !== null) ? ind[k].value : '—'; }
    function money(k) { return String(v(k)).replace(/^Rs /, '₹ '); }

    var hour = new Date().getHours();
    var part = hour < 12 ? 'Good morning' : (hour < 17 ? 'Good afternoon' : 'Good evening');
    var first = (d.user.full_name || '').split(' ')[0] || 'there';
    $r.getElementById('hello').textContent = part + ', ' + first;
    $r.getElementById('asat').textContent = d.as_at + ' · every figure below is the one in this morning’s emailed summary';
    $r.getElementById('ver').textContent = 'ERPNext v16 · India Compliance · Frappe HR';

    // KPI tiles -------------------------------------------------------------
    var kpis = [
      { l: 'Cash & bank', v: money('Cash and bank balance'), n: '2 accounts', href: route.rep('General Ledger'), report: 'General Ledger' },
      { l: 'Receivables', v: money('Outstanding from customers'), n: String(v('Overdue beyond due date')).replace(/^Rs /, '₹ ') + ' overdue', cls: String(v('Overdue beyond due date')) === 'Rs 0' ? 'good' : 'warn', href: route.rep('MSCAST Schedule III - Trade Receivable Ageing'), report: 'MSCAST Schedule III - Trade Receivable Ageing' },
      { l: 'Payables', v: money('Outstanding to suppliers'), n: money('MSME dues due within the next 15 days') + ' MSME in 15 days', cls: 'warn', href: route.rep('MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))'), report: 'MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))' },
      { l: 'Order book', v: money('Orders in hand (booked less billed)'), n: v('Open projects') + ' projects running', href: route.list('Sales Order'), dt: 'Sales Order' },
      { l: 'Billed this month', v: money('Billed this month'), n: 'against milestones', href: route.list('Sales Invoice'), dt: 'Sales Invoice' },
      { l: 'Retention held', v: money('Retention held by customers'), n: 'released on certificate', href: route.rep('MSCAST Retention and Certificates'), report: 'MSCAST Retention and Certificates' }
    ];
    var kw = $r.getElementById('kpis');
    kw.innerHTML = '';
    kpis.forEach(function (k) {
      var a = lnk('kpi', '<span class="lbl">' + esc(k.l) + '</span><span class="val">' + esc(k.v) + '</span><span class="note ' + (k.cls || '') + '">' + esc(k.n) + '</span>', k);
      kw.appendChild(a);
    });

    // Open projects ---------------------------------------------------------
    var pw = $r.getElementById('projects');
    pw.innerHTML = '';
    (d.projects || []).forEach(function (p) {
      var c = el('article', 'proj');
      var tight = p.days_left !== null && p.days_left < 60;
      var draft = p.pcc_state && p.pcc_state !== 'Approved';
      c.innerHTML =
        '<div class="top"><div style="flex-grow:1"><h3>' + esc(p.title) + '</h3><div class="cust">' + esc(p.customer) + ' · ' + esc(p.name) + '</div></div>' +
        '<div class="due' + (tight ? ' tight' : '') + '"><b>' + esc(p.due) + '</b>' + (p.days_left !== null ? esc(p.days_left) + ' days left' : '') + '</div></div>' +
        '<div class="bar"><i style="width:' + Math.max(2, Math.min(100, p.percent)) + '%"></i></div>' +
        '<div class="figs">' +
        '<div><span class="k">Contract</span><span class="v">' + esc(String(p.contract).replace(/^Rs /, '₹ ')) + '</span></div>' +
        '<div><span class="k">Cost (PCC)</span><span class="v' + (draft ? ' draftpcc' : '') + '">' + esc(String(p.cost).replace(/^Rs /, '₹ ')) + (draft ? ' draft' : '') + '</span></div>' +
        '<div><span class="k">Margin</span><span class="v">' + (p.margin === null ? '—' : esc(p.margin) + '%') + '</span></div>' +
        '<div><span class="k">Billed</span><span class="v">' + esc(String(p.billed).replace(/^Rs /, '₹ ')) + '</span></div>' +
        '</div>';
      var foot = el('div', 'figs');
      foot.style.gridTemplateColumns = 'auto auto auto';
      foot.style.gap = '14px';
      foot.appendChild(lnk('', 'Open project', { href: '/app/project/' + p.name, dt: 'Project' }));
      if (p.pcc) foot.appendChild(lnk('', 'Cost sheet (PCC)', { href: '/app/mscast-pcc/' + p.pcc, dt: 'MSCAST PCC' }));
      foot.appendChild(lnk('', 'Schedule', { href: route.rep('MSCAST Project MIS'), report: 'MSCAST Project MIS' }));
      c.appendChild(foot);
      pw.appendChild(c);
    });

    // Needs attention -------------------------------------------------------
    var MAP = {
      'Drawings sitting with the customer for approval': { dt: 'MSCAST Drawing', filters: { status: 'For Customer Approval' }, t: 'Drawings waiting on the customer' },
      'Drawings still in draft with us': { dt: 'MSCAST Drawing', filters: { status: 'Draft' }, t: 'Drawings still in draft with us' },
      'Inspection stages pending': { dt: 'MSCAST Inspection Plan', filters: { result: 'Pending' }, t: 'Inspection stages still to be done' },
      'Inspections rejected or accepted with deviation': { dt: 'MSCAST Inspection Plan', t: 'Inspections rejected or passed with deviation' },
      'MSME dues due within the next 15 days': { report: 'MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))', t: 'MSME bills reaching the 45-day limit' },
      'MSME dues beyond 45 days (s.43B(h) risk)': { report: 'MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))', t: 'MSME bills past the 45-day limit' },
      'Falling due in the next 7 days': { report: 'MSCAST Schedule III - Trade Receivable Ageing', t: 'Customer money falling due this week' },
      'Overdue beyond due date': { report: 'MSCAST Schedule III - Trade Receivable Ageing', t: 'Receivables past their due date' },
      'Client claims open': { dt: 'MSCAST Client Claim', t: 'Client claims agreed but not yet billed' },
      'Acceptance certificates awaited from customers': { dt: 'MSCAST Project Certificate', filters: { status: 'Awaited' }, t: 'Acceptance certificates not yet received' },
      'Purchase orders not fully received': { dt: 'Purchase Order', t: 'Purchase orders not fully received' },
      'BRMs pending certification (payment blocked)': { dt: 'MSCAST BRM', t: 'Supplier bills waiting for certification' }
    };
    var watch = [], cleared = [];
    (d.summary || []).forEach(function (s) {
      var m = MAP[s.indicator];
      if (!m) return;
      var att = (s.attention || '').toUpperCase();
      if (att.indexOf('WATCH') === 0 || att.indexOf('ACTION') === 0) {
        watch.push({ s: s, m: m });
      } else if (att === 'OK') {
        cleared.push(m.t.toLowerCase());
      }
    });
    var aw = $r.getElementById('attention');
    aw.innerHTML = '';
    var hd = el('div', 'hd',
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.3 3.9 2.4 17.5A1.9 1.9 0 0 0 4 20.4h16a1.9 1.9 0 0 0 1.6-2.9L13.7 3.9a1.9 1.9 0 0 0-3.4 0Z"/></svg>');
    hd.appendChild(el('h2', '', 'Needs attention today'));
    hd.appendChild(el('span', 'n', watch.length + (watch.length === 1 ? ' item' : ' items') + ', each one click away'));
    aw.appendChild(hd);
    var rows = el('div', 'rows');
    watch.forEach(function (w) {
      var why = (w.s.attention || '').replace(/^WATCH\s*-?\s*/i, '').replace(/^ACTION\s*-?\s*/i, '');
      var a = lnk('row',
        '<span class="v">' + esc(String(w.s.value).replace(/^Rs /, '₹ ')) + '</span>' +
        '<span class="t">' + esc(w.m.t) + '</span>' +
        (why ? '<span class="why">' + esc(why) + '</span>' : ''),
        { href: w.m.report ? route.rep(w.m.report) : route.list(w.m.dt, w.m.filters), report: w.m.report, dt: w.m.dt, filters: w.m.filters });
      rows.appendChild(a);
    });
    aw.appendChild(rows);
    if (cleared.length) {
      aw.appendChild(el('p', 'cleared', 'Cleared today — nothing on: ' + esc(cleared.join('; ')) + '.'));
    }

    // Quick actions ---------------------------------------------------------
    var qw = $r.getElementById('quick');
    qw.innerHTML = '<span class="lbl">Start something</span>';
    [['Quotation', 'Quotation'], ['Sales order', 'Sales Order'], ['Purchase order', 'Purchase Order'], ['Stock entry', 'Stock Entry'], ['Payment entry', 'Payment Entry'], ['Expense claim', 'Expense Claim']].forEach(function (q) {
      qw.appendChild(lnk('qa', '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#b45309" stroke-width="2" stroke-linecap="round" aria-hidden="true">' + ICON.plus + '</svg>' + esc(q[0]), { href: '/app/' + q[1].toLowerCase().replace(/ /g, '-') + '/new', newdoc: q[1] }));
    });

    // Cards -----------------------------------------------------------------
    var c = d.counts || {};
    function n(x) { return String(x); }
    var CARDS = [
      { ic: 'sales', t: 'Sales & estimation', badge: money('Orders in hand (booked less billed)'), rows: [
        ['Open opportunities', n(c.opportunity_open), { dt: 'Opportunity' }],
        ['Quotations', n(c.quotation), { dt: 'Quotation' }],
        ['Cost sheets (PCC)', null, { dt: 'MSCAST PCC' }],
        ['Sales orders', n(c.so_open), { dt: 'Sales Order' }],
        ['Billing schedule by milestone', null, { report: 'MSCAST Billing and Dispatch Schedule' }]
      ]},
      { ic: 'proj', t: 'Projects & execution', badge: v('Open projects') + ' open', rows: [
        ['Projects', n(c.so_open), { dt: 'Project' }],
        ['Project MIS (cost against PCC)', null, { report: 'MSCAST Project MIS' }],
        ['Kick-off checklists', c.kickoff_open ? n(c.kickoff_open) + ' open' : null, { dt: 'MSCAST Project Kickoff' }],
        ['Acceptance certificates', n(c.cert_awaited) + ' awaited', { dt: 'MSCAST Project Certificate' }, 'warn'],
        ['Client claims', n(c.claims_open) + ' open', { dt: 'MSCAST Client Claim' }, 'warn']
      ]},
      { ic: 'design', t: 'Design & drawings', badge: n(c.drawing_customer + c.drawing_draft) + ' in play', badgeWarn: true, rows: [
        ['Drawing register', n(c.drawing_total), { report: 'MSCAST Drawing Register' }],
        ['With the customer for approval', n(c.drawing_customer), { dt: 'MSCAST Drawing', filters: { status: 'For Customer Approval' } }, 'warn'],
        ['Still in draft with us', n(c.drawing_draft), { dt: 'MSCAST Drawing', filters: { status: 'Draft' } }, 'warn'],
        ['Material data files (MDF)', c.mdf_draft ? n(c.mdf_draft) + ' unreleased' : 'released', { dt: 'MSCAST MDF' }],
        ['Transmittals', n(c.transmittal), { dt: 'MSCAST Transmittal' }]
      ]},
      { ic: 'buy', t: 'Purchase & vendors', badge: n(c.po_open) + ' open PO', rows: [
        ['Material requests', n(c.mr_pending) + ' pending', { dt: 'Material Request' }],
        ['Requests for quotation', n(c.rfq), { dt: 'Request for Quotation' }],
        ['Purchase orders', n(c.po_open), { dt: 'Purchase Order' }],
        ['PO against PCC variance', null, { report: 'MSCAST PO vs PCC Variance' }],
        ['Billing Routing Memos (BRM)', c.brm_pending ? n(c.brm_pending) + ' to certify' : 'none pending', { dt: 'MSCAST BRM' }, c.brm_pending ? 'warn' : 'good']
      ]},
      { ic: 'store', t: 'Stores & dispatch', badge: n(c.items) + ' items', rows: [
        ['Stock balance', null, { report: 'Stock Balance' }],
        ['Issue material to a project', null, { dt: 'Stock Entry' }],
        ['Free issue lying with vendors', null, { report: 'MSCAST Free Issue at Vendor' }],
        ['Material Dispatch Memos', n(c.mdm), { dt: 'MSCAST MDM' }],
        ['Delivery instructions to site', n(c.di), { dt: 'MSCAST Delivery Instruction' }]
      ]},
      { ic: 'qc', t: 'Quality', badge: n(c.insp_pending) + ' pending', badgeWarn: true, rows: [
        ['Inspection plan & status', n(c.insp_plans), { report: 'MSCAST Inspection Status' }],
        ['Stages still to be done', n(c.insp_pending), { dt: 'MSCAST Inspection Plan', filters: { result: 'Pending' } }, 'warn'],
        ['Incoming inspection at receipt', n(c.qi), { dt: 'Quality Inspection' }],
        ['Spares handover', n(c.spares), { dt: 'MSCAST Spares Handover' }],
        ['Commissioning reports', null, { dt: 'MSCAST Commissioning Report' }]
      ]},
      { ic: 'acc', t: 'Accounts & compliance', badge: 'FY 2026-27', rows: [
        ['Payments to release', money('MSME dues due within the next 15 days') + ' due', { dt: 'Purchase Invoice' }, 'warn'],
        ['Sales invoices & receipts', money('Billed this month') + ' MTD', { dt: 'Sales Invoice' }],
        ['GST returns and ITC-04', null, { report: 'MSCAST GST on Closing Inventory (ITC and ITC-04)' }],
        ['Bank guarantees', n(c.bg) + (d.bg_next ? ' · next ' + d.bg_next : ''), { dt: 'Bank Guarantee' }],
        ['Schedule III financials', null, { report: 'MSCAST Balance Sheet (Schedule III)' }]
      ]},
      { ic: 'hr', t: 'People', badge: n(c.employees) + ' on roll', rows: [
        ['Attendance', null, { report: 'MSCAST Biometric Attendance Audit' }],
        ['Leave applications', c.leave_pending ? n(c.leave_pending) + ' waiting' : 'none waiting', { dt: 'Leave Application' }, c.leave_pending ? 'warn' : 'good'],
        ['Payroll run', null, { dt: 'Payroll Entry' }],
        ['Expense claims from site', n(c.expense_claims), { dt: 'Expense Claim' }],
        ['Employee records', n(c.employees), { dt: 'Employee' }]
      ]},
      { ic: 'mis', t: 'Director’s desk', dark: true, badge: 'daily 08:30', rows: [
        ['Daily management summary', '20 indicators', { report: 'MSCAST Daily Management Summary' }],
        ['Sales order to cash tracker', null, { report: 'MSCAST SO - PO - Invoice Tracker' }],
        ['Project cost MIS', null, { report: 'MSCAST Project MIS' }],
        ['Receivable & payable ageing', null, { report: 'MSCAST Schedule III - Trade Receivable Ageing' }],
        ['Project closure report', null, { report: 'MSCAST Project Closure Report' }]
      ]}
    ];
    var cw = $r.getElementById('cards');
    cw.innerHTML = '';
    CARDS.forEach(function (card) {
      var box = el('article', 'card' + (card.dark ? ' dark' : ''));
      var head = el('div', 'ch', '<span class="ic">' + svg(card.ic) + '</span>');
      head.appendChild(el('h3', '', esc(card.t)));
      head.appendChild(el('span', '', ''));
      head.lastChild.className = 'badge' + (card.badgeWarn ? ' warn' : '');
      head.lastChild.style.marginLeft = 'auto';
      head.lastChild.textContent = card.badge;
      box.appendChild(head);
      card.rows.forEach(function (r) {
        var line = el('div', 'ln');
        line.appendChild(lnk('', esc(r[0]), { href: r[2].report ? route.rep(r[2].report) : route.list(r[2].dt, r[2].filters), report: r[2].report, dt: r[2].dt, filters: r[2].filters }));
        if (r[1] !== null && r[1] !== undefined) {
          var s = el('span', 'c' + (r[3] ? ' ' + r[3] : ''));
          s.textContent = r[1];
          line.appendChild(s);
        }
        box.appendChild(line);
      });
      cw.appendChild(box);
    });
  }

  F.call({ method: 'mscast_home_data' })
    .then(function (r) { if (r && r.message) render(r.message); })
    .catch(function (e) {
      $r.getElementById('hello').textContent = 'Could not load today’s figures';
      $r.getElementById('asat').textContent = 'Open the daily management summary report instead.';
      console.error(e);
    });
})();
"""

name = "MSCAST Home"
if frappe.db.exists("Custom HTML Block", name):
    doc = frappe.get_doc("Custom HTML Block", name)
else:
    doc = frappe.new_doc("Custom HTML Block")
    doc.name = name
doc.private = 0
doc.html = HTML
doc.style = STYLE
doc.script = SCRIPT
doc.set("roles", [])
doc.save(ignore_permissions=True)
frappe.db.commit()
print("custom html block saved:", doc.name, "html", len(HTML), "css", len(STYLE), "js", len(SCRIPT))
