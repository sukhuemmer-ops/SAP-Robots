"""
SAP GUI Scripting -- SD-Rechnungserstellung (VA01) -- Modul "Rechnungserstellung"
===================================================================================
Vollstaendige Python-Portierung des VBA-Moduls create_Invoice aus der Datei
Create_invoice__SAP_New2026.xlsm (CATENSYS-spezifisch, Passwort: Boumerdes).

VBA-Module im Original:
    MS_Invoices        - Haupt-Ablaufsteuerung, liest Control-Sheet
    SAP_Connection     - SAP-GUI-Verbindungsaufbau
    DatenAuslesenSAP   - Daten aus SAP lesen
    create_Invoice     - VA01-Erfassung (hier vollstaendig portiert)

Einstiegspunkte:
    parse_control_sheet(filepath)
        Liest Control-Sheet aus Excel, gibt Liste von Zeilen-Dicts zurueck.

    record_invoice_from_control_sheet(session, rows, tracer=None)
        Verarbeitet alle Zeilen aus parse_control_sheet() sequenziell.
        Jede Zeile = ein VA01-Aufruf. Gibt Gesamtergebnis-Liste zurueck.

    record_invoice_multi(session, payload, tracer=None)
        Erstellt einen VA01-Verkaufsauftrag (beliebig viele Positionen).
        Kann direkt aus rechnung.html / handlers.py aufgerufen werden.

    record_invoice(session, payload)
        Legacy-Wrapper fuer Single-Item-Aufrufe.

Control-Sheet-Spalten (VBA-Referenz):
    A  Kunden-Nr         -> customer (Sold-To = Ship-To)
    B  Name              -> info only
    C  Datum (MM/YYYY)   -> letzter Tag des Monats als Lieferdatum + Preisdatum
    D  Buchungstext      -> ARKTX (Positionstext) + BSTKD (Bestellkopf)
    E  Betrag            -> PR00-Konditionswert (KBETR)
    F  Leistungsart      -> bestimmt KTGRM (Z4/ZM/ZT/Z1)
    G  Waehrung          -> WAERK
    H  PayTerm           -> ZTERM (Zahlungsbedingung)
    I  MWSt              -> TAXM1 (0 = steuerfrei / >0 = steuerpflichtig)
    J  Invoice Nr.       -> Ausgabe: angelegte VA01-Belegnummer
    K  Status            -> "ready created" / "Re. geschrieben" -> ueberspringen

Config-Sheet-Konstanten (aus Tabelle3 / Sheet3):
    SAP Transaktion : VA01
    Auftragsart     : ZTA   (negativ: ZG2)
    VKOrg           : C060
    Vertriebsweg    : 10
    Sparte          : 10
    Material Nr.    : 000000000000000013

Leistungsart-Mapping (Config-Sheet):
    SPI / Management-Service / Simulation / Cost-Allocation -> Z2  (Performances, GL 502050)
    Rental    -> ZM
    Tooling   -> ZT
    Trading-Good -> Z1

VBA-Hardcodes (1:1 portiert):
    BSTKD   = "Service Level Agreement"
    INCO1   = "FCA"
    INCO2   = "Germany"
    AUGRU   = "Z06"
    KDMAT   = "STT 25 0205 PartNo 900016200000010"
    Menge   = 1
    Einheit = "PC"  (EN, nicht "St" DE)
    WERKS   = C060  (nicht 0435)
    KTGRD:  Z3 fuer IC-Kunden (103xxxx) / Z2 Ausland
"""
from __future__ import annotations

import calendar
import contextlib
import ctypes
import logging
import os
import re
import threading
import time
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

log = logging.getLogger("gui.sd_invoice")

# ---------------------------------------------------------------------------
# Windows-Druckdialog automatisch schließen
# ---------------------------------------------------------------------------
def _close_windows_print_dialog(timeout: float = 15.0) -> None:
    """
    Läuft im Background-Thread; schließt das Windows-Druckdialog-Fenster.
    Methode: ctypes FindWindowW + WM_CLOSE (kein PowerShell, kein win32gui nötig).
    Sucht nach Fenstertiteln 'Drucken' (DE) und 'Print' (EN).
    """
    try:
        user32   = ctypes.WinDLL('user32', use_last_error=True)
        WM_CLOSE = 0x0010
        TITLES   = ["Drucken", "Print"]
        deadline = time.time() + timeout

        while time.time() < deadline:
            for title in TITLES:
                hwnd = user32.FindWindowW(None, title)
                if hwnd:
                    # Kurz warten bis Dialog vollständig gerendert ist
                    time.sleep(0.4)
                    user32.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
                    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                    log.info(
                        "BILL: Windows-Druckdialog '%s' per WM_CLOSE geschlossen (hwnd=%d)",
                        title, hwnd,
                    )
                    return
            time.sleep(0.15)

        log.warning("BILL: Windows-Druckdialog nach %.1fs nicht gefunden", timeout)

    except Exception as exc:
        log.warning("BILL: _close_windows_print_dialog Fehler: %s", exc)


# ---------------------------------------------------------------------------
# Konstanten (aus VBA / Config-Sheet)
# ---------------------------------------------------------------------------
DEFAULT_DOC_TYPE  = "ZTA"
DEFAULT_SALES_ORG = "C060"
DEFAULT_DISTR_CHN = "10"
DEFAULT_DIVISION  = "10"
DEFAULT_PLANT     = "C060"
DEFAULT_MATERIAL  = "000000000000000013"
BSTKD_TEXT        = "Service Level Agreement"
INCO1             = "FCA"
INCO2             = "Germany"
AUGRU             = "Z06"
UNIT              = "PC"
KDMAT             = "STT 25 0205 PartNo 900016200000010"
SKIP_STATUS       = {"ready created", "re. geschrieben", "re.geschrieben"}

