/**
 * YCONN – Auth-Guard
 * Einbinden in jede geschützte Seite:
 *   <script src="auth.js"></script>
 *
 * Stellt bereit:
 *   AUTH.user   – aktuell eingeloggter Benutzer (Objekt) oder null
 *   AUTH.logout() – Session löschen + zu login.html
 *   AUTH.renderHeader(containerId) – Benutzer-Chip + Logout in Element rendern
 */
(function () {
  const KEY      = 'yconn_user';
  const LOGIN    = 'login.html';

  function getUser() {
    try {
      // localStorage zuerst (tab-übergreifend), sessionStorage als Fallback
      const raw = localStorage.getItem(KEY) || sessionStorage.getItem(KEY);
      return JSON.parse(raw);
    } catch { return null; }
  }

  function logout() {
    localStorage.removeItem(KEY);
    sessionStorage.removeItem(KEY);
    location.replace(LOGIN);
  }

  // Guard: sofort weiterleiten wenn nicht eingeloggt
  const user = getUser();
  if (!user || !user.id) {
    location.replace(LOGIN);
  }

  /**
   * App-Regel G-9: Globaler Header – Benutzer + SAP-System (SEP/SEQ) + Abmelden.
   * Gilt für alle Cockpit-Seiten (cockpit.html, cockpit-v2.html, zinsen.html, …).
   * Zeigt: SAP-Server-Info · Benutzer-Chip (Avatar + Name + Rolle + SEP/SEQ-Badge) · Abmelden
   */
  function renderHeader(containerId) {
    const el = document.getElementById(containerId);
    if (!el || !user) return;

    const initials = (user.display_name || '?')
      .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();

    const roleColor = user.role === 'Admin'
      ? '#f59e0b' : user.role === 'Readonly' ? '#8b949e' : '#10b981';

    // SAP-System: SEP = amber, SEQ = grün
    const sys = (user.sap_system || 'SEP').toUpperCase();
    const isSeq = sys === 'SEQ';
    const sysBg    = isSeq ? 'rgba(16,185,129,.15)'   : 'rgba(245,158,11,.15)';
    const sysColor = isSeq ? '#10b981'                 : '#f59e0b';

    // SAP-Server-Info (ashost + client)
    const sapInfo = user.ashost
      ? `SAP: ${esc(user.ashost)} · Mdt. ${esc(user.client || '600')}`
      : '';

    el.insertAdjacentHTML('beforeend', `
      <div style="display:flex;align-items:center;gap:8px;margin-left:6px;">
        ${sapInfo ? `<span style="background:rgba(31,111,235,.15);color:#79b8ff;
          border:1px solid rgba(31,111,235,.3);border-radius:999px;
          padding:3px 10px;font-size:11px;font-weight:600;white-space:nowrap;">${sapInfo}</span>` : ''}
        <div style="display:flex;align-items:center;gap:7px;padding:4px 12px 4px 6px;
                    border-radius:20px;border:1px solid rgba(88,166,255,.2);
                    background:rgba(88,166,255,.08);font-size:12px;white-space:nowrap;">
          <div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;
                      background:#1f6feb;display:flex;align-items:center;
                      justify-content:center;font-size:12px;font-weight:700;color:#fff;">${initials}</div>
          <span style="color:#e6edf3;font-weight:600;">${esc(user.display_name)}</span>
          <span style="color:${roleColor};font-size:10px;">${esc(user.role)}</span>
          <span style="background:${sysBg};color:${sysColor};border-radius:4px;
                       padding:1px 6px;font-size:10px;font-weight:700;letter-spacing:.5px;">${sys}</span>
        </div>
        <button onclick="AUTH.logout()"
          style="padding:4px 10px;border-radius:6px;border:1px solid rgba(239,68,68,.2);
                 background:rgba(239,68,68,.1);color:#ef4444;font-size:11px;font-weight:600;
                 cursor:pointer;font-family:inherit;white-space:nowrap;"
          onmouseover="this.style.background='rgba(239,68,68,.2)'"
          onmouseout="this.style.background='rgba(239,68,68,.1)'"
          title="Abmelden">⏻ Abmelden</button>
      </div>
    `);
  }

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;')
                          .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  /**
   * requireRole(allowedRoles)
   * Seite nur für bestimmte Rollen freigeben.
   * Admin hat immer Zugriff, egal welche Rollen angegeben sind.
   * Bei fehlendem Zugriff → Weiterleitung zu startseite.html mit Hinweis.
   *
   * Beispiel in benutzer.html:
   *   AUTH.requireRole(['Admin']);
   */
  function requireRole(allowedRoles) {
    if (!user) return; // Guard oben hat schon weitergeleitet
    if (user.role === 'Admin') return; // Admin kommt immer durch
    const allowed = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    if (!allowed.includes(user.role)) {
      // Hinweis in sessionStorage, damit Startseite ihn anzeigen kann
      sessionStorage.setItem('yconn_access_denied',
        `Kein Zugriff: Seite ist nur für ${allowed.join(', ')} freigegeben.`);
      location.replace('startseite.html');
    }
  }

  window.AUTH = { user, logout, renderHeader, requireRole };
})();
