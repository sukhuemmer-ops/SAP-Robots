"""
Cockpit-Bridge
==============
Schlanker HTTP-Server, der zwischen Cockpit (Browser) und Worker-Handlern vermittelt.

Architektur:
    Cockpit (Browser)
       | fetch http://localhost:8765
       v
    bridge.py (dieses Skript)
       | direktcall
       v
    handlers.py (BAPI/GUI/Batch-Calls)
       | pyrfc / pywin32
       v
    SAP

Endpoints:
    GET  /health                Lebenszeichen + Liste der Handler
    POST /run                   Aufgabe ausfuehren (Body: { method, tcode, payload })
    POST /test_rfc              SAP-Verbindung testen (RFC_PING)
    GET  /reports               Liste der erzeugten Reports
    GET  /reports/<name>        Report herunterladen

Start:
    python bridge.py
oder:
    Bridge starten.bat (Doppelklick)
"""
from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# .env laden (vor Import von handlers, damit Env-Werte da sind)
here = Path(__file__).resolve().parent

# .env laden – direkt über os.environ setzen damit Windows-Systemvariablen
# IMMER überschrieben werden (override=True reicht bei manchen dotenv-Versionen nicht)
def _load_env_force(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key:
                    os.environ[key] = val
    except Exception:
        pass

for _cand in (here / ".env", here / ".env.example"):
    if _cand.exists():
        _load_env_force(_cand)
        break

# Auch dotenv versuchen (für Kompatibilität)
try:
    from dotenv import load_dotenv
    for _cand in (here / ".env", here / ".env.example"):
        if _cand.exists():
            load_dotenv(_cand, override=True)
            break
except ImportError:
    pass

from handlers import HANDLERS, REPORT_OUT_DIR, _rfc_connection_with_auth, _rfc_read  # noqa: E402

# voice_bot aus dem Modul-Cache entfernen → beim nächsten Import wird die
# aktuelle Datei frisch geladen (verhindert "alten Code läuft noch"-Probleme)
import sys as _sys
_sys.modules.pop("voice_bot", None)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bridge")

app = Flask(__name__)
CORS(app)  # erlaubt fetch() aus file:// und http://localhost:8000/cockpit/

# Alle unbehandelten Fehler als JSON zurückgeben (nie HTML an den Browser)
@app.errorhandler(Exception)
def handle_all_errors(exc):
    log.exception("Unbehandelter Fehler: %s", exc)
    return jsonify({"status": "error", "message": str(exc)}), 500

@app.errorhandler(404)
def handle_404(exc):
    return jsonify({"status": "error", "message": "Endpoint nicht gefunden"}), 404

@app.errorhandler(405)
def handle_405(exc):
    return jsonify({"status": "error", "message": "Methode nicht erlaubt"}), 405

# Cockpit-Verzeichnis: liegt eine Ebene über dem Worker-Ordner
COCKPIT_DIR = here.parent / "cockpit"


# ----------------------------------------------------------------------------
# Static-File-Server: liefert alle Cockpit-HTML/JS/CSS-Dateien aus
# Aufruf: http://localhost:8765/  -> login.html
#         http://localhost:8765/startseite.html etc.
# ----------------------------------------------------------------------------
@app.get("/")
def cockpit_root():
    return send_from_directory(COCKPIT_DIR, "login.html")

@app.route("/kundenvertraege", methods=["GET", "POST", "OPTIONS"])
def kundenvertraege_api():
    """
    Liest Kundenvertraege (VBAK + VBKD) via RFC_READ_TABLE.
    Payload (POST): { kunnr, vkorg, _sap_auth }
    Liefert: { status, contracts: [{vbeln, audat, guebg, gueen, netwr, waerk, vbtyp, zterm}] }
    """
    if request.method in ("GET", "OPTIONS"):
        return jsonify({"status": "ok", "info": "POST kunnr+vkorg+_sap_auth"}), 200

    data    = request.get_json(silent=True) or {}
    kunnr   = str(data.get("kunnr", "")).strip()
    vkorg   = str(data.get("vkorg", "0439")).strip()
    maxrows = int(data.get("maxrows", 200))
    auth    = data.get("_sap_auth") or {}
    log.info(">>> /kundenvertraege kunnr=%s vkorg=%s", kunnr, vkorg)

    try:
        conn = _rfc_connection_with_auth(auth)
        kunnr_pad = kunnr.zfill(10)

        # Schritt 1: Aktive G+H-Kontrakte (GUEEN >= 2023, 2 RFC-Calls)
        # Datum-Filter verhindert Full-Table-Scan auf VBAK
        vbak_fields = ["VBELN", "AUDAT", "GUEBG", "GUEEN", "NETWR", "WAERK", "VBTYP", "ERNAM", "VKORG"]
        kontrakte_g = _rfc_read(conn, "VBAK", vbak_fields,
            options=[{"TEXT": "VBTYP EQ 'G' AND GUEEN GE '20230101'"}], maxrows=5000)
        kontrakte_h = _rfc_read(conn, "VBAK", vbak_fields,
            options=[{"TEXT": "VBTYP EQ 'H' AND GUEEN GE '20230101'"}], maxrows=5000)
        alle_vbeln = {r.get("VBELN","").strip(): r
                     for r in (kontrakte_g + kontrakte_h)
                     if r.get("VBELN","").strip()}
        log.info("/kundenvertraege VBAK systemweit: %d Kontrakte (G=%d H=%d)",
                 len(alle_vbeln), len(kontrakte_g), len(kontrakte_h))

        # Schritt 2: Belegnummern des Kunden aus VBPA (1 RFC-Call)
        vbpa = _rfc_read(conn, "VBPA", ["VBELN", "KUNNR"],
            options=[
                {"TEXT": f"KUNNR EQ '{kunnr_pad}'"},
                {"TEXT": "AND PARVW EQ 'AG'"},
                {"TEXT": "AND POSNR EQ '000000'"},
            ],
            maxrows=5000,
        )
        kunden_vbeln = {r.get("VBELN","").strip() for r in vbpa if r.get("VBELN","").strip()}
        log.info("/kundenvertraege VBPA: %d Belege fuer %s", len(kunden_vbeln), kunnr_pad)

        # Schnittmenge in Python – keine weiteren RFC-Calls
        vbak = [v for vbeln, v in alle_vbeln.items() if vbeln in kunden_vbeln]
        log.info("/kundenvertraege Kontrakte fuer %s: %d", kunnr_pad, len(vbak))

        if not vbak:
            conn.close()
            return jsonify({"status": "ok", "contracts": [], "count": 0,
                            "info": f"Keine Kontrakte (G/H) fuer Kunde {kunnr}"})

        vbtyp_label = {"G": "Mengenkontrakt", "H": "Wertkontrakt", "K": "Preisfixierung"}
        zterm_map = {}
        for row in vbak:
            vbeln = row.get("VBELN", "").strip()
            if not vbeln:
                continue
            try:
                kd = _rfc_read(conn, "VBKD",
                    ["VBELN", "POSNR", "ZTERM", "VALDT", "BSTNK"],
                    options=[{"TEXT": f"VBELN EQ '{vbeln}' AND POSNR EQ '000000'"}],
                    maxrows=1,
                )
                zterm_map[vbeln] = {
                    "zterm": kd[0].get("ZTERM", "").strip() if kd else "",
                    "valdt": kd[0].get("VALDT", "").strip() if kd else "",
                    "bstnk": kd[0].get("BSTNK", "").strip() if kd else "",
                }
            except Exception as e:
                log.warning("/kundenvertraege VBKD %s: %s", vbeln, e)
                zterm_map[vbeln] = {"zterm": "", "valdt": "", "bstnk": ""}

        result = []
        for row in vbak:
            vbeln = row.get("VBELN", "").strip()
            kd    = zterm_map.get(vbeln, {})
            result.append({
                "vbeln": vbeln,
                "audat": row.get("AUDAT", ""),
                "guebg": row.get("GUEBG", ""),
                "gueen": row.get("GUEEN", ""),
                "netwr": row.get("NETWR", ""),
                "waerk": row.get("WAERK", ""),
                "vbtyp": row.get("VBTYP", ""),
                "vbtyp_label": vbtyp_label.get(row.get("VBTYP", ""), row.get("VBTYP", "")),
                "zterm": kd.get("zterm", ""),
                "valdt": kd.get("valdt", ""),
                "bstnk": kd.get("bstnk", ""),
            })

        conn.close()
        log.info("/kundenvertraege kunnr=%s: %d Vertraege gefunden", kunnr, len(result))
        return jsonify({"status": "ok", "contracts": result, "count": len(result)})

    except Exception as exc:
        tb = traceback.format_exc()
        log.error("/kundenvertraege Fehler: %s\n%s", exc, tb)
        return jsonify({"status": "error", "message": str(exc)})


@app.get("/<path:filename>")
def cockpit_static(filename):
    # API-Routen haben Vorrang (werden vorher registriert / matchen zuerst)
    return send_from_directory(COCKPIT_DIR, filename)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "env": os.getenv("APP_ENV", "prod"),
        "handlers": [f"{m}/{t}" for (m, t) in HANDLERS],
        "report_dir": str(REPORT_OUT_DIR),
        "sap_host": os.getenv("SAP_ASHOST", ""),
        "sap_user": os.getenv("SAP_USER", ""),
        "sap_client": os.getenv("SAP_CLIENT", ""),
        "sap_mock": os.getenv("SAP_MOCK", "0") == "1",
    })