KTGRM_MAP: dict[str, str] = {
    "SPI":                "Z2",   # Performances → GL 502050
    "Management-Service": "Z2",
    "Management Service": "Z2",
    "Simulation":         "Z2",
    "Cost-Allocation":    "Z2",
    "Rental":             "ZM",
    "Tooling":            "ZT",
    "Trading-Good":       "Z1",
}

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _last_day_of_month(mm_yyyy: str) -> str:
    """
    Konvertiert "MM/YYYY" in den letzten Tag des Monats im SAP-Format DD.MM.YYYY.
    Beispiel: "06/2023" -> "30.06.2023"
    """
    s = (mm_yyyy or "").strip()
    m = re.match(r"^(\d{1,2})[/\-](\d{4})$", s)
    if m:
        month, year = int(m.group(1)), int(m.group(2))
    else:
        m2 = re.match(r"^(\d{4})(\d{2})$", s)
        if m2:
            year, month = int(m2.group(1)), int(m2.group(2))
        else:
            return datetime.now().strftime("%d.%m.%Y")
    last_day = calendar.monthrange(year, month)[1]
    return f"{last_day:02d}.{month:02d}.{year:04d}"


def _fmt_de_date(yyyymmdd: str) -> str:
    """20260520 -> 20.05.2026 (Legacy-Kompatibilitaet)."""
    if not yyyymmdd:
        return datetime.now().strftime("%d.%m.%Y")
    s = str(yyyymmdd).replace("-", "").replace(".", "").replace("/", "")
    if len(s) == 8:
        return f"{s[6:8]}.{s[4:6]}.{s[0:4]}"
    return s


def _bar_text(session) -> str:
    """Liest SAP-Statusleiste wnd[0]/sbar."""
    try:
        return session.findById("wnd[0]/sbar").text or ""
    except Exception:
        return ""


def _sfind(session, eid: str):
    """findById mit sprechendem Fehlertext."""
    try:
        return session.findById(eid)
    except Exception as exc:
        raise RuntimeError(
            f"SAP-Element nicht gefunden: {eid!r}  |  {exc}"
        ) from exc


def _dismiss_popups(session, max_rounds: int = 10) -> None:
    """Schliesst Hinweis- / Datum- / Sicherheitsfrage-Popups."""
    past_triggers = (
        "liegt in der Vergangenheit",
        "is in the past",
        "Date is in the past",
        "Bitte Datum",
    )
    for _ in range(max_rounds):
        msg = _bar_text(session)
        if any(t in msg for t in past_triggers):
            session.findById("wnd[0]").sendVKey(0)
            time.sleep(0.2)
            continue
        try:
            session.findById("wnd[1]")
            session.findById("wnd[1]").sendVKey(0)
            time.sleep(0.2)
        except Exception:
            break


