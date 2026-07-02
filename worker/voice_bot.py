"""
Finance Voice Bot – Kernlogik
==============================
Wird von bridge.py aufgerufen (POST /voice/chat).

Ablauf:
  1. Finance-Kontext aus dem Orchestrator holen (Buchungshistorie, Darlehen, Zeitpläne)
  2. Claude Haiku mit Kontext + Nutzerfrage aufrufen
  3. Intent + optionale Bridge-Aktion erkennen
  4. Strukturierte Antwort zurückgeben

Spracherkennung (STT) und Sprachausgabe (TTS) laufen im Browser
via Web Speech API und speechSynthesis — kein Server nötig für Phase 1.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Any

log = logging.getLogger("voice_bot")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")


# ──────────────────────────────────────────────────────────────────────────────
# Finance-Kontext aus Orchestrator holen
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_url(url: str, timeout: int = 5) -> Any:
    """Kleiner HTTP-GET Helper ohne requests-Abhängigkeit."""
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log.warning("_fetch_url %s: %s", url, e)
        return None


def _fetch_post(url: str, payload: dict, timeout: int = 10) -> Any:
    """HTTP-POST Helper ohne requests-Abhängigkeit."""
    import urllib.request
    try:
        data = json.dumps(payload).encode()
        req  = urllib.request.Request(url, data=data,
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log.warning("_fetch_post %s: %s", url, e)
        return None


def fetch_finance_context() -> dict:
    """
    Holt aktuellen Finance-Kontext aus dem Orchestrator.
    Alle verfügbaren Datenquellen werden kompakt zusammengefasst.
    """
    parts = []
    month = datetime.now().strftime("%Y-%m")
    today = datetime.now().strftime("%Y-%m-%d")
    parts.append(f"Aktuelles Datum: {today}  |  Monat: {month}")

    # ── Zeitpläne ────────────────────────────────────────────────
    sched = _fetch_url(f"{ORCHESTRATOR_URL}/schedules")
    if sched and isinstance(sched, list):
        active = [s for s in sched if s.get("enabled")]
        if active:
            lines = [
                f"  - {s.get('name','?')}: {s.get('cron','?')} "
                f"(letzter Lauf: {s.get('last_run','nie')})"
                for s in active[:5]
            ]
            parts.append("Aktive Zeitpläne:\n" + "\n".join(lines))
        else:
            parts.append("Zeitpläne: keine aktiven Zeitpläne.")

    # ── Payroll-Imports ──────────────────────────────────────────
    payroll = _fetch_url(f"{ORCHESTRATOR_URL}/payroll/imports?limit=5")
    if payroll and isinstance(payroll, list):
        lines = [
            f"  - {p.get('periode','?')}: {p.get('dateiname','?')} | "
            f"Status={p.get('status','?')} | "
            f"Gesamt={p.get('gesamtbetrag','?')} EUR"
            for p in payroll[:5]
        ]
        parts.append("Payroll-Imports (letzte 5):\n" + "\n".join(lines))
    else:
        parts.append("Payroll: keine Daten verfügbar.")

    # ── Rechnungen diesen Monat ──────────────────────────────────
    inv = _fetch_url(f"{ORCHESTRATOR_URL}/invoice_records?month={month}&limit=10")
    if inv and isinstance(inv, list):
        total = sum(float(i.get("amount", 0) or 0) for i in inv)
        booked = sum(1 for i in inv if i.get("status") == "booked")
        lines  = [
            f"  - {i.get('subsidiary','?')}: "
            f"{i.get('amount','?')} EUR | Status={i.get('status','?')}"
            for i in inv[:6]
        ]
        parts.append(
            f"Rechnungen {month} ({len(inv)} gesamt, {booked} gebucht, "
            f"Summe: {total:,.0f} EUR):\n" + "\n".join(lines)
        )
    else:
        parts.append(f"Rechnungen {month}: keine Daten.")

    # ── ZTERM-Log (Zahlungsbedingungen-Änderungen) ───────────────
    zlog = _fetch_url(f"{ORCHESTRATOR_URL}/zterm-log?limit=5")
    if zlog and isinstance(zlog, list) and zlog:
        lines = [
            f"  - {z.get('created_at','?')[:10]}: "
            f"Kunde {z.get('kunnr','?')} | "
            f"{z.get('old_zterm','?')}→{z.get('new_zterm','?')} | "
            f"User: {z.get('sap_user','?')}"
            for z in zlog[:5]
        ]
        parts.append("Letzte ZTERM-Änderungen:\n" + "\n".join(lines))

    return {"text": "\n\n".join(parts)}


# ──────────────────────────────────────────────────────────────────────────────
# System-Prompt
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """Du bist Esra 2.0 aus Catensys – die intelligente Finance-Assistentin für das YCONN SAP-Cockpit.
Du antwortest freundlich, professionell und präzise – wie Alexa, aber für SAP und Finance.
Dein Name ist Esra. Wenn jemand fragt wer du bist, sagst du: "Ich bin Esra 2.0 aus Catensys."
Antworte IMMER auf Deutsch, kurz (max 2-3 Sätze – für Sprachausgabe optimiert).

