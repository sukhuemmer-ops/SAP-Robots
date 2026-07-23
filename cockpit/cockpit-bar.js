/**
 * cockpit-bar.js — Globale YCONN Cockpit-Statusleiste
 * =====================================================
 * FIXED (bleibt beim Scrollen immer oben sichtbar)
 *
 *  LINKS  — 🌐 EN|DE · ← Zurück · 🏠 Start
 *  RECHTS — SAP-System (SEP/SEQ) · Benutzer-Chip · ⏻ Abmelden
 *
 * Einbinden: <script src="cockpit-bar.js"></script>  (nach auth.js)
 * Läuft vollautomatisch — keine weiteren Aufrufe nötig.
 *
 * API:
 *   YCONN_LANG.get()         → 'en' | 'de'
 *   YCONN_LANG.set('de')     → speichert + aktualisiert Bar
 *   YCONN_LANG.toggle()      → wechselt Sprache
 *   YCONN_LANG.onChange(fn)  → Callback bei Sprachwechsel
 */
(function () {
  'use strict';

  var LANG_KEY   = 'yconn_lang';
  var SAP_KEY    = 'yconn_sap_conn';
  var BAR_HEIGHT = 36;   // px — muss mit CSS-min-height übereinstimmen

  // ── Sprach-API ────────────────────────────────────────────────────────────
  var _langListeners = [];
  window.YCONN_LANG = {
    get: function () {
      return localStorage.getItem(LANG_KEY) || 'en';
    },
    set: function (lang) {
      lang = (lang === 'de') ? 'de' : 'en';
      localStorage.setItem(LANG_KEY, lang);
      _refreshBar();
      _langListeners.forEach(function (fn) { try { fn(lang); } catch (e) {} });
    },
    toggle: function () {
      YCONN_LANG.set(YCONN_LANG.get() === 'en' ? 'de' : 'en');
    },
    onChange: function (fn) { _langListeners.push(fn); },
  };

  // ── SAP-System auslesen ───────────────────────────────────────────────────
  function _getSapSystem() {
    try {
      var raw = localStorage.getItem('yconn_user') || sessionStorage.getItem('yconn_user');
      var u = JSON.parse(raw);
      if (u && u.sap_system) return u.sap_system.toUpperCase();
    } catch (e) {}
    try {
      var conn = JSON.parse(localStorage.getItem(SAP_KEY) || '{}');
      if (conn.system) return conn.system.toUpperCase();
    } catch (e) {}
    return 'SEQ';
  }

  function _getUser() {
    try {
      var raw = localStorage.getItem('yconn_user') || sessionStorage.getItem('yconn_user');
      return JSON.parse(raw);
    } catch (e) { return null; }
  }

  function _esc(s) {
    return String(s || '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  window._yconnBarLogout = function () {
    localStorage.removeItem('yconn_user');
    sessionStorage.removeItem('yconn_user');
    location.replace('login.html');
  };

  // ── Bar-Inhalt rendern ────────────────────────────────────────────────────
  function _refreshBar() {
    var bar = document.getElementById('yconn-cockpit-bar');
    if (!bar) return;

    var lang  = YCONN_LANG.get();
    var sys   = _getSapSystem();
    var user  = _getUser();
    var isSeq = sys === 'SEQ';

    var sysColor  = isSeq ? '#10b981' : '#f59e0b';
    var sysBg     = isSeq ? 'rgba(16,185,129,.18)' : 'rgba(245,158,11,.18)';
    var sysBorder = isSeq ? 'rgba(16,185,129,.4)'  : 'rgba(245,158,11,.4)';
    var sysIcon   = isSeq ? '🟢' : '🟡';

    var userName  = user ? (user.display_name || user.username || '?') : '—';
    var initials  = userName.split(' ')
      .map(function (w) { return w[0] || ''; })
      .join('').slice(0, 2).toUpperCase();
    var roleColor = !user ? '#8b949e'
      : user.role === 'Admin'    ? '#f59e0b'
      : user.role === 'Approver' ? '#fb7185'
      : user.role === 'Readonly' ? '#8b949e' : '#10b981';
    var userRole  = user ? (user.role || '') : '';

    var logoutLabel = lang === 'de' ? 'Abmelden' : 'Logout';
    var backLabel   = lang === 'de' ? 'Zurück'   : 'Back';
    var startLabel  = lang === 'de' ? 'Start'    : 'Home';

    /* ── Button-Basis-Style ── */
    var btnBase =
      'border-radius:5px;padding:2px 9px;font-size:11px;font-weight:500;' +
      'cursor:pointer;white-space:nowrap;line-height:1.7;transition:.12s;';

    /* ── LINKS: Sprache + Navigation ── */
    var leftHtml =
      '<div style="display:flex;align-items:center;gap:4px;">' +

        /* Sprache */
        '<span style="font-size:10px;color:#8b949e;margin-right:2px;user-select:none;">🌐</span>' +
        '<button onclick="YCONN_LANG.set(\'en\')" title="English" style="' + btnBase +
          'background:' + (lang === 'en' ? 'rgba(31,111,235,.25)' : 'transparent') + ';' +
          'border:1px solid ' + (lang === 'en' ? '#388bfd' : 'transparent') + ';' +
          'color:' + (lang === 'en' ? '#79b8ff' : '#8b949e') + ';' +
          'font-weight:' + (lang === 'en' ? '700' : '400') + ';">EN</button>' +
        '<span style="color:#30363d;font-size:10px;">|</span>' +
        '<button onclick="YCONN_LANG.set(\'de\')" title="Deutsch" style="' + btnBase +
          'background:' + (lang === 'de' ? 'rgba(31,111,235,.25)' : 'transparent') + ';' +
          'border:1px solid ' + (lang === 'de' ? '#388bfd' : 'transparent') + ';' +
          'color:' + (lang === 'de' ? '#79b8ff' : '#8b949e') + ';' +
          'font-weight:' + (lang === 'de' ? '700' : '400') + ';">DE</button>' +

        /* Trenner */
        '<span style="color:#30363d;font-size:14px;margin:0 4px;">│</span>' +

        /* Zurück */
        '<button onclick="history.back()" title="' + backLabel + '" style="' + btnBase +
          'background:rgba(48,54,61,.6);border:1px solid #30363d;color:#8b949e;">' +
          '← ' + backLabel +
        '</button>' +

        /* Start */
        '<a href="startseite.html" title="' + startLabel + '" style="' + btnBase +
          'background:rgba(31,111,235,.15);border:1px solid rgba(31,111,235,.35);' +
          'color:#79b8ff;text-decoration:none;display:inline-flex;align-items:center;gap:4px;">' +
          '🏠 ' + startLabel +
        '</a>' +

      '</div>';

    /* ── RECHTS: SAP-System + User + Logout ── */
    var rightHtml =
      '<div style="display:flex;align-items:center;gap:7px;">' +

        /* SAP-System Badge */
        '<span style="background:' + sysBg + ';color:' + sysColor + ';' +
          'border:1px solid ' + sysBorder + ';border-radius:5px;' +
          'padding:2px 9px;font-size:11px;font-weight:700;letter-spacing:.4px;' +
          'white-space:nowrap;" title="Aktives SAP-System">' +
          sysIcon + ' ' + sys +
        '</span>' +

        /* Benutzer-Chip */
        (user
          ? '<div style="display:flex;align-items:center;gap:5px;' +
              'padding:2px 9px 2px 3px;border-radius:16px;' +
              'border:1px solid rgba(88,166,255,.2);background:rgba(88,166,255,.07);' +
              'font-size:11px;white-space:nowrap;">' +
              '<div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;' +
                'background:#1f6feb;display:flex;align-items:center;justify-content:center;' +
                'font-size:9px;font-weight:700;color:#fff;">' + initials + '</div>' +
              '<span style="color:#e6edf3;font-weight:600;max-width:120px;overflow:hidden;' +
                'text-overflow:ellipsis;">' + _esc(userName) + '</span>' +
              '<span style="color:' + roleColor + ';font-size:10px;">' + _esc(userRole) + '</span>' +
            '</div>'
          : '') +

        /* Abmelden */
        '<button onclick="_yconnBarLogout()" style="' + btnBase +
          'background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);color:#f87171;">' +
          '⏻ ' + logoutLabel +
        '</button>' +

      '</div>';

    bar.innerHTML = leftHtml + rightHtml;
  }

  // ── Bar-Element erzeugen (position:fixed) ─────────────────────────────────
  function _createBar() {
    if (document.getElementById('yconn-cockpit-bar')) {
      _refreshBar();
      return;
    }

    var bar = document.createElement('div');
    bar.id = 'yconn-cockpit-bar';
    bar.style.cssText =
      'position:fixed;top:0;left:0;right:0;z-index:10000;' +
      'background:#0d1117;border-bottom:1px solid #21262d;' +
      'padding:0 16px;display:flex;align-items:center;justify-content:space-between;gap:8px;' +
      'font-family:-apple-system,"Segoe UI",Roboto,sans-serif;' +
      'box-sizing:border-box;height:' + BAR_HEIGHT + 'px;' +
      'box-shadow:0 2px 8px rgba(0,0,0,.4);';

    /* Spacer damit Seiteninhalt nicht unter der Bar verschwindet */
    var spacer = document.createElement('div');
    spacer.id = 'yconn-bar-spacer';
    spacer.style.cssText = 'height:' + BAR_HEIGHT + 'px;width:100%;flex-shrink:0;';

    document.body.insertBefore(bar, document.body.firstChild);
    document.body.insertBefore(spacer, bar.nextSibling);

    /* env-banner (falls vorhanden) direkt nach dem Spacer positionieren */
    var envBanner = document.getElementById('yconn-env-banner');
    if (envBanner) {
      envBanner.style.position = 'sticky';
      envBanner.style.top      = BAR_HEIGHT + 'px';
      envBanner.style.zIndex   = '9999';
    }

    _refreshBar();
  }

  /* localStorage-Änderungen aus anderen Tabs */
  window.addEventListener('storage', function (e) {
    if (e.key === SAP_KEY || e.key === 'yconn_user' || e.key === LANG_KEY) _refreshBar();
  });

  /* env-banner taucht oft nach dem Bar-Init auf (async) → nachjustieren */
  function _fixEnvBanner() {
    var envBanner = document.getElementById('yconn-env-banner');
    if (envBanner && !envBanner._barFixed) {
      envBanner._barFixed = true;
      envBanner.style.position = 'sticky';
      envBanner.style.top      = BAR_HEIGHT + 'px';
      envBanner.style.zIndex   = '9999';
    }
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _createBar);
  } else {
    _createBar();
  }
  setTimeout(_fixEnvBanner, 400);
  setTimeout(_fixEnvBanner, 1200);

})();