def _create_billing_and_export_pdf(session, sales_order: str,
                                    pdf_dir: str = r"C:\WF\sap-robots\invoices") -> tuple:
    """
    VA02 → menu[9] (Drucken) → btn[11] (Bestätigen) → tbar[1]/btn[35] (Belege anzeigen)
    → GOS-Toolbox → Anhänge → Export (wnd[2]/tbar[0]/btn[11]).
    VBA-Recording: 2x btn[3] → va02 → 2x Enter → menu[9] → btn[11]
                   → tbar[1]/btn[35] → Enter → GOS → Export → btn[11] → Close → btn[3] → btn[15]
    Gibt (invoice_nr, pdf_path) zurück.
    """
    os.makedirs(pdf_dir, exist_ok=True)
    invoice_nr = ""
    pdf_path   = ""

    try:
        # ── Schritt 1: VA02 mit Auftragsnummer aufrufen ────────────────────
        log.info("BILL: Navigiere zu /nVA02 %s", sales_order)
        session.findById("wnd[0]/tbar[0]/okcd").text = f"/nVA02 {sales_order}"
        session.findById("wnd[0]").sendVKey(0)
        time.sleep(0.8)
        _dismiss_popups(session)
        # Zweites Enter wie im VBA-Recording
        session.findById("wnd[0]").sendVKey(0)
        time.sleep(0.8)
        _dismiss_popups(session)
        try:
            log.info("BILL: VA02 Screen: '%s' | Bar='%s'",
                     session.findById("wnd[0]/titl").text or "",
                     _bar_text(session))
        except Exception:
            pass

        # ── Schritt 2: menu[9] = Drucken (erzeugt Faktura) ────────────────
        log.info("BILL: menu[0]/menu[9] (Drucken)")
        session.findById("wnd[0]/mbar/menu[0]/menu[9]").select()
        time.sleep(0.8)
        try:
            log.info("BILL: nach menu[9]: '%s' | Bar='%s'",
                     session.findById("wnd[0]/titl").text or "",
                     _bar_text(session))
        except Exception:
            pass

        # ── Schritt 3: btn[11] = Druckdialog bestätigen ───────────────────
        # Vor dem Klick einen Thread starten, der den Windows-Druckdialog automatisch schließt
        threading.Thread(target=_close_windows_print_dialog, args=(10.0,), daemon=True).start()
        log.info("BILL: btn[11] (Druckdialog OK)")
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        time.sleep(1.5)
        _dismiss_popups(session)

        # Status-Bar polling für Faktura-Nr
        for _p in range(12):
            time.sleep(0.2)
            msg = _bar_text(session)
            if msg:
                log.info("BILL: Poll %02d Bar='%s'", _p, msg)
            m = re.search(r"(\d{8,10})", msg)
            if m:
                invoice_nr = m.group(1)
                break
        log.info("BILL: Faktura nach btn[11]: %s", invoice_nr or "(leer)")
        try:
            log.info("BILL: Screen nach btn[11]: '%s'",
                     session.findById("wnd[0]/titl").text or "")
        except Exception:
            pass

        # ── Schritt 4: tbar[1]/btn[35] = Belege anzeigen ─────────────────
        log.info("BILL: tbar[1]/btn[35] (Belege anzeigen)")
        try:
            session.findById("wnd[0]/tbar[1]/btn[35]").press()
            time.sleep(0.6)
            session.findById("wnd[0]").sendVKey(0)   # Enter
            time.sleep(0.8)
            try:
                log.info("BILL: Screen Belege: '%s'",
                         session.findById("wnd[0]/titl").text or "")
            except Exception:
                pass
        except Exception as e:
            log.warning("BILL: tbar[1]/btn[35] fehlgeschlagen: %s", e)

        # Faktura-Nr aus Tabelle lesen (falls Status-Bar leer)
        if not invoice_nr:
            for col_idx in range(5):
                try:
                    tbl  = "wnd[0]/usr/tblSAPMV60ATCTRL_UEB_FAKT"
                    cell = session.findById(
                        f"{tbl}/txtVBFA-VBELN[{col_idx},0]").text or ""
                    m2 = re.search(r"(\d{8,10})", cell)
                    if m2:
                        invoice_nr = m2.group(1)
                        log.info("BILL: Faktura aus Tabelle col %d: %s", col_idx, invoice_nr)
                        break
                except Exception:
                    pass

        # ── Schritt 5: GOS-Toolbox → Anhänge → Export ────────────────────
        # Zweimal versuchen wie im VBA-Recording
        for attempt in range(2):
            try:
                session.findById("wnd[0]/titl/shellcont/shell").pressContextButton(
                    "%GOS_TOOLBOX")
                time.sleep(0.4)
                log.info("BILL: GOS_TOOLBOX Versuch %d OK", attempt + 1)
            except Exception as e:
                log.warning("BILL: GOS_TOOLBOX Versuch %d: %s", attempt + 1, e)

        session.findById("wnd[0]/titl/shellcont/shell").selectContextMenuItem(
            "%GOS_VIEW_ATTA")
        time.sleep(0.8)

        atta = "wnd[1]/usr/cntlCONTAINER_0100/shellcont/shell"
        log.info("BILL: Anhang-Export: Zeile 0 / BITM_DESCR")
        session.findById(atta).setCurrentCell(0, "BITM_DESCR")
        session.findById(atta).selectedRows = "0"
        session.findById(atta).pressToolbarButton("%ATTA_EXPORT")
        time.sleep(0.6)

        # ── Schritt 6: wnd[2] Export-Dialog ──────────────────────────────
        pdf_filename = f"Invoice_{invoice_nr or sales_order}.pdf"
        pdf_path     = os.path.join(pdf_dir, pdf_filename)
        pdf_dir_sap  = pdf_dir.rstrip("\\") + "\\"
        log.info("BILL: DY_PATH='%s' DY_FILENAME='%s'", pdf_dir_sap, pdf_filename)
        try:
            session.findById("wnd[2]/usr/ctxtDY_PATH").text = pdf_dir_sap
        except Exception as e:
            log.warning("BILL: DY_PATH nicht setzbar: %s", e)
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = pdf_filename
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = len(pdf_filename)
        # WICHTIG: btn[11] (nicht btn[0]!) laut VBA-Recording
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        time.sleep(0.8)
        log.info("BILL: Export-Dialog btn[11] gedrueckt")

        # ── Schritt 7: Anhänge-Dialog schließen + zurück ─────────────────
        try:
            session.findById("wnd[1]").close()
            log.info("BILL: Anhänge-Dialog geschlossen")
        except Exception:
            pass
        time.sleep(0.3)

        # btn[3] = Exit, btn[15] = ggf. weiterer Schritt laut Recording
        session.findById("wnd[0]/tbar[0]/btn[3]").press()
        time.sleep(0.3)
        try:
            session.findById("wnd[0]/tbar[0]/btn[15]").press()
        except Exception:
            pass
        time.sleep(0.3)

        exists = os.path.exists(pdf_path)
        log.info("BILL: PDF vorhanden=%s | Pfad=%s", exists, pdf_path)
        return invoice_nr, (pdf_path if exists else "")

    except Exception as e:
        log.error("BILL: Billing+PDF fehlgeschlagen: %s", e)
        for _ in range(4):
            try:
                session.findById("wnd[0]").sendVKey(12)
                time.sleep(0.2)
            except Exception:
                break
        return invoice_nr, ""


def _safe_navigate_to(session, tcode: str, wait: float = 0.8) -> None:
    """Navigiert zu Transaktion; schliesst vorher offene Dialoge."""
    for _ in range(4):
        try:
            session.findById("wnd[1]")
            session.findById("wnd[1]").sendVKey(12)
        except Exception:
            break
    session.findById("wnd[0]/tbar[0]/okcd").text = f"/n{tcode}"
    session.findById("wnd[0]").sendVKey(0)
    time.sleep(wait)