═══════════════════════════════════════════════════
VERFÜGBARE MODULE – öffne sie mit NAVIGATE:
═══════════════════════════════════════════════════
• Zinsbuchungen / Darlehen  → NAVIGATE: zinsen.html
• Rechnungen / SAP-SD       → NAVIGATE: rechnung.html
• Payroll / Gehaltsimport   → NAVIGATE: payroll.html
• Kundenstamm               → NAVIGATE: kundenstamm.html
• Cockpit / Buchungshistorie→ NAVIGATE: cockpit.html
• Startseite / Übersicht    → NAVIGATE: startseite.html
• Verbindungen / SAP-RFC    → NAVIGATE: verbindungen.html
• Digitales Gehirn / 3W     → NAVIGATE: brain.html

═══════════════════════════════════════════════════
REGELN FÜR NAVIGATE:
═══════════════════════════════════════════════════
- Wenn Benutzer ein Modul öffnen möchte → NAVIGATE: <datei>
- Bei Buchungen: ERST öffne das Modul, DANN erkläre was zu tun ist
- KEINE automatischen Buchungen ausführen – nur navigieren und erklären

═══════════════════════════════════════════════════
WAS DU BEANTWORTEST (aus dem Kontext unten):
═══════════════════════════════════════════════════
- Payroll: Status, Betrag, welcher Monat bereits importiert
- Rechnungen: Anzahl, Summe, Status (offen/gebucht) diesen Monat
- Zeitpläne: Wann läuft was automatisch, letzter Lauf
- ZTERM: Letzte Zahlungsbedingungen-Änderungen
- Finance-Begriffe erklären (ZTERM, Buchungskreis, IC-Buchung, etc.)

═══════════════════════════════════════════════════
AUSGABEFORMAT (am Ende der Antwort):
═══════════════════════════════════════════════════
INTENT: [query|navigate|invoice|payroll|schedule|sap_action|unknown]
NAVIGATE: <dateiname.html>   ← nur wenn Navigation sinnvoll/gewünscht
ACTION: <JSON oder null>     ← nur für SAP-Aktionen mit Bestätigung

Beispiele:
- "Öffne Zinsen" → INTENT: navigate\nNAVIGATE: zinsen.html
- "Wie viele Rechnungen diesen Monat?" → INTENT: invoice (aus Kontext beantworten)
- "Was ist ZTERM?" → INTENT: query (direkt erklären)
- "Buche die Zinsen" → INTENT: sap_action, NAVIGATE: zinsen.html + erklären dass Benutzer dort buchen soll