@app.get("/env")
def get_env():
    labels = {"dev": "🟡 ENTWICKLUNG", "test": "🔵 TEST", "prod": "🔴 PRODUKTION"}
    env = os.getenv("APP_ENV", "prod")
    return jsonify({
        "env":   env,
        "label": labels.get(env, env),
        "sap_mock": os.getenv("SAP_MOCK", "0") == "1",
    })


@app.post("/run")
def run_task():
    data = request.get_json(silent=True) or {}
    method = data.get("method")
    tcode  = data.get("tcode")
    payload = data.get("payload", {})

    log.info(">>> /run empfangen: method=%r  tcode=%r", method, tcode)
    log.info(">>> Verfügbare Handler: %s", list(HANDLERS.keys()))

    if not method or not tcode:
        return jsonify({"status": "error", "message": "method und tcode sind Pflicht."}), 400

    handler = (HANDLERS.get((method, tcode))
               or HANDLERS.get(("*", tcode))
               or HANDLERS.get((method, "*")))

    log.info(">>> Handler gefunden: %s", handler)

    if not handler:
        log.warning("KEIN Handler für (%r, %r) – verfügbar: %s", method, tcode, list(HANDLERS.keys()))
        return jsonify({
            "status": "not-implemented",
            "message": f"Kein Handler fuer {method}/{tcode} - bitte im Worker ergaenzen."
        })

    safe = {k: ("***" if "password" in k.lower() or "secret" in k.lower() else v) for k, v in (payload or {}).items()}
    log.info("Run-Request: %s/%s payload=%s", method, tcode, safe)
    try:
        result = handler({"method": method, "tcode": tcode}, payload)
        if isinstance(result, dict):
            return jsonify({"status": "ok", **result})
        return jsonify({"status": "ok", "message": result})
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        log.error("Handler-Fehler: %s\n%s", exc, tb)
        return jsonify({"status": "error", "message": str(exc), "trace": tb})


