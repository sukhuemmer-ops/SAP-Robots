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


def fetch_finance_context() -> dict:
    """
    Holt aktuellen Finance-Kontext aus dem Orchestrator:
    - Letzte 10 Buchungen
    - Aktive Darlehen (aus localStorage-Konfiguration)
    - Aktive Zeitpläne
    - Aktuelle Invoice-Records
    Gibt einen kompakten Text-Kontext für den System-Prompt zurück.
    """
    context_parts = []
    today = datetime.now().strftime("%Y-%m-%d")
    context_parts.append(f"Aktuelles Datum: {today}")

    # Buchungshistorie
    hist = _fetch_url(f"{ORCHESTRATOR_URL}/api/booking-history?limit=10")
    if hist and isinstance(hist, list) and hist:
        lines = []
        for b in hist[:10]:
            lines.append(
                f"  - {b.get('date','?')}: {b.get('tcode','?')} | "
                f"Kunde {b.get('kunnr','?')} | "
                f"ZTERM {b.get('zterm_old','?')}→{b.get('zterm_new','?')} | "
                f"{b.get('status','?')}"
            )
        context_parts.append("Letzte Buchungen (YCONN):\n" + "\n".join(lines))
    else:
        context_parts.append("Buchungshistorie: keine Daten verfügbar.")

    # Zeitpläne
    sched = _fetch_url(f"{ORCHESTRATOR_URL}/api/schedules")
    if sched and isinstance(sched, list):
        active = [s for s in sched if s.get("enabled")]
        if active:
            lines = [f"  - {s.get('name','?')}: {s.get('cron','?')} ({s.get('last_run','nie')})"
                     for s in active[:5]]
            context_parts.append("Aktive Zeitpläne:\n" + "\n".join(lines))

    # Rechnungen diesen Monat
    month = datetime.now().strftime("%Y-%m")
    inv = _fetch_url(f"{ORCHESTRATOR_URL}/api/invoices?month={month}")
    if inv and isinstance(inv, list):
        lines = [f"  - {i.get('subsidiary','?')}: {i.get('amount','?')} EUR, Status={i.get('status','?')}"
                 for i in inv[:5]]
        context_parts.append(f"Rechnungen {month}:\n" + "\n".join(lines))

    return {"text": "\n\n".join(context_parts)}


# ──────────────────────────────────────────────────────────────────────────────
# System-Prompt
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """Du bist Esra – die intelligente Finance-Assistentin von Catensys.
Du antwortest freundlich, professionell und präzise – wie Alexa, aber für SAP und Finance.

Du kannst:
- Fragen zu Buchungshistorie, Zinsbuchungen, Darlehen, Rechnungen beantworten
- SAP-Aktionen ankündigen (Zahlungsbedingungen ändern via XD02/VA42)
- Buchungsstatus und Zeitpläne erklären
- Finance-Begriffe auf Deutsch erklären (SAP, ZTERM, Buchungskreis, etc.)

Dein Name ist Esra. Wenn jemand fragt wer du bist, sagst du: "Ich bin Esra, Ihre Finance-Assistentin von Catensys."
Antworte immer auf Deutsch, kurz und präzise (max 2-3 Sätze – optimiert für Sprachausgabe).
Bei SAP-Aktionen frage immer erst nach Bestätigung bevor du handelst.
Wenn du etwas nicht weißt, sage es ehrlich.

Aktueller Finance-Kontext:
{context}

Erkannte Intents (gib am Ende deiner Antwort in einer neuen Zeile an):
INTENT: [query|sap_action|schedule|invoice|loan|unknown]
ACTION: [optional JSON für Bridge-Aufruf oder null]

Beispiele:
- "Zeige letzte Buchungen" → INTENT: query, ACTION: null
- "Ändere Zahlungsbedingung Maruti auf X004" → INTENT: sap_action, ACTION: {{"method":"GUI","tcode":"XD02_KZTERM","payload":{{"customers":["1012588"],"new_zterm":"X004","bukrs":"0439"}}}}
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
    """Liest KI-Provider + API-Key aus Orchestrator-DB (mit Env-Var-Fallback)."""
    cfg = _fetch_url(f"{ORCHESTRATOR_URL}/ai_config/full")
    if cfg and cfg.get("api_key"):
        return cfg
    # Env-Var-Fallback: Anthropic
    return {
        "provider": "claude",
        "api_key":  os.getenv("ANTHROPIC_API_KEY", "").strip(),
        "model":    "",
    }


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
        log.error("KI API Fehler (%s): %s", provider, e)
        fallback = f"Entschuldigung, der KI-Dienst ({provider}) ist gerade nicht erreichbar. ({e})"
        return {"text": fallback, "intent": keyword_intent, "action": None, "raw": str(e), "provider": provider}

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
    """Extrahiert INTENT: und ACTION: Zeilen aus Claude-Antwort."""
    intent = fallback_intent
    action = None
    lines  = raw.strip().split("\n")
    text_lines = []

    for line in lines:
        ls = line.strip()
        if ls.startswith("INTENT:"):
            intent = ls.replace("INTENT:", "").strip().lower()
        elif ls.startswith("ACTION:"):
            action_str = ls.replace("ACTION:", "").strip()
            if action_str and action_str.lower() != "null":
                try:
                    action = json.loads(action_str)
                except Exception:
                    pass
        else:
            text_lines.append(line)

    clean_text = "\n".join(text_lines).strip()
    if not clean_text:
        clean_text = raw.strip()

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