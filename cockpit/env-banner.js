/**
 * YCONN Umgebungs-Banner
 * ======================
 * Zeigt oben im Cockpit einen farbigen Banner je nach aktiver Umgebung.
 * Wird von startseite.html und allen Cockpit-Seiten eingebunden.
 *
 * Bezieht die Umgebung von:
 *   1. GET http://localhost:8000/env   (Orchestrator, zuverlässigste Quelle)
 *   2. GET http://localhost:8765/env   (Bridge Fallback)
 *   3. localStorage 'yconn_env'        (letzter bekannter Wert)
 *   4. 'unknown'                       (kein Server erreichbar)
 */
(function () {
  var STYLES = {
    dev:     { bg: '#0f2a1a', border: '#2ea043', text: '#56d364', label: '🟢 ENTWICKLUNG',  sub: 'SAP SEQ · 172.28.189.11 · Quality Assurance' },
    test:    { bg: '#0c2860', border: '#388bfd', text: '#79b8ff', label: '🔵 TEST',          sub: 'SAP SEQ · 172.28.189.11 · Quality Assurance' },
    prod:    { bg: '#5a0000', border: '#f85149', text: '#ff7b72', label: '🔴 PRODUKTION',   sub: '⚠ SAP SEP · 172.28.189.8 · Echtes Produktivsystem' },
    unknown: { bg: '#161b22', border: '#30363d', text: '#8b949e', label: '⚪ UMGEBUNG UNBEKANNT', sub: 'Orchestrator nicht erreichbar' },
  };

  function createBanner(env) {
    var s = STYLES[env] || STYLES.unknown;
    var el = document.getElementById('yconn-env-banner');
    if (!el) {
      el = document.createElement('div');
      el.id = 'yconn-env-banner';
      document.body.prepend(el);
    }
    el.style.cssText =
      'position:sticky;top:0;z-index:9999;width:100%;' +
      'background:' + s.bg + ';border-bottom:1px solid ' + s.border + ';' +
      'padding:4px 16px;display:flex;align-items:center;gap:10px;font-size:11px;' +
      'font-family:-apple-system,"Segoe UI",sans-serif;';
    el.innerHTML =
      '<strong style="color:' + s.text + ';font-size:12px">' + s.label + '</strong>' +
      '<span style="color:' + s.border + '">|</span>' +
      '<span style="color:' + s.text + ';opacity:.8">' + s.sub + '</span>' +
      (env === 'prod'
        ? '<span style="margin-left:auto;background:#f85149;color:#fff;border-radius:4px;padding:1px 7px;font-size:10px;font-weight:700">PROD</span>'
        : '');

    // Persistieren für Fallback
    try { localStorage.setItem('yconn_env', env); } catch(_) {}
  }

  async function fetchEnv() {
    // Versuche Orchestrator
    try {
      var r = await fetch('http://localhost:8000/env', { signal: AbortSignal.timeout(2000) });
      var d = await r.json();
      if (d.env) return d.env;
    } catch(_) {}

    // Versuche Bridge
    try {
      var r2 = await fetch('http://localhost:8765/env', { signal: AbortSignal.timeout(2000) });
      var d2 = await r2.json();
      if (d2.env) return d2.env;
    } catch(_) {}

    // localStorage Fallback
    try {
      var cached = localStorage.getItem('yconn_env');
      if (cached) return cached;
    } catch(_) {}

    return 'unknown';
  }

  // Sofort mit gecachtem Wert anzeigen, dann aktualisieren
  try {
    var cached = localStorage.getItem('yconn_env') || 'unknown';
    createBanner(cached);
  } catch(_) {
    createBanner('unknown');
  }

  fetchEnv().then(function(env) {
    createBanner(env);
  });
})();