@app.get("/test_handler")
def test_handler():
    """Prüft ob BAPI_ACC_DOCUMENT_POST Handler registriert ist."""
    key = ("BAPI", "BAPI_ACC_DOCUMENT_POST")
    found = key in HANDLERS
    return jsonify({
        "key_tested":  f"{key[0]}/{key[1]}",
        "handler_found": found,
        "all_handlers": [f"{m}/{t}" for (m, t) in HANDLERS],
        "sap_host": os.getenv("SAP_ASHOST", ""),
        "sap_user": os.getenv("SAP_USER", ""),
        "sap_client": os.getenv("SAP_CLIENT", ""),
    })


@app.post("/test_rfc")
def test_rfc():
    """Verbindungstest: versucht RFC_PING, faellt bei Berechtigungsfehler auf
    STFC_CONNECTION zurueck. Nur wenn beide fehlschlagen, wird ein Fehler gemeldet.
    Wenn Body ein _sap_auth-Objekt enthaelt, werden diese Verbindungsdaten genutzt."""
    from handlers import _rfc_connection_with_auth
    data     = request.get_json(silent=True) or {}
    sap_auth = data.get("_sap_auth")
    host  = (sap_auth or {}).get("ashost") or os.getenv("SAP_ASHOST", "?")
    sysnr = (sap_auth or {}).get("sysnr")  or os.getenv("SAP_SYSNR", "00")
    port  = 3300 + int(sysnr)

    try:
        conn = _rfc_connection_with_auth(sap_auth)
        conn.close()
        return jsonify({"status": "ok",
                        "message": f"Anmeldung erfolgreich – {host}:{port} erreichbar",
                        "host": host, "port": port})
    except Exception as exc:  # noqa: BLE001
        exc_str = str(exc)
        # Das SAP NW RFC SDK ruft intern RFCPING beim Verbindungsaufbau auf.
        # RFC_NO_AUTHORITY auf RFCPING bedeutet: Anmeldedaten korrekt,
        # aber der Benutzer hat keine S_RFC-Berechtigung fuer RFCPING.
        # -> Anmeldung trotzdem als erfolgreich werten.
        if "RFC_NO_AUTHORITY" in exc_str and "RFCPING" in exc_str:
            log.info("RFC-Test: Anmeldung OK, RFCPING nicht berechtigt (Benutzer=%s, Host=%s)",
                     (sap_auth or {}).get("user", "?"), host)
            return jsonify({"status": "ok",
                            "message": f"Anmeldung erfolgreich – {host}:{port} "
                                       f"(Hinweis: RFCPING nicht berechtigt – für Buchungen ausreichend)",
                            "host": host, "port": port})
        log.warning("RFC-Test fehlgeschlagen: %s", exc)
        return jsonify({"status": "error", "message": exc_str,
                        "host": host, "port": port})