═══════════════════════════════════════════════════
AKTUELLER FINANCE-KONTEXT:
═══════════════════════════════════════════════════
{context}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Intent-Erkennung (Keyword-Fallback ohne Claude)
# ──────────────────────────────────────────────────────────────────────────────

INTENT_KEYWORDS = {
    "query":      ["buchung", "gebucht", "history", "historie", "was wurde", "zeige", "liste"],
    "sap_action": ["ändere", "ändern", "setze", "zahlungsbedingung", "zterm", "xd02", "va42"],
    "schedule":   ["zeitplan", "nächste", "fällig", "wann", "scheduler", "automatisch"],
    "invoice":    ["rechnung", "invoice", "faktura", "sd", "billing"],
    "loan":       ["darlehen", "zins", "kredit", "tilgung", "annuität"],
}

def detect_intent_keywords(text: str) -> str:
    t = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in t for k in keywords):
            return intent
    return "unknown"


# ──────────────────────────────────────────────────────────────────────────────
# KI-Provider-Konfiguration aus Orchestrator lesen
# ──────────────────────────────────────────────────────────────────────────────

def _load_ai_config() -> dict:
    """
    Liest KI-Provider + API-Key in dieser Reihenfolge:
    1. Orchestrator-DB (/ai_config/full)
    2. Umgebungsvariablen (.env)
    3. esra_config.json (vom Esra Desktop-App gespeichert)
    """
    # 1. Orchestrator-DB
    cfg = _fetch_url(f"{ORCHESTRATOR_URL}/ai_config/full")
    if cfg and cfg.get("api_key"):
        return cfg

    # 2. Env-Var
    claude_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if claude_key:
        return {"provider": "claude", "api_key": claude_key, "model": ""}
    if openai_key:
        return {"provider": "openai", "api_key": openai_key, "model": ""}

    # 3. esra_config.json (Einstellungen aus Esra Desktop-App)
    try:
        esra_cfg_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "esra", "esra_config.json"
        )
        if os.path.isfile(esra_cfg_path):
            with open(esra_cfg_path, "r", encoding="utf-8") as f:
                esra_cfg = json.load(f)
            ck = esra_cfg.get("claude_key", "").strip()
            ok = esra_cfg.get("openai_key", "").strip()
            if ck:
                log.info("KI-Key aus esra_config.json geladen (Claude)")
                return {"provider": "claude", "api_key": ck, "model": "claude-haiku-4-5-20251001"}
            if ok:
                log.info("KI-Key aus esra_config.json geladen (OpenAI)")
                return {"provider": "openai", "api_key": ok, "model": "gpt-4o-mini"}
    except Exception as e:
        log.warning("esra_config.json Lesefehler: %s", e)

    return {"provider": "claude", "api_key": "", "model": ""}


# ──────────────────────────────────────────────────────────────────────────────
# KI-Aufruf (Claude oder OpenAI/ChatGPT)
# ──────────────────────────────────────────────────────────────────────────────

def _call_claude(api_key: str, model: str, system: str, messages: list) -> str:
    import anthropic  # type: ignore
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model or "claude-haiku-4-5-20251001",
        max_tokens=600,
        system=system,
        messages=messages,
    )
    return resp.content[0].text


