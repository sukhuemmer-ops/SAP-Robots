/**
 * YCONN - Auth-Guard
 * Einbinden in jede geschuetzte Seite: <script src="auth.js"></script>
 *
 * Stellt bereit:
 *   AUTH.user                  - aktuell eingeloggter Benutzer (Objekt) oder null
 *   AUTH.logout()              - Session loeschen + zu login.html
 *   AUTH.renderHeader(id)      - Benutzer-Chip + GUI-BG-Toggle + Logout rendern
 *   AUTH.getGuiBg()            - true = Hintergrund, false = Vordergrund (localStorage)
 *   AUTH.setGuiBg(bool)        - Einstellung speichern + alle Chips aktualisieren
 *   AUTH.renderGuiBgToggle(id) - GUI-BG-Toggle-Chip in beliebiges Element rendern
 *   AUTH.requireRole(roles)    - Seite auf bestimmte Rollen beschraenken
 */
(function () {
  var KEY        = 'yconn_user';
  var LOGIN      = 'login.html';
  var GUI_BG_KEY = 'yconn_gui_bg';

  /* Benutzer */
  function getUser() {
    try {
      var raw = localStorage.getItem(KEY) || sessionStorage.getItem(KEY);
      return JSON.parse(raw);
    } catch (e) { return null; }
  }

  function logout() {
    localStorage.removeItem(KEY);
    sessionStorage.removeItem(KEY);
    location.replace(LOGIN);
  }

  var user = getUser();
  if (!user || !user.id) { location.replace(LOGIN); }

  /* GUI-Scripting: Hintergrund / Vordergrund */
  function getGuiBg() {
    var v = localStorage.getItem(GUI_BG_KEY);
    return v === null ? true : v === '1';
  }

  function setGuiBg(val) {
    var bg = !!val;
    localStorage.setItem(GUI_BG_KEY, bg ? '1' : '0');
    document.querySelectorAll('[data-gui-bg-toggle]').forEach(function(el) {
      _renderGuiBgChip(el, bg);
    });
  }

  function _renderGuiBgChip(el, bg) {
    el.innerHTML =
      '<label style="display:flex;align-items:center;gap:5px;font-size:11px;' +
      'color:#8b949e;cursor:pointer;user-select:none;white-space:nowrap;" ' +
      'title="SAP GUI Scripting: Hintergrund=Fenster unsichtbar / Vordergrund=Fenster sichtbar">' +
      '<input type="checkbox" ' + (bg ? 'checked' : '') + ' ' +
      'onchange="AUTH.setGuiBg(this.checked)" ' +
      'style="width:13px;height:13px;cursor:pointer;accent-color:#10b981;">' +
      '<span>' + (bg ? '🔇 Hintergrund' : '👁 Vordergrund') + '</span>' +
      '</label>';
  }

  function renderGuiBgToggle(containerId) {
    var el = document.getElementById(containerId);
    if (!el) return;
    el.setAttribute('data-gui-bg-toggle', '1');
    _renderGuiBgChip(el, getGuiBg());
  }

  /* Header */
  function renderHeader(containerId) {
    var el = document.getElementById(containerId);
    if (!el || !user) return;

    var initials = (user.display_name || '?')
      .split(' ').map(function(w){ return w[0]; }).join('').slice(0, 2).toUpperCase();

    var roleColor = user.role === 'Admin'
      ? '#f59e0b' : user.role === 'Readonly' ? '#8b949e' : '#10b981';

    var sys      = (user.sap_system || 'SEP').toUpperCase();
    var isSeq    = sys === 'SEQ';
    var sysBg    = isSeq ? 'rgba(16,185,129,.15)'  : 'rgba(245,158,11,.15)';
    var sysColor = isSeq ? '#10b981'                : '#f59e0b';

    var sapInfo = user.ashost
      ? 'SAP: ' + esc(user.ashost) + ' · Mdt. ' + esc(user.client || '600')
      : '';

    var guiBgId = 'auth_gui_bg_' + Math.random().toString(36).slice(2);

    el.insertAdjacentHTML('beforeend',
      '<div style="display:flex;align-items:center;gap:8px;margin-left:6px;">' +

        '<div id="' + guiBgId + '" data-gui-bg-toggle="1" ' +
          'style="padding:3px 9px;border-radius:999px;' +
                 'border:1px solid rgba(88,166,255,.15);' +
                 'background:rgba(88,166,255,.06);"></div>' +

        (sapInfo
          ? '<span style="background:rgba(31,111,235,.15);color:#79b8ff;' +
              'border:1px solid rgba(31,111,235,.3);border-radius:999px;' +
              'padding:3px 10px;font-size:11px;font-weight:600;white-space:nowrap;">' +
              sapInfo + '</span>'
          : '') +

        '<div style="display:flex;align-items:center;gap:7px;padding:4px 12px 4px 6px;' +
            'border-radius:20px;border:1px solid rgba(88,166,255,.2);' +
            'background:rgba(88,166,255,.08);font-size:12px;white-space:nowrap;">' +
          '<div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;' +
                      'background:#1f6feb;display:flex;align-items:center;' +
                      'justify-content:center;font-size:12px;font-weight:700;color:#fff;">' +
            initials + '</div>' +
          '<span style="color:#e6edf3;font-weight:600;">' + esc(user.display_name) + '</span>' +
          '<span style="color:' + roleColor + ';font-size:10px;">' + esc(user.role) + '</span>' +
          '<span style="background:' + sysBg + ';color:' + sysColor + ';border-radius:4px;' +
                       'padding:1px 6px;font-size:10px;font-weight:700;letter-spacing:.5px;">' +
            sys + '</span>' +
        '</div>' +

        '<button onclick="AUTH.logout()" ' +
          'style="padding:4px 10px;border-radius:6px;border:1px solid rgba(239,68,68,.2);' +
                 'background:rgba(239,68,68,.1);color:#ef4444;font-size:11px;font-weight:600;' +
                 'cursor:pointer;font-family:inherit;white-space:nowrap;" ' +
          'onmouseover="this.style.background=\'rgba(239,68,68,.2)\'" ' +
          'onmouseout="this.style.background=\'rgba(239,68,68,.1)\'" ' +
          'title="Abmelden">&#9211; Abmelden</button>' +

      '</div>'
    );

    setTimeout(function() {
      var chip = document.getElementById(guiBgId);
      if (chip) _renderGuiBgChip(chip, getGuiBg());
    }, 0);
  }

  /* Rollen-Guard */
  function requireRole(allowedRoles) {
    if (!user) return;
    if (user.role === 'Admin') return;
    var allowed = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    if (!allowed.includes(user.role)) {
      sessionStorage.setItem('yconn_access_denied',
        'Kein Zugriff: Seite ist nur fuer ' + allowed.join(', ') + ' freigegeben.');
      location.replace('startseite.html');
    }
  }

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;')
                          .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  /* Exports */
  window.AUTH = {
    user: user,
    logout: logout,
    renderHeader: renderHeader,
    requireRole: requireRole,
    getGuiBg: getGuiBg,
    setGuiBg: setGuiBg,
    renderGuiBgToggle: renderGuiBgToggle,
    get guiBg() { return getGuiBg(); }
  };
})();