# ──────────────────────────────────────────────────────────────────────────────
# Voice Bot Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/voice/chat")
def voice_chat():
    """
    Finance-Bot Chat.
    POST { text: "...", history: [{role, content}, ...] }
    Returns { status, text, intent, action, provider }
    """
    data    = request.get_json(silent=True) or {}
    text    = (data.get("text") or "").strip()
    history = data.get("history") or []

    if not text:
        return jsonify({"status": "error", "message": "text fehlt"}), 400

    log.info(">>> /voice/chat: %r", text[:80])
    try:
        from voice_bot import chat as bot_chat  # noqa: PLC0415 (lazy, gecachéd)
        result = bot_chat(text, history)
        return jsonify({"status": "ok", **result})
    except Exception as exc:
        log.exception("/voice/chat Fehler")
        return jsonify({"status": "error", "message": str(exc), "text": f"Fehler: {exc}"})


@app.get("/voice/status")
def voice_status():
    """Prüft ob Voice-Bot konfiguriert ist (liest KI-Konfiguration aus Orchestrator-DB)."""
    import urllib.request as _ur, json as _js
    orch_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
    provider = "offline"
    api_key_set = False
    model = ""
    try:
        with _ur.urlopen(f"{orch_url}/ai_config/full", timeout=3) as r:
            cfg = _js.loads(r.read().decode())
        provider    = cfg.get("provider", "claude")
        api_key     = cfg.get("api_key",  "").strip()
        model       = cfg.get("model",    "")
        api_key_set = bool(api_key)
    except Exception:
        # Fallback auf env-var
        api_key_set = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
        if api_key_set:
            provider = "claude"
    return jsonify({
        "status":      "ok",
        "provider":    provider if api_key_set else "offline",
        "api_key_set": api_key_set,
        "claude_api":  api_key_set and provider == "claude",
        "openai_api":  api_key_set and provider == "openai",
        "model":       model or ("claude-haiku-4-5-20251001" if provider == "claude" else "gpt-4o-mini"),
        "hint":        "" if api_key_set else "API-Key in voice.html → ⚙ KI-API eintragen",
    })


@app.get("/teams/status")
def teams_status():
    """Prüft ob Teams-Webhook konfiguriert ist."""
    url = os.getenv("TEAMS_WEBHOOK_URL", "").strip()
    return jsonify({
        "configured": bool(url),
        "hint": "" if url else "TEAMS_WEBHOOK_URL in worker/.env eintragen",
    })