def _find_pr00_row(session, kond_tbl: str, max_scan: int = 50) -> int:
    """
    Gibt Zeile fuer PR00 zurueck.
    Aufzeichnung: Zeile 15 (hardcoded als Primaer-Kandidat).
    Fallback: dynamische Suche mit hohem Miss-Limit (Schema hat viele
    Berechnungszeilen ohne ctxtKOMV-KSCHL Control).
    """
    PR00_PRIMARY = 15   # aus SAP-Aufzeichnung (25.06.2026)

    # Tabelle auf Anfang scrollen
    try:
        session.findById(kond_tbl).firstVisibleRow = 0
        time.sleep(0.1)
    except Exception:
        pass

    # Phase 1: PR00 bereits gesetzt?
    misses = 0
    for r in range(max_scan):
        try:
            el = session.findById(f"{kond_tbl}/ctxtKOMV-KSCHL[1,{r}]")
            misses = 0
            if (el.text or "").strip() == "PR00":
                log.debug("PR00 bereits in Zeile %d", r)
                return r
        except Exception:
            misses += 1
            if misses >= 20:
                break

    # Phase 2: Primaer-Zeile 15 probieren
    try:
        el = session.findById(f"{kond_tbl}/ctxtKOMV-KSCHL[1,{PR00_PRIMARY}]")
        kschl = (el.text or "").strip()
        if not kschl:
            el.text = "PR00"
            log.info("PR00: Primaer-Zeile %d gesetzt", PR00_PRIMARY)
            return PR00_PRIMARY
        elif kschl == "PR00":
            log.info("PR00: Primaer-Zeile %d bereits PR00", PR00_PRIMARY)
            return PR00_PRIMARY
    except Exception as e:
        log.warning("PR00: Primaer-Zeile %d nicht zugaenglich: %s", PR00_PRIMARY, e)

    # Phase 3: Erste beschreibbare leere Zeile (Schreib-Test), miss-tolerant
    misses = 0
    for r in range(max_scan):
        try:
            el = session.findById(f"{kond_tbl}/ctxtKOMV-KSCHL[1,{r}]")
            misses = 0
            if (el.text or "").strip():
                continue
            try:
                el.text = "PR00"
                log.info("PR00: Fallback beschreibbare Zeile %d", r)
                return r
            except Exception:
                log.debug("PR00: Zeile %d read-only", r)
        except Exception:
            misses += 1
            if misses >= 20:
                break

    raise RuntimeError("Konditionstabelle (T\\05): keine beschreibbare Zeile fuer PR00.")


# ---------------------------------------------------------------------------
# Parse Control-Sheet aus Excel-Datei
# ---------------------------------------------------------------------------

def parse_control_sheet(filepath: str) -> list[dict]:
    """
    Liest das Control-Sheet aus einer .xlsm/.xlsx-Datei (ohne Excel / ohne Passwort).
    Gibt eine Liste von Zeilen-Dicts zurueck (eine pro Datenzeile ab Zeile 5).
    """
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    with zipfile.ZipFile(filepath) as z:
        names = z.namelist()
        ss_xml = z.read("xl/sharedStrings.xml").decode("utf-8")
        sheet1_name = "xl/worksheets/sheet1.xml"
        if sheet1_name not in names:
            raise FileNotFoundError(f"{sheet1_name} nicht in {filepath}")
        sheet_xml = z.read(sheet1_name).decode("utf-8")

    ss_tree = ET.fromstring(ss_xml)
    shared: list[str] = []
    for si in ss_tree.findall(".//a:si", ns):
        parts = si.findall(".//a:t", ns)
        shared.append("".join(p.text or "" for p in parts))

    def _cell_val(c) -> str:
        t = c.get("t", "")
        v_el = c.find("a:v", ns)
        if v_el is None:
            return ""
        v = v_el.text or ""
        if t == "s":
            idx = int(v)
            return shared[idx] if idx < len(shared) else v
        return v

    def _col_letter(ref: str) -> str:
        return re.match(r"([A-Z]+)", ref).group(1) if ref else ""

    col_map = {
        "A": "customer", "B": "name",    "C": "datum",       "D": "buchungstext",
        "E": "betrag",   "F": "leistungsart", "G": "currency", "H": "zterm",
        "I": "mwst",     "J": "invoice_nr",   "K": "status",
    }

    tree = ET.fromstring(sheet_xml)
    rows_out: list[dict] = []

    for row_el in tree.findall(".//a:row", ns):
        rn = int(row_el.get("r", 0))
        if rn <= 4:
            continue
        row_dict: dict[str, Any] = {k: "" for k in col_map.values()}
        row_dict["row"] = rn

        for c in row_el.findall("a:c", ns):
            ref = c.get("r", "")
            col = _col_letter(ref)
            key = col_map.get(col)
            if key:
                row_dict[key] = _cell_val(c)

        if not row_dict["customer"]:
            continue

        try:
            row_dict["betrag"] = float(row_dict["betrag"]) if row_dict["betrag"] else 0.0
        except (ValueError, TypeError):
            row_dict["betrag"] = 0.0

        try:
            row_dict["mwst"] = int(float(row_dict["mwst"])) if row_dict["mwst"] else 0
        except (ValueError, TypeError):
            row_dict["mwst"] = 0

        if not row_dict["currency"]:
            row_dict["currency"] = "EUR"
        if not row_dict["zterm"]:
            row_dict["zterm"] = "0001"
        if not row_dict["leistungsart"]:
            row_dict["leistungsart"] = "Management-Service"

        status_lower = (row_dict["status"] or "").strip().lower()
        row_dict["skip"] = status_lower in SKIP_STATUS
        row_dict["posting_date"] = (
            _last_day_of_month(row_dict["datum"]) if row_dict["datum"]
            else datetime.now().strftime("%d.%m.%Y")
        )
        rows_out.append(row_dict)

    log.info(
        "Control-Sheet gelesen: %d Zeilen total, %d zu ueberspringen.",
        len(rows_out), sum(1 for r in rows_out if r["skip"]),
    )
    return rows_out


# ---------------------------------------------------------------------------
# StepTracer
# ---------------------------------------------------------------------------