def _call_openai(api_key: str, model: str, system: str, messages: list) -> str:
    import urllib.request, urllib.error as _ue, json as _js, time as _tm
    model = model or "gpt-4o-mini"
    payload = {
        "model": model,
        "max_tokens": 600,
        "messages": [{"role": "system", "content": system}] + messages,
    }
    data = _js.dumps(payload).encode()
    req  = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    for attempt in range(3):   # bis zu 3 Versuche bei Rate-Limit
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                result = _js.loads(r.read().decode())
            return result["choices"][0]["message"]["content"]
        except _ue.HTTPError as exc:
            if exc.code != 429:
                # andere Fehler (401, 400 …) sofort weitergeben
                body = ""
                try: body = exc.read().decode()
                except Exception: pass
                try:
                    err = _js.loads(body).get("error", {})
                    raise Exception(f"OpenAI Fehler {exc.code}: {err.get('message', body[:200])}")
                except (_js.JSONDecodeError, KeyError):
                    raise Exception(f"OpenAI HTTP {exc.code}: {body[:200]}")
            # --- 429 Rate-Limit oder Kontingent-Erschöpft ---
            body = ""
            try: body = exc.read().decode()
            except Exception: pass
            # Kontingent (kein Guthaben) vs. Rate-Limit unterscheiden
            if any(k in body for k in ("insufficient_quota", "billing", "exceeded your current quota")):
                raise Exception(
                    "OpenAI-Kontingent erschöpft. Bitte Guthaben unter "
                    "platform.openai.com/account/billing aufladen oder ein günstigeres Modell wählen."
                )
            # Rate-Limit: warten und erneut versuchen
            retry_after = 3
            try:
                retry_after = int(exc.headers.get("Retry-After", 3))
            except Exception:
                pass
            retry_after = min(retry_after, 10)   # max 10s warten
            if attempt < 2:
                log.warning("OpenAI 429 – warte %ds (Versuch %d/3)", retry_after, attempt + 1)
                _tm.sleep(retry_after)
                continue
            raise Exception(
                f"OpenAI Anfrage-Limit (429) nach 3 Versuchen. "
                f"Tipp: Weniger häufig anfragen oder Modell 'gpt-4o-mini' wählen."
            )


def chat(user_text: str, history: list[dict]) -> dict:
    """
    Hauptfunktion: Text → KI (Claude oder OpenAI) → strukturierte Antwort.

    Returns:
        {
            "text":     "Antworttext für TTS",
            "intent":   "query|sap_action|...",
            "action":   {method, tcode, payload} | None,
            "raw":      vollständiger KI-Output,
            "provider": "claude|openai",
        }
    """
    ai_cfg  = _load_ai_config()
    provider = ai_cfg.get("provider", "claude")
    api_key  = ai_cfg.get("api_key",  "").strip()
    model    = ai_cfg.get("model",    "").strip()

    # Kontext holen
    context_data = fetch_finance_context()
    context_text = context_data.get("text", "Kein Kontext verfügbar.")

    # Keyword-Fallback (wenn kein API-Key)
    keyword_intent = detect_intent_keywords(user_text)

    if not api_key:
        fallback = _offline_response(user_text, keyword_intent, context_text)
        return {"text": fallback, "intent": keyword_intent, "action": None, "raw": fallback, "provider": "offline"}

    system   = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)
    messages = [{"role": m["role"], "content": m["content"]} for m in history[-8:]]
    messages.append({"role": "user", "content": user_text})

    try:
        if provider == "openai":
            raw = _call_openai(api_key, model, system, messages)
            log.info("OpenAI Antwort (%d Zeichen)", len(raw))
        else:
            raw = _call_claude(api_key, model, system, messages)
            log.info("Claude Antwort (%d Zeichen)", len(raw))

    except Exception as e:
        err_msg = str(e)
        log.error("KI API Fehler (%s): %s", provider, err_msg)

        # Automatischer Fallback: wenn OpenAI ausfällt → Claude (env-var) versuchen
        if provider == "openai":
            claude_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
            if claude_key:
                try:
                    log.warning("OpenAI fehlgeschlagen – versuche Claude-Fallback")
                    raw = _call_claude(claude_key, "", system, messages)
                    log.info("Claude-Fallback erfolgreich (%d Zeichen)", len(raw))
                    intent, action, clean_text = _parse_claude_output(raw, keyword_intent)
                    return {"text": clean_text, "intent": intent, "action": action,
                            "raw": raw, "provider": "claude_fallback"}
                except Exception as e2:
                    log.error("Claude-Fallback auch fehlgeschlagen: %s", e2)

        # Nutzerfreundliche Fehlermeldung je nach Fehlertyp
        if "Kontingent erschöpft" in err_msg or "insufficient_quota" in err_msg or "billing" in err_msg:
            user_msg = ("OpenAI-Guthaben aufgebraucht. Bitte unter "
                        "platform.openai.com/account/billing Guthaben aufladen "
                        "oder in den KI-Einstellungen auf Claude wechseln.")
        elif "429" in err_msg or "Rate" in err_msg or "Anfrage-Limit" in err_msg:
            user_msg = ("OpenAI-Anfragelimit erreicht. Bitte einen Moment warten "
                        "und erneut versuchen, oder in den KI-Einstellungen "
                        "das Modell 'GPT-3.5 Turbo' wählen.")
        elif "401" in err_msg or "Unauthorized" in err_msg:
            user_msg = "OpenAI-API-Key ungültig. Bitte in den KI-Einstellungen (⚙) prüfen."
        else:
            user_msg = f"KI-Dienst ({provider}) nicht erreichbar: {err_msg}"

        return {"text": user_msg, "intent": keyword_intent, "action": None,
                "raw": err_msg, "provider": provider}

    # Intent und Action aus Claude-Output parsen
    intent, action, clean_text = _parse_claude_output(raw, keyword_intent)

    return {
        "text":     clean_text,
        "intent":   intent,
        "action":   action,
        "raw":      raw,
        "provider": provider,
    }


