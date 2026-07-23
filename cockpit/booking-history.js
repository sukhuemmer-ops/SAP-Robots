// booking-history.js — Globale Buchungshistorie (YCONN)
// ──────────────────────────────────────────────────────
// Dieses Skript in alle Module einbinden, die SAP-Buchungen durchführen:
//   <script src="booking-history.js"></script>
// Voraussetzung: window._ORCH muss gesetzt sein (wird zur Laufzeit gelesen).
// ──────────────────────────────────────────────────────
(function () {
  'use strict';

  var MODULE_LABELS = {
    zinsen:          '💰 Zinsen',
    payroll:         '👥 PayRoll',
    reisekosten:     '🚗 Reisekosten',
    'ust-firmenwagen':'🚙 USt-Firmenwagen',
    rechnung:        '🧾 Rechnung',
    afa:             '📉 Afa-Lauf',
    rueckstellung:   '📦 Rückstellung',
  };

  function _orch() {
    return window._ORCH || (window.location.origin + ':8000');
  }

  function _user() {
    try {
      var u = window.AUTH && AUTH.user;
      return (u && (u.username || u.sap_username)) || 'unknown';
    } catch (_) { return 'unknown'; }
  }

  // Öffentliche Funktion: wird von allen Modulen nach erfolgreicher Buchung aufgerufen
  window.saveGlobalBooking = function (entry) {
    if (!entry || !entry.module) { console.warn('[GlobalBookingHistory] module fehlt'); return; }

    var now    = new Date();
    var isoNow = now.toISOString();

    // Datum normalisieren: DD.MM.YYYY → YYYY-MM-DD
    var rawDate = entry.doc_date || entry.date || isoNow.slice(0, 10);
    var docDate = rawDate;
    if (/^\d{2}\.\d{2}\.\d{4}$/.test(rawDate)) {
      var p = rawDate.split('.');
      docDate = p[2] + '-' + p[1] + '-' + p[0];
    }

    var yr     = entry.yr     || docDate.slice(0, 4);
    var period = entry.period || String(parseInt(docDate.slice(5, 7), 10));

    var payload = {
      module:      entry.module,
      bukrs:       entry.bukrs       || '',
      sap_system:  entry.sap_system  || entry.system || '',
      doc_date:    docDate,
      yr:          yr,
      period:      period,
      belnr:       entry.belnr       || entry.docNr  || entry.docNrDisplay || '',
      obj_key:     entry.obj_key     || entry.docNr  || '',
      ref_doc_no:  entry.ref_doc_no  || '',
      header_txt:  entry.header_txt  || '',
      amount:      parseFloat(entry.amount) || 0,
      currency:    entry.currency    || 'EUR',
      description: entry.description || entry.text || '',
      booked_by:   entry.booked_by   || _user(),
      booked_at:   entry.booked_at   || isoNow,
      status:      entry.status      || 'booked',
      source:      entry.source      || 'app',
    };

    // DB speichern (fire-and-forget)
    fetch(_orch() + '/booking-history', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    }).then(function (r) {
      if (!r.ok) r.text().then(function (t) { console.warn('[GlobalBookingHistory] Server-Fehler:', t); });
    }).catch(function (e) {
      console.warn('[GlobalBookingHistory] Netzwerk-Fehler:', e.message);
    });

    // Auch localStorage aktualisieren (Kompatibilität mit cockpit.html)
    try {
      var KEY  = 'yconn_booking_history';
      var hist = [];
      try { hist = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (_) {}
      hist.unshift({
        id:        'g' + Date.now(),
        ts:        isoNow,
        yr:        yr,
        mi:        parseInt(period, 10) - 1,
        monthName: ['Januar','Februar','März','April','Mai','Juni',
                    'Juli','August','September','Oktober','November','Dezember'][parseInt(period,10)-1] || period,
        nr:        payload.ref_doc_no || '',
        bukrs:     payload.bukrs,
        cocode:    payload.bukrs,
        company:   '',
        account:   '',
        offset:    '',
        dtyp:      'SA',
        curr:      payload.currency,
        amount:    payload.amount,
        docNr:     payload.belnr,
        system:    payload.sap_system,
        status:    payload.status === 'booked' ? 'ok' : payload.status,
        source:    payload.module,   // Modul als Quelle
        user:      payload.booked_by,
        text:      payload.description,
        module:    payload.module,
        storno:    '',
      });
      // Limit 2000 Einträge
      if (hist.length > 2000) hist = hist.slice(0, 2000);
      localStorage.setItem(KEY, JSON.stringify(hist));
    } catch (e) {
      console.warn('[GlobalBookingHistory] localStorage-Fehler:', e.message);
    }
  };

  // Für cockpit.html: Lädt Buchungshistorie aus DB (Promise → Array)
  window.loadGlobalBookingHistory = function (filters) {
    filters = filters || {};
    var qs = Object.keys(filters)
      .filter(function (k) { return filters[k]; })
      .map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(filters[k]); })
      .join('&');
    return fetch(_orch() + '/booking-history' + (qs ? '?' + qs : ''))
      .then(function (r) { return r.ok ? r.json() : []; })
      .catch(function () { return []; });
  };

  window.BOOKING_MODULE_LABELS = MODULE_LABELS;

})();