class _StepTracer:
    """Zeichnet jeden Ausfuehrungsschritt auf."""

    def __init__(self, session):
        self.session = session
        self.steps: list[dict] = []
        self._nr = 0

    @contextlib.contextmanager
    def step(self, name: str):
        self._nr += 1
        entry: dict = {"nr": self._nr, "name": name, "status": "ok", "sap_msg": ""}
        self.steps.append(entry)
        try:
            yield entry
            entry["status"]  = "ok"
            entry["sap_msg"] = _bar_text(self.session)
            log.info("  [OK] %2d %s | %s", entry["nr"], name, entry["sap_msg"])
        except Exception as exc:
            entry["status"]  = "error"
            entry["error"]   = str(exc)
            entry["sap_msg"] = _bar_text(self.session)
            log.error("  [ERR] %2d %s | SAP: %s | %s",
                      entry["nr"], name, entry["sap_msg"], exc)
            raise


# ---------------------------------------------------------------------------
# Kernfunktion: record_invoice_multi (VBA-Portierung create_Invoice)
# ---------------------------------------------------------------------------

def record_invoice_multi(
    session,
    payload: dict,
    tracer: "_StepTracer | None" = None,
) -> dict:
    """
    Erstellt einen VA01-Verkaufsauftrag mit beliebig vielen Positionen.

    Pflicht: customer, items=[{buchungstext, betrag}, ...]
    """
    items = payload.get("items", [])
    if not items:
        raise RuntimeError("Keine Positionen (items) im Payload.")

    customer = str(payload.get("customer", "")).strip()
    if not customer:
        raise RuntimeError("Pflichtfeld 'customer' fehlt.")

    posting_date = payload.get("posting_date", "")
    if not posting_date:
        datum = payload.get("datum", "")
        posting_date = _last_day_of_month(datum) if datum else _fmt_de_date("")

    currency     = payload.get("currency",     "EUR")
    sales_org    = payload.get("sales_org",    DEFAULT_SALES_ORG)
    distr_chan   = payload.get("distr_chan",    DEFAULT_DISTR_CHN)
    division     = payload.get("division",     DEFAULT_DIVISION)
    material     = payload.get("material",     DEFAULT_MATERIAL)
    werks         = payload.get("plant",         DEFAULT_PLANT)
    item_category = payload.get("item_category", "ZTAD")
    leistungsart = (payload.get("leistungsart") or
                    payload.get("service_type", "Management-Service"))
    zterm        = payload.get("zterm",        "0001")
    mwst         = int(payload.get("mwst",     0) or 0)
    taxm1        = "0" if mwst == 0 else "1"

    total    = sum(float(p.get("betrag", 0) or 0) for p in items)
    doc_type = DEFAULT_DOC_TYPE if total >= 0 else "ZG2"

    ktgrm = KTGRM_MAP.get(leistungsart, "Z2")  # Default: Performances
    ktgrd = "Z3" if customer.startswith("103") else "Z2"

    log.info(
        "VA01 Start: Kd=%s Pos=%d DocType=%s Datum=%s KTGRD=%s KTGRM=%s "
        "Waehrung=%s ZTERM=%s TAXM1=%s",
        customer, len(items), doc_type, posting_date,
        ktgrd, ktgrm, currency, zterm, taxm1,
    )

    T = tracer or _StepTracer(session)

    HDR_SUB   = "wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4021"
    TAB_OV    = "wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01"
    HDR_FRAME = (f"{TAB_OV}/ssubSUBSCREEN_BODY:SAPMV45A:4400"
                 "/ssubHEADER_FRAME:SAPMV45A:4440")
    TBL       = (f"{TAB_OV}/ssubSUBSCREEN_BODY:SAPMV45A:4400"
                 "/subSUBSCREEN_TC:SAPMV45A:4900"
                 "/tblSAPMV45ATCTRL_U_ERF_AUFTRAG")
    KOND_TBL  = ("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\05"
                 "/ssubSUBSCREEN_BODY:SAPLV69A:6201"
                 "/tblSAPLV69ATCTRL_KONDITIONEN")

    # ------------------------------------------------------------------
    # S1: VA01 oeffnen
    # ------------------------------------------------------------------
    with T.step(f"S1: VA01 oeffnen (AuftArt={doc_type} / VKOrg={sales_org})"):
        session.findById("wnd[0]").maximize()
        _safe_navigate_to(session, "VA01", wait=1.0)
        try:
            session.findById("wnd[0]/usr/ctxtVBAK-AUART")
        except Exception:
            log.warning("VA01-Maske nicht sofort geladen - 2. Versuch.")
            _safe_navigate_to(session, "VA01", wait=1.5)
        _sfind(session, "wnd[0]/usr/ctxtVBAK-AUART").text = doc_type
        _sfind(session, "wnd[0]/usr/ctxtVBAK-VKORG").text = sales_org
        _sfind(session, "wnd[0]/usr/ctxtVBAK-VTWEG").text = distr_chan
        _sfind(session, "wnd[0]/usr/ctxtVBAK-SPART").text = division
        session.findById("wnd[0]").sendVKey(0)
        time.sleep(1.0)
        _dismiss_popups(session)

    # ------------------------------------------------------------------
    # S2: Auftraggeber + Warenempfaenger + BSTKD
    # ------------------------------------------------------------------
    with T.step(f"S2: Auftraggeber={customer} BSTKD='{BSTKD_TEXT}'"):
        _sfind(session,
               f"{HDR_SUB}/subPART-SUB:SAPMV45A:4701/ctxtKUAGV-KUNNR").text = customer
        _sfind(session,
               f"{HDR_SUB}/subPART-SUB:SAPMV45A:4701/ctxtKUWEV-KUNNR").text = customer
        try:
            _sfind(session, f"{HDR_SUB}/txtVBKD-BSTKD").text = BSTKD_TEXT
        except Exception as e:
            log.warning("BSTKD nicht setzbar: %s", e)

    # ------------------------------------------------------------------
    # S3: Kopfdaten (Datum, INCO, AUGRU, ZTERM)
    # ------------------------------------------------------------------
    with T.step(f"S3: Kopfdaten Datum={posting_date} INCO={INCO1}/{INCO2} AUGRU={AUGRU}"):
        session.findById(f"wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01").select()
        time.sleep(0.3)
        _sfind(session, f"{HDR_FRAME}/ctxtRV45A-KETDAT").text = posting_date
        _sfind(session, f"{HDR_FRAME}/ctxtVBKD-PRSDT").text  = posting_date
        _sfind(session, f"{HDR_FRAME}/ctxtVBKD-INCO1").text  = INCO1
        _sfind(session, f"{HDR_FRAME}/txtVBKD-INCO2").text   = INCO2
        _sfind(session, f"{HDR_FRAME}/cmbVBAK-AUGRU").key    = AUGRU
        try:
            _sfind(session, f"{HDR_FRAME}/ctxtVBKD-ZTERM").text = zterm
        except Exception as e:
            log.warning("ZTERM im Kopfrahmen nicht setzbar: %s", e)

    # ------------------------------------------------------------------
    # S4..S(3+N): Pro Position – VBA-getreuer Zyklus:
    #   a) Uebersichtszeile D fuellen (MABNR, KWMENG, VRKME, ARKTX[5], ETDAT[11])
    #   b) Goto-Header (menu[2/1/0]) → 5x Enter → KTGRD, AUDAT, WAERK → F5 zurueck
    #   c) F2 von MABNR → Item-Detail → WERKS, KTGRM, TAXM1, PR00 → F5 zurueck
    # Nach jedem Zyklus legt SAP Zeile D+1 automatisch an.
    # ------------------------------------------------------------------
    POAN_PATH = (f"{TAB_OV}/ssubSUBSCREEN_BODY:SAPMV45A:4400"
                 "/subSUBSCREEN_TC:SAPMV45A:4900"
                 "/subSUBSCREEN_BUTTONS:SAPMV45A:4050/btnBT_POAN")

    for idx, pos in enumerate(items):
        # D = sichtbare Tabellenzeile:
        #   idx=0 -> Zeile 0 (erste leere Zeile, immer vorhanden)
        #   idx=1 -> Zeile 1 (SAP legt sie nach idx=0-Zyklus automatisch an)
        #   idx>=2 -> POAN druecken, dann IMMER Zeile 1 befuellen
        D          = min(idx, 1)
        txt        = str(pos.get("buchungstext", "") or "")[:40]
        betrag     = round(abs(float(pos.get("betrag", 0) or 0)), 2)
        # SAP erwartet deutsches Zahlenformat (Punkt=Tausender, Komma=Dezimal)
        betrag_str = f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lbl        = f"Pos {idx + 1}/{len(items)}"

        with T.step(f"S{4 + idx}: {lbl} \'{txt[:20]}\' {betrag_str} {currency}"):
            log.info("VA01 %s D=%d betrag=%s", lbl, D, betrag_str)

            # --- a) Uebersichts-Tab aktivieren ---
            try:
                session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01").select()
                time.sleep(0.2)
            except Exception:
                pass

            # Ab Pos 3 (idx>=2): POAN druecken um neue Zeile zu erzeugen
            # Aufzeichnung: setFocus auf letzte befuellte Zeile (row 1),
            # dann POAN -> neue leere Zeile erscheint bei Row 1
            if idx >= 2:
                try:
                    prev = f"{TBL}/ctxtRV45A-MABNR[1,1]"
                    session.findById(prev).setFocus()
                    session.findById(prev).caretPosition = 6
                except Exception:
                    pass
                try:
                    session.findById(POAN_PATH).press()
                    time.sleep(0.4)
                    log.info("%s: POAN gedrueckt -> neue Uebersichtszeile D=1", lbl)
                except Exception as e:
                    log.warning("%s: POAN fehlgeschlagen: %s", lbl, e)

            # --- Uebersichtszeile D fuellen (Aufzeichnung-Reihenfolge) ---
            # Material (Pflichtfeld)
            _sfind(session, f"{TBL}/ctxtRV45A-MABNR[1,{D}]").text = material
            # Menge
            try:
                session.findById(f"{TBL}/txtRV45A-KWMENG[2,{D}]").text = "1"
            except Exception:
                pass
            # Einheit
            try:
                session.findById(f"{TBL}/ctxtVBAP-VRKME[3,{D}]").text = UNIT
            except Exception:
                pass
            # ARKTX Kurztext (Spalte 5)
            try:
                session.findById(f"{TBL}/txtVBAP-ARKTX[5,{D}]").text = txt
            except Exception:
                pass
            # Item-Kategorie PSTYV (Spalte 7) - aus Aufzeichnung
            try:
                session.findById(f"{TBL}/ctxtVBAP-PSTYV[7,{D}]").text = item_category
            except Exception:
                pass
            # Lieferdatum (Spalte 11)
            try:
                session.findById(f"{TBL}/ctxtRV45A-ETDAT[11,{D}]").text = posting_date
            except Exception:
                pass
            # WERKS direkt in Uebersicht (Spalte 12) - aus Aufzeichnung
            try:
                session.findById(f"{TBL}/ctxtVBAP-WERKS[12,{D}]").text = werks
            except Exception:
                pass

            # --- b) Goto Header: menu[2]/menu[1]/menu[0] ---
            # Die 5x Enter-Kaskade committed die Uebersichtszeile
            # und navigiert zum Header-Screen.
            session.findById("wnd[0]/mbar/menu[2]/menu[1]/menu[0]").select()
            for _ in range(5):
                session.findById("wnd[0]").sendVKey(0)
                time.sleep(0.15)
            _dismiss_popups(session)

            # Header-Tab T\04: KTGRD
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\04").select()
            sbar = _bar_text(session)
            if "vergangenheit" in sbar.lower() or "in the past" in sbar.lower():
                session.findById("wnd[0]").sendVKey(0)
            H4 = ("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\04"
                  "/ssubSUBSCREEN_BODY:SAPMV45A:4311")
            try:
                session.findById(f"{H4}/cmbVBKD-KTGRD").key = ktgrd
            except Exception as e:
                log.warning("%s: KTGRD nicht setzbar: %s", lbl, e)

            # Header-Tab T\01: AUDAT + WAERK
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\01").select()
            H1 = ("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\01"
                  "/ssubSUBSCREEN_BODY:SAPMV45A:4301")
            try:
                session.findById(f"{H1}/ctxtVBAK-AUDAT").text = posting_date
            except Exception:
                pass
            try:
                session.findById(f"{H1}/ctxtVBAK-WAERK").text = currency
            except Exception:
                pass

            # T\04 → Enter (Datumswarnung abfangen)
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\04").select()
            session.findById("wnd[0]").sendVKey(0)
            sbar = _bar_text(session)
            if "vergangenheit" in sbar.lower() or "in the past" in sbar.lower():
                session.findById("wnd[0]").sendVKey(0)

            # T\03 + T\02 anwaehlen (VBA: nur Select, kein Dateneintrag)
            try:
                session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\03").select()
            except Exception:
                pass
            try:
                session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\\02").select()
            except Exception:
                pass

            # F5 zurueck zur Uebersicht
            session.findById("wnd[0]/tbar[0]/btn[3]").press()
            time.sleep(0.4)
            _dismiss_popups(session)

            # --- c) F2 von MABNR → Positionsdetail ---
            try:
                session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_OVERVIEW/tabpT\\01").select()
            except Exception:
                pass
            mat_cell = f"{TBL}/ctxtRV45A-MABNR[1,{D}]"
            _sfind(session, mat_cell).setFocus()
            try:
                session.findById(mat_cell).caretPosition = 6
            except Exception:
                pass
            session.findById("wnd[0]").sendVKey(2)   # F2 = Positionsdetail
            time.sleep(0.8)
            _dismiss_popups(session)

            # Tab T\03: WERKS
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\03").select()
            T03 = ("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\03"
                   "/ssubSUBSCREEN_BODY:SAPMV45A:4452")
            _sfind(session, f"{T03}/ctxtVBAP-WERKS").text = werks

            # Tab T\04: KTGRM + TAXM1
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\04").select()
            T04 = ("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\04"
                   "/ssubSUBSCREEN_BODY:SAPMV45A:4453")
            try:
                session.findById(f"{T04}/cmbVBAP-KTGRM").key = ktgrm
            except Exception as e:
                log.warning("%s: KTGRM nicht setzbar: %s", lbl, e)
            try:
                session.findById(f"{T04}/ctxtVBAP-TAXM1").text = taxm1
            except Exception as e:
                log.warning("%s: TAXM1 nicht setzbar: %s", lbl, e)

            # Tab T\05: PR00-Kondition (Preis)
            # Ablauf aus SAP-Aufzeichnung (28.06.2026):
            #   1. btnBT_KOAN druecken  -> fuegt neue leere Konditionszeile ein
            #   2. Zeile 1 = neue beschreibbare Zeile fuer PR00
            #   3. setFocus auf KMEIN[6,1] + caretPosition=2 + Enter (statt KWERT)
            session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\05").select()
            time.sleep(0.6)
            _dismiss_popups(session)

            # KOAN-Button: "Neue Konditionszeile anlegen"
            T05_BASE = ("wnd[0]/usr/tabsTAXI_TABSTRIP_ITEM/tabpT\\05"
                        "/ssubSUBSCREEN_BODY:SAPLV69A:6201")
            KOAN_BTN = f"{T05_BASE}/subSUBSCREEN_PUSHBUTTONS:SAPLV69A:1000/btnBT_KOAN"
            try:
                session.findById(KOAN_BTN).press()
                time.sleep(0.4)
                log.info("%s: KOAN-Button gedrueckt -> neue Konditionszeile", lbl)
            except Exception as e:
                log.warning("%s: KOAN-Button nicht zugaenglich: %s", lbl, e)

            # Nach KOAN: PR00 in Zeile 1
            PR00_ROW = 1
            T.steps[-1]["pr00_row"] = PR00_ROW
            _sfind(session, f"{KOND_TBL}/ctxtKOMV-KSCHL[1,{PR00_ROW}]").text = "PR00"
            _sfind(session, f"{KOND_TBL}/txtKOMV-KBETR[3,{PR00_ROW}]").text = betrag_str
            try:
                session.findById(f"{KOND_TBL}/ctxtRV61A-KOEIN[4,{PR00_ROW}]").text = currency
            except Exception:
                pass
            try:
                session.findById(f"{KOND_TBL}/txtKOMV-KPEIN[5,{PR00_ROW}]").text = "1"
            except Exception:
                pass
            kmein = f"{KOND_TBL}/ctxtKOMV-KMEIN[6,{PR00_ROW}]"
            try:
                session.findById(kmein).text = UNIT
                session.findById(kmein).setFocus()
                session.findById(kmein).caretPosition = 2
            except Exception:
                pass
            session.findById("wnd[0]").sendVKey(0)
            time.sleep(0.4)
            _dismiss_popups(session)

            # F5 zurueck zur Uebersicht
            # (SAP legt Zeile D+1 automatisch an nach abgeschlossenem Zyklus)
            session.findById("wnd[0]/tbar[0]/btn[3]").press()
            time.sleep(0.4)
            _dismiss_popups(session)

    # ------------------------------------------------------------------
    # Sichern (F11) + Belegnummer lesen
    # ------------------------------------------------------------------
    s_save = 4 + len(items)
    sales_order = ""
    with T.step(f"S{s_save}: Sichern (F11) + Belegnummer lesen"):
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        time.sleep(1.5)
        msg   = _bar_text(session)
        match = re.search(r"(\d{5,10})", msg)
        sales_order = match.group(1) if match else ""
        if not sales_order:
            raise RuntimeError(
                f"Belegnummer nicht in SAP-Statusleiste. Meldung: {msg!r}"
            )
        log.info("VA01 erfolgreich: Auftrag %s angelegt.", sales_order)
        T.steps[-1]["sales_order"] = sales_order

    # ------------------------------------------------------------------
    # Faktura anlegen + PDF exportieren (VA02-Weg laut VBA-Recording)
    # Recording: VA02 {sales_order} -> menu[9] -> btn[11]
    #            -> tbar[1]/btn[35] -> GOS -> Export -> wnd[2]/tbar[0]/btn[11]
    # ------------------------------------------------------------------
    invoice_nr = ""
    pdf_path   = ""
    s_bill = s_save + 1
    with T.step(f"S{s_bill}: Faktura anlegen + PDF (Auftrag {sales_order})"):
        try:
            # Schritt 1: "Verkaufsbeleg" > "Faktura anlegen"
            session.findById("wnd[0]/mbar/menu[0]/menu[2]").select()
            time.sleep(0.6)
            _dismiss_popups(session)

            # VA02-Recording: menu[9] + btn[11] + tbar[1]/btn[35] + GOS-Export
            invoice_nr, pdf_path = _create_billing_and_export_pdf(
                session, sales_order)
            T.steps[-1]["invoice_nr"] = invoice_nr
            T.steps[-1]["pdf_path"]   = pdf_path

        except Exception as e:
            log.error("VF: Faktura/PDF fehlgeschlagen: %s", e)
            T.steps[-1]["error"] = str(e)

    return {
        "sales_order": sales_order,
        "invoice_nr":  invoice_nr,
        "pdf_path":    pdf_path,
        "message":     _bar_text(session),
        "steps":       T.steps,
    }


# ---------------------------------------------------------------------------
# Batch-Verarbeitung: Control-Sheet -> mehrere VA01-Aufrufe
# ---------------------------------------------------------------------------

def record_invoice_from_control_sheet(
    session,
    rows: list[dict],
    tracer: "_StepTracer | None" = None,
) -> list[dict]:
    """
    Verarbeitet alle Zeilen aus parse_control_sheet() sequenziell.
    Jede Zeile (nicht skip) -> ein VA01-Aufruf.
    """
    results: list[dict] = []

    for row in rows:
        base = {
            "row":          row["row"],
            "customer":     row["customer"],
            "buchungstext": row.get("buchungstext", ""),
            "skipped":      row.get("skip", False),
            "sales_order":  "",
            "error":        "",
            "steps":        [],
        }

        if row.get("skip"):
            base["sales_order"] = row.get("invoice_nr", "")
            log.info("Zeile %d uebersprungen (Status: %s).",
                     row["row"], row.get("status", ""))
            results.append(base)
            continue

        payload = {
            "customer":     row["customer"],
            "posting_date": row["posting_date"],
            "datum":        row.get("datum", ""),
            "currency":     row.get("currency", "EUR"),
            "leistungsart": row.get("leistungsart", "Management-Service"),
            "zterm":        row.get("zterm", "0001"),
            "mwst":         row.get("mwst", 0),
            "items": [{
                "buchungstext": row.get("buchungstext", ""),
                "betrag":       row.get("betrag", 0.0),
            }],
        }

        T = _StepTracer(session)
        try:
            result = record_invoice_multi(session, payload, tracer=T)
            base["sales_order"] = result["sales_order"]
            base["steps"]       = T.steps
            log.info("Zeile %d -> Auftrag %s (Kd=%s, %.2f %s)",
                     row["row"], result["sales_order"],
                     row["customer"], row.get("betrag", 0), row.get("currency", "EUR"))
        except Exception as exc:
            base["error"] = str(exc)
            base["steps"] = T.steps
            log.error("Zeile %d Fehler (Kd=%s): %s", row["row"], row["customer"], exc)

        results.append(base)

    ok   = sum(1 for r in results if r.get("sales_order") and not r.get("error"))
    skip = sum(1 for r in results if r.get("skipped"))
    err  = sum(1 for r in results if r.get("error"))
    log.info("Batch abgeschlossen: %d OK / %d uebersprungen / %d Fehler.", ok, skip, err)
    return results



# ---------------------------------------------------------------------------
# Legacy: Single-Item Wrapper
# ---------------------------------------------------------------------------

def record_invoice(session, payload: dict) -> str:
    """Wrapper fuer Single-Item-Aufrufe aus aelterem Code."""
    if "items" not in payload:
        payload = dict(payload)
        payload["items"] = [{
            "buchungstext": (payload.get("po_reference", "")
                             or payload.get("item_text", ""))[:40],
            "betrag":       payload.get("amount", 0),
        }]
    result = record_invoice_multi(session, payload)
    return (f"VA01: Auftrag {result['sales_order']} angelegt. "
            f"SAP: {result['message']}")