def _parse_claude_output(raw: str, fallback_intent: str) -> tuple[str, Any, str]:
    """Extrahiert INTENT:, NAVIGATE: und ACTION: Zeilen aus Claude-Antwort."""
    intent   = fallback_intent
    action   = None
    navigate = None
    lines    = raw.strip().split("\n")
    text_lines = []

    for line in lines:
        ls = line.strip()
        if ls.startswith("INTENT:"):
            intent = ls.replace("INTENT:", "").strip().lower().split()[0]
        elif ls.startswith("NAVIGATE:"):
            navigate = ls.replace("NAVIGATE:", "").strip()
        elif ls.startswith("ACTION:"):
            action_str = ls.replace("ACTION:", "").strip()
            if action_str and action_str.lower() not in ("null", "none", ""):
                try:
                    action = json.loads(action_str)
                except Exception:
                    pass
        else:
            text_lines.append(line)

    clean_text = "\n".join(text_lines).strip()
    if not clean_text:
        clean_text = raw.strip()

    # Navigate-Aktion in action einbetten (Frontend wertet aus)
    if navigate:
        nav_action = {"type": "navigate", "url": navigate}
        if action and isinstance(action, dict):
            action["navigate"] = navigate
        else:
            action = nav_action

    return intent, action, clean_text


def _offline_response(user_text: str, intent: str, context: str) -> str:
    """Einfache regelbasierte Antworten wenn kein ANTHROPIC_API_KEY."""
    t = user_text.lower()
    if intent == "query":
        return "Ich zeige Ihnen die letzten Buchungen. Bitte schauen Sie im Cockpit unter Buchungshistorie nach."
    if intent == "sap_action":
        return "Ich kann SAP-Aktionen ausführen. Bitte bestätigen Sie den Befehl im Cockpit."
    if intent == "schedule":
        return "Die Zeitpläne finden Sie unter Zinsen → Zeitpläne im Cockpit."
    if intent == "invoice":
        return "Rechnungsinformationen finden Sie unter Rechnungen im Cockpit."
    if intent == "loan":
        return "Darlehens- und Zinsdetails finden Sie unter Zinsen → Rechner im Cockpit."
    return ("Ich bin Esra, Ihre Finance-Assistentin von Catensys. "
            "Ich beantworte Fragen zu SAP-Buchungen, Zinsen, Rechnungen und Zeitplänen. "
            "Wie kann ich Ihnen helfen?")