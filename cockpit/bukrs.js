/**
 * bukrs.js — Zentrale Buchungskreis-Registry
 * Gültig für SEP (Produktion) und SEQ (Test)
 * Quelle der Wahrheit für alle YCONN Cockpit-Seiten.
 *
 * Einbinden: <script src="bukrs.js"></script>
 * Danach: YCONN.fillBukrsSelect('meinSelect', '0435');
 */

window.YCONN = window.YCONN || {};

/** Vollständige Buchungskreis-Liste (SEP & SEQ) */
YCONN.BUKRS = [
  { code: 'VV9',  name: 'Catensys Holding',  fullName: 'Catensys Holding GmbH' },
  { code: '0334', name: 'Catensys France',    fullName: 'Catensys France S.A.S.' },
  { code: '0435', name: 'Catensys Germany',   fullName: 'Catensys Germany GmbH' },
  { code: '0436', name: 'Catensys China',     fullName: 'Catensys China Co. Ltd.' },
  { code: '0437', name: 'Catensys Slovakia',  fullName: 'Catensys Slovakia s.r.o.' },
  { code: '0438', name: 'Catensys Korea',     fullName: 'Catensys Korea Co. Ltd.' },
  { code: '0439', name: 'Catensys India',     fullName: 'Catensys India Pvt. Ltd.' },
  { code: '0440', name: 'Catensys US',        fullName: 'Catensys US Inc.' },
  { code: '0441', name: 'Catensys Japan',     fullName: 'Catensys Japan K.K.' },
];

/**
 * SD-Rechnungsmodul: Werk- und VKOrg-Zuordnung je Buchungskreis.
 * Für Buchungskreise ohne eigene SD-Konfiguration (VV9, 0334) bitte
 * manuell im Formular anpassen.
 */
YCONN.BUKRS_PLANT = {
  '0435': { vkorg: 'C060', plant: 'C060' },
  '0436': { vkorg: 'C199', plant: 'C199' },
  '0437': { vkorg: 'C095', plant: 'C095' },
  '0438': { vkorg: 'C074', plant: 'C074' },
  '0439': { vkorg: 'C042', plant: 'C042' },
  '0440': { vkorg: 'C051', plant: 'C051' },
  '0441': { vkorg: '',     plant: ''     },  // Japan: Werk bitte manuell eintragen
  'VV9':  { vkorg: '',     plant: ''     },  // Holding: kein eigenes Werk
  '0334': { vkorg: '',     plant: ''     },  // France: Werk bitte manuell eintragen
};

/**
 * Füllt ein <select>-Element mit allen Buchungskreisen.
 *
 * @param {string|HTMLElement} idOrEl   Element-ID oder DOM-Element
 * @param {string}  [selected]          Vorausgewählter Code (Default: '0435')
 * @param {boolean} [addAllOption]      Erste Option "— Alle —" hinzufügen
 * @param {string[]}[only]              Nur diese Codes anzeigen (leer = alle)
 */
YCONN.fillBukrsSelect = function(idOrEl, selected, addAllOption, only) {
  var el = (typeof idOrEl === 'string') ? document.getElementById(idOrEl) : idOrEl;
  if (!el) return;
  var current = selected != null ? selected : (el.value || '0435');
  var list = only && only.length
    ? YCONN.BUKRS.filter(function(b) { return only.indexOf(b.code) !== -1; })
    : YCONN.BUKRS;
  var html = addAllOption ? '<option value="">— Alle Buchungskreise —</option>' : '';
  list.forEach(function(b) {
    html += '<option value="' + b.code + '"'
          + (b.code === current ? ' selected' : '') + '>'
          + b.code + ' — ' + b.name
          + '</option>';
  });
  el.innerHTML = html;
};

/**
 * Gibt den kurzen Namen eines Buchungskreis-Codes zurück.
 * @param {string} code
 * @returns {string}
 */
YCONN.getBukrsName = function(code) {
  var b = YCONN.BUKRS.find(function(x) { return x.code === code; });
  return b ? b.name : (code || '');
};

/**
 * Gibt den vollständigen Firmennamen zurück.
 * @param {string} code
 * @returns {string}
 */
YCONN.getBukrsFullName = function(code) {
  var b = YCONN.BUKRS.find(function(x) { return x.code === code; });
  return b ? b.fullName : (code || '');
};

/**
 * Auto-Init: füllt alle <select data-bukrs> Elemente beim Laden.
 * Optionale Attribute:
 *   data-bukrs-selected="0435"   — vorausgewählter Code
 *   data-bukrs-all="true"        — "Alle"-Option voranstellen
 */
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('select[data-bukrs]').forEach(function(sel) {
    var selected = sel.getAttribute('data-bukrs-selected') || sel.value || '0435';
    var addAll   = sel.getAttribute('data-bukrs-all') === 'true';
    YCONN.fillBukrsSelect(sel, selected, addAll);
  });
});