@app.post("/teams/send")
def teams_send():
    """Sendet eine Nachricht an den konfigurierten Teams-Kanal."""
    import urllib.request as _ur, json as _js
    url = os.getenv("TEAMS_WEBHOOK_URL", "").strip()
    if not url:
        return jsonify({"ok": False, "error": "TEAMS_WEBHOOK_URL nicht konfiguriert"}), 503
    data = request.get_json(silent=True) or {}
    title   = data.get("title",   "Esra – Finance-Assistentin")
    message = data.get("message", "")
    if not message:
        return jsonify({"ok": False, "error": "message fehlt"}), 400
    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard", "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": title, "weight": "Bolder", "size": "Medium"},
                    {"type": "TextBlock", "text": message, "wrap": True},
                ],
            },
        }],
    }
    try:
        payload = _js.dumps(card, ensure_ascii=False).encode("utf-8")
        req = _ur.Request(url, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
        with _ur.urlopen(req, timeout=10) as r:
            r.read()
        return jsonify({"ok": True})
    except Exception as exc:
        log.exception("Teams-Send Fehler")
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/reports")
def list_reports():
    files = []
    for p in sorted(REPORT_OUT_DIR.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file():
            files.append({
                "name": p.name,
                "size": p.stat().st_size,
                "mtime": int(p.stat().st_mtime * 1000),
            })
    return jsonify({"files": files})



@app.post("/stammdaten")
def stammdaten_api():
    """
    Selbststaendiger Endpoint fuer SAP Stammdaten via RFC_READ_TABLE.
    Keine Abhaengigkeit von HANDLERS oder handlers.py.
    Payload: { entity, comp_code, kokrs, maxrows, _sap_auth }
    entity: debitoren | kreditoren | konten | kostenstellen
    """
    data    = request.get_json(silent=True) or {}
    entity    = data.get("entity", "debitoren")
    comp_code = data.get("comp_code", "0435")
    kokrs     = data.get("kokrs") or comp_code
    ktopl     = (data.get("ktopl") or "").strip()   # Kontenplan z.B. ZIKR
    maxrows   = int(data.get("maxrows", 1000))
    auth      = data.get("_sap_auth") or {}
    log.info(">>> /stammdaten entity=%r bukrs=%s", entity, comp_code)

    try:
        from pyrfc import Connection  # type: ignore
        conn_params = {
            "ashost": auth.get("ashost") or os.getenv("SAP_ASHOST", ""),
            "sysnr":  auth.get("sysnr")  or os.getenv("SAP_SYSNR", "00"),
            "client": auth.get("client") or os.getenv("SAP_CLIENT", ""),
            "user":   auth.get("user")   or os.getenv("SAP_USER", ""),
            "passwd": auth.get("passwd") or os.getenv("SAP_PASSWORD", ""),
            "lang":   auth.get("lang")   or os.getenv("SAP_LANG", "DE"),
        }
        conn = Connection(**conn_params)

        def rfc_table(table, fields, options=None, row_limit=1000):
            def _call(limit):
                return conn.call("RFC_READ_TABLE",
                    QUERY_TABLE=table,
                    FIELDS=[{"FIELDNAME": f} for f in fields],
                    OPTIONS=options or [],
                    ROWCOUNT=limit,
                )
            def _parse(res):
                flds = res.get("FIELDS", [])
                out  = []
                for row in res.get("DATA", []):
                    wa  = row.get("WA", "")
                    rec = {}
                    for fld in flds:
                        nm = fld.get("FIELDNAME", "")
                        try:
                            off = int(fld.get("OFFSET", 0))
                            lng = int(fld.get("LENGTH", 0))
                            rec[nm] = wa[off:off + lng].strip() if lng > 0 else ""
                        except Exception:
                            rec[nm] = ""
                    out.append(rec)
                return out

            try:
                return _parse(_call(row_limit))
            except Exception as rfc_exc:
                err_str = str(rfc_exc)
                if "TABLE_WITHOUT_DATA" in err_str:
                    log.info("rfc_table %s: 0 Zeilen", table)
                    return []
                if "DATA_BUFFER_EXCEEDED" in err_str or "SAPSQL_DATA_LOSS" in err_str:
                    # Buffer zu klein – in 2 kleineren Batches lesen
                    half = max(50, row_limit // 2)
                    log.warning("rfc_table %s: Buffer-Fehler bei %d Zeilen, retry mit %d", table, row_limit, half)
                    try:
                        return _parse(_call(half))
                    except Exception:
                        quarter = max(20, half // 2)
                        log.warning("rfc_table %s: retry mit %d", table, quarter)
                        try:
                            return _parse(_call(quarter))
                        except Exception:
                            log.error("rfc_table %s: auch %d Zeilen fehlgeschlagen", table, quarter)
                            return []
                raise

        try:
            from datetime import datetime as _dt
            records = []

            if entity == "debitoren":
                knb1 = rfc_table("KNB1", ["KUNNR","BUKRS","AKONT","ZTERM"],
                                 [{"TEXT": f"BUKRS EQ '{comp_code}'"}], maxrows)
                kset = {r["KUNNR"] for r in knb1 if r.get("KUNNR")}
                kna1 = rfc_table("KNA1", ["KUNNR","NAME1","ORT01","LAND1","TELF1"],
                                 [], min(maxrows * 3, 5000))
                km   = {r["KUNNR"]: r for r in kna1 if r.get("KUNNR") in kset}
                records = [{
                    "nr": r["KUNNR"],
                    "name":  km.get(r["KUNNR"], {}).get("NAME1", ""),
                    "city":  km.get(r["KUNNR"], {}).get("ORT01", ""),
                    "land":  km.get(r["KUNNR"], {}).get("LAND1", ""),
                    "tel":   km.get(r["KUNNR"], {}).get("TELF1", ""),
                    "akont": r.get("AKONT", ""),
                    "zterm": r.get("ZTERM", ""),
                } for r in knb1 if r.get("KUNNR")]

            elif entity == "kreditoren":
                lfb1 = rfc_table("LFB1", ["LIFNR","BUKRS","AKONT","ZTERM"],
                                 [{"TEXT": f"BUKRS EQ '{comp_code}'"}], maxrows)
                lset = {r["LIFNR"] for r in lfb1 if r.get("LIFNR")}
                lfa1 = rfc_table("LFA1", ["LIFNR","NAME1","ORT01","LAND1","TELF1"],
                                 [], min(maxrows * 3, 5000))
                lm   = {r["LIFNR"]: r for r in lfa1 if r.get("LIFNR") in lset}
                records = [{
                    "nr": r["LIFNR"],
                    "name":  lm.get(r["LIFNR"], {}).get("NAME1", ""),
                    "city":  lm.get(r["LIFNR"], {}).get("ORT01", ""),
                    "land":  lm.get(r["LIFNR"], {}).get("LAND1", ""),
                    "tel":   lm.get(r["LIFNR"], {}).get("TELF1", ""),
                    "akont": r.get("AKONT", ""),
                    "zterm": r.get("ZTERM", ""),
                } for r in lfb1 if r.get("LIFNR")]

            elif entity == "konten":
                bukrs_pad = comp_code.strip().zfill(4)
                use_ktopl = (ktopl or "").strip() or "ZIKR"
                log.info("Konten-Abruf: KTOPL=%s BUKRS=%s", use_ktopl, bukrs_pad)

                # ── SKA1: zuerst MIT KTOPL-Filter versuchen, Fallback ohne Filter ──
                ska1_all = rfc_table("SKA1", ["SAKNR","KTOPL","KTOKS","XBILK"],
                                     [{"TEXT": f"KTOPL EQ '{use_ktopl}'"}], 5000)
                log.info("SKA1 mit Filter KTOPL=%s: %d Zeilen", use_ktopl, len(ska1_all))

                if not ska1_all:
                    # WHERE-Filter liefert nichts → alle lesen, Python-Filter
                    ska1_raw = rfc_table("SKA1", ["SAKNR","KTOPL","KTOKS","XBILK"], [], 5000)
                    log.info("SKA1 ohne Filter: %d Zeilen gesamt", len(ska1_raw))
                    all_ktopl = sorted({r.get("KTOPL","").strip() for r in ska1_raw if r.get("KTOPL","").strip()})
                    log.info("KTOPL-Werte: %s", all_ktopl)
                    ska1_all = [r for r in ska1_raw if r.get("KTOPL","").strip() == use_ktopl]
                    if not ska1_all and all_ktopl:
                        use_ktopl = all_ktopl[0]
                        ska1_all = [r for r in ska1_raw if r.get("KTOPL","").strip() == use_ktopl]
                log.info("SKA1 KTOPL=%s: %d Konten", use_ktopl, len(ska1_all))

                # ── SKAT: Texte MIT Filter, Fallback ohne ──
                skat_all = rfc_table("SKAT", ["SPRAS","SAKNR","KTOPL","TXT20","TXT50"],
                                     [{"TEXT": f"KTOPL EQ '{use_ktopl}'"}], 5000)
                if not skat_all:
                    skat_raw = rfc_table("SKAT", ["SPRAS","SAKNR","KTOPL","TXT20","TXT50"], [], 5000)
                    skat_all = [r for r in skat_raw if r.get("KTOPL","").strip() == use_ktopl]
                log.info("SKAT KTOPL=%s: %d Zeilen", use_ktopl, len(skat_all))

                skat_map = {}
                for r in skat_all:
                    saknr = r.get("SAKNR","").strip()
                    spras = r.get("SPRAS","").strip()
                    if saknr and spras:
                        skat_map.setdefault(saknr, {})[spras] = (
                            r.get("TXT20","").strip(), r.get("TXT50","").strip())

                def _skat_text(saknr):
                    langs = skat_map.get(saknr, {})
                    for p in ["D","E","DE","EN"]:
                        if p in langs: return langs[p]
                    return next(iter(langs.values())) if langs else ("","")

                # ── SKB1: MIT Filter, Fallback ohne ──
                skb1_all = rfc_table("SKB1", ["SAKNR","BUKRS","XSPEA","WAERS"],
                                     [{"TEXT": f"BUKRS EQ '{bukrs_pad}'"}], 5000)
                if not skb1_all:
                    skb1_raw = rfc_table("SKB1", ["SAKNR","BUKRS","XSPEA","WAERS"], [], 5000)
                    skb1_all = [r for r in skb1_raw if r.get("BUKRS","").strip() == bukrs_pad]
                skb1_map = {r["SAKNR"].strip(): r for r in skb1_all if r.get("SAKNR")}
                log.info("SKB1 BUKRS=%s: %d Konten", bukrs_pad, len(skb1_map))

                # ── Join: SKB1 als Filter wenn vorhanden, sonst alle SKA1 ──
                records = []
                for r in ska1_all:
                    saknr = r.get("SAKNR","").strip()
                    if not saknr: continue
                    b = skb1_map.get(saknr)
                    if skb1_map and b is None: continue  # nur filtern wenn SKB1 Daten hat
                    txt20, txt50 = _skat_text(saknr)
                    records.append({
                        "nr":    saknr,
                        "txt20": txt20,
                        "txt50": txt50,
                        "ktoks": r.get("KTOKS",""),
                        "ktopl": r.get("KTOPL",""),
                        "xbilk": r.get("XBILK",""),
                        "xspea": (b or {}).get("XSPEA",""),
                        "waers": (b or {}).get("WAERS",""),
                    })
                log.info("Konten: %d (KTOPL=%s BUKRS=%s | SKA1=%d SKAT=%d SKB1=%d)",
                         len(records), use_ktopl, bukrs_pad,
                         len(ska1_all), len(skat_all), len(skb1_map))

            elif entity == "kostenstellen":
                use_kokrs = (kokrs or "").strip() or "1000"
                log.info("Kostenstellen: CSKS+CSKT KOKRS=%s", use_kokrs)

                # Schritt 1: CSKS – alle Zeilen lesen (kein SAP-Filter, Buffer-Retry aktiv)
                # CSKS hat mehrere Gültigkeitsperioden pro Kostenstelle → Duplikate erwartet
                csks_raw = rfc_table("CSKS",
                                     ["KOSTL","KOKRS","VERAK","ABTEI"],
                                     [], 5000)
                log.info("CSKS gesamt: %d Zeilen (inkl. alte Perioden)", len(csks_raw))

                # KOKRS in Python filtern; Fallback auf ersten vorhandenen Wert
                csks_filtered = [r for r in csks_raw if r.get("KOKRS","").strip() == use_kokrs]
                if not csks_filtered and csks_raw:
                    found = sorted({r.get("KOKRS","").strip() for r in csks_raw if r.get("KOKRS","").strip()})
                    log.info("KOKRS=%s nicht in CSKS – vorhandene: %s", use_kokrs, found)
                    use_kokrs = found[0]
                    csks_filtered = [r for r in csks_raw if r.get("KOKRS","").strip() == use_kokrs]
                log.info("CSKS KOKRS=%s: %d Zeilen", use_kokrs, len(csks_filtered))

                # Deduplizieren: pro KOSTL nur einen Eintrag behalten
                # (letzter Eintrag = neueste Gültigkeitsperiode in RFC-Reihenfolge)
                csks_dedup = {}
                for r in csks_filtered:
                    kostl = r.get("KOSTL","").strip()
                    if kostl:
                        csks_dedup[kostl] = r   # überschreibt alte Perioden
                log.info("CSKS nach Deduplizierung: %d eindeutige Kostenstellen", len(csks_dedup))

                # Schritt 2: CSKT – Bezeichnungen ohne SPRAS-Filter (alle Sprachen),
                # dann in Python nach DE filtern (Fallback EN, dann erste verfügbare)
                cskt_raw = rfc_table("CSKT",
                                     ["KOKRS","KOSTL","SPRAS","KTEXT","LTEXT"],
                                     [{"TEXT": f"KOKRS EQ '{use_kokrs}'"}],
                                     5000)
                log.info("CSKT gesamt: %d Zeilen", len(cskt_raw))

                # Pro KOSTL+SPRAS den Text merken
                cskt_by_lang = {}   # {kostl: {spras: (ktext, ltext)}}
                for r in cskt_raw:
                    kostl = r.get("KOSTL","").strip()
                    spras = r.get("SPRAS","").strip()
                    if kostl and spras:
                        cskt_by_lang.setdefault(kostl, {})[spras] = (
                            r.get("KTEXT","").strip(),
                            r.get("LTEXT","").strip(),
                        )

                # Besten Text pro Kostenstelle wählen: DE > EN > erster verfügbarer
                cskt_map = {}  # kostl → (ktext, ltext)
                for kostl, langs in cskt_by_lang.items():
                    for pref in ["DE", "EN"]:
                        if pref in langs:
                            cskt_map[kostl] = langs[pref]
                            break
                    else:
                        cskt_map[kostl] = next(iter(langs.values()))
                log.info("CSKT Texte: %d Kostenstellen", len(cskt_map))

                # Schritt 3: Join CSKS + CSKT
                records = [{
                    "nr":    kostl,
                    "kokrs": r.get("KOKRS",""),
                    "ktext": cskt_map.get(kostl, ("",""))[1] or cskt_map.get(kostl, ("",""))[0],
                    "verak": r.get("VERAK",""),
                    "abtei": r.get("ABTEI",""),
                } for kostl, r in sorted(csks_dedup.items())]
                log.info("Kostenstellen: %d Eintraege (%d mit Bezeichnung)",
                         len(records), sum(1 for r in records if r["ktext"]))

        finally:
            conn.close()

        log.info("/stammdaten OK: entity=%s count=%d", entity, len(records))
        return jsonify({"status": "ok", "records": records,
                        "count": len(records), "entity": entity})

    except Exception as exc:
        tb = traceback.format_exc()
        log.error("/stammdaten Fehler: %s\n%s", exc, tb)
        return jsonify({"status": "error", "message": str(exc)})


@app.get("/reports/<path:name>")
def download_report(name):
    return send_from_directory(REPORT_OUT_DIR, name, as_attachment=True)



# ── AP-Aging / FBL1N-Import ───────────────────────────────────────────────────
@app.post("/ap-aging/fbl1n-import")
def ap_aging_fbl1n_import():
    """
    Direkter FBL1N-Import via Bridge (hat pyrfc).
    Wird vom Orchestrator-Endpoint /ap-aging/import aufgerufen.
    """
    import json as _json
    data = request.get_json(silent=True) or {}

    # batch_fbl1n_ap_aging erwartet (task: dict, payload: dict)
    task    = {"method": "BATCH", "tcode": "FBL1N_AP_AGING"}
    payload = {
        "bukrs":        data.get("bukrs", ""),
        "key_date":     data.get("key_date", ""),
        "normal_items": data.get("normal_items", True),
        "special_gl":   data.get("special_gl",  True),
        "months_back":  int(data.get("months_back", 36)),
        # _sap_auth: None → _rfc_connection_with_auth faellt auf .env zurück
    }

    try:
        from handlers import batch_fbl1n_ap_aging
        result = batch_fbl1n_ap_aging(task, payload)
        return jsonify({"status": "ok", **result})
    except Exception as exc:
        tb = traceback.format_exc()
        log.error("/ap-aging/fbl1n-import Fehler: %s\n%s", exc, tb)
        return jsonify({"status": "error", "message": str(exc)}), 500


# ── Sales / CO-PA-Import ──────────────────────────────────────────────────────
@app.post("/sales/copa-import")
def sales_copa_import():
    """
    Direkter CO-PA/SD-Billing-Import via Bridge (hat pyrfc).
    Wird vom Orchestrator-Endpoint /sales/import aufgerufen.
    """
    data = request.get_json(silent=True) or {}

    task    = {"method": "BAPI", "tcode": "COPA_SALES_REPORT"}
    payload = {
        "comp_codes":        data.get("comp_codes", ""),
        "date_from":         data.get("date_from", ""),
        "date_to":           data.get("date_to", ""),
        "source":            data.get("source", "vbrk"),
        "operating_concern": data.get("operating_concern", ""),
        "customer_filter":   data.get("customer_filter", ""),
        "material_filter":   data.get("material_filter", ""),
        "maxrows":           int(data.get("maxrows", 5000)),
        "_sap_auth":         data.get("_sap_auth"),
    }

    try:
        from handlers import copa_sales_report
        result = copa_sales_report(task, payload)
        return jsonify({"status": "ok", **result})
    except Exception as exc:
        tb = traceback.format_exc()
        log.error("/sales/copa-import Fehler: %s\n%s", exc, tb)
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("BRIDGE_PORT", "8765"))
    log.info("Bridge startet auf Port %d ...")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
