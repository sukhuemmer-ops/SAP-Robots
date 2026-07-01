"""
Teams-Integration – Phase 3
=============================
Bidirektionale Microsoft Teams-Anbindung für den YCONN Finance-Assistenten.

AUSGEHEND (YCONN → Teams):
  send_to_teams(text, title)  → postet eine adaptive Card in den konfigurierten Kanal

EINGEHEND (Teams → YCONN):
  POST /teams/message wird vom voice_server.py bereitgestellt.
  Teams-Outgoing-Webhook sendet JSON an diese URL.
  YCONN verarbeitet via voice_bot.chat() und antwortet.

Setup:
  1. Teams → Kanal → ··· → Connectors → "Eingehender Webhook"
     → URL kopieren → TEAMS_WEBHOOK_URL in .env eintragen
  2. Teams → Kanal → ··· → Connectors → "Ausgehender Webhook"
     → Callback-URL: http://<YCONN-IP>:8766/teams/message
     → Token in TEAMS_BOT_TOKEN eintragen

Env:
  TEAMS_WEBHOOK_URL  — URL für ausgehende Nachrichten (YCONN→Teams)
  TEAMS_BOT_TOKEN    — HMAC-Token zur Verifikation eingehender Teams-Nachrichten
  TEAMS_BOT_NAME     — Name des Bots in Teams (Default: YCONN)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import urllib.request
from datetime import datetime

log = logging.getLogger("teams_integration")

TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")
TEAMS_BOT_TOKEN:   str = os.getenv("TEAMS_BOT_TOKEN",   "")
TEAMS_BOT_NAME:    str = os.getenv("TEAMS_BOT_NAME",    "YCONN Finance-Assistent")


# ── Ausgehend: YCONN → Teams ─────────────────────────────────────────────────

def send_message(text: str, title: str = "", color: str = "0076D7") -> bool:
    """
    Sendet eine Nachricht als Adaptive Card an Teams.

    Args:
        text:  Nachrichtentext (Markdown erlaubt)
        title: Optionaler Titel
        color: Hex-Farbe der Card (0076D7=blau, 28a745=grün, dc3545=rot)

    Returns:
        True bei Erfolg
    """
    if not TEAMS_WEBHOOK_URL:
        log.warning("TEAMS_WEBHOOK_URL nicht konfiguriert – Nachricht nicht gesendet")
        return False

    _title = title or TEAMS_BOT_NAME
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    # MessageCard Format (kompatibel mit allen Teams-Versionen)
    card = {
        "@type":      "MessageCard",
        "@context":   "http://schema.org/extensions",
        "themeColor": color,
        "summary":    _title,
        "sections": [{
            "activityTitle":    f"🤖 {_title}",
            "activitySubtitle": timestamp,
            "text":             text,
            "markdown":         True,
        }],
    }

    try:
        payload = json.dumps(card, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            TEAMS_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            if body.strip() == "1":
                log.info("Teams-Nachricht gesendet (%d Zeichen)", len(text))
                return True
            log.warning("Teams-Antwort: %s", body[:100])
            return False
    except Exception as e:
        log.error("Teams-Fehler: %s", e)
        return False


def send_sap_result(tcode: str, result: str, ok: bool = True) -> bool:
    """Sendet SAP-Aktionsergebnis formatiert an Teams."""
    icon  = "✅" if ok else "❌"
    color = "28a745" if ok else "dc3545"
    text  = f"**Transaktion:** `{tcode}`\n\n{icon} {result}"
    return send_message(text, title=f"SAP-Aktion: {tcode}", color=color)


def send_booking_summary(bookings: list[dict]) -> bool:
    """Sendet Buchungszusammenfassung an Teams."""
    if not bookings:
        return send_message("Keine Buchungen vorhanden.", title="Buchungsübersicht")
    lines = [f"| Datum | Transaktion | Status |", "| --- | --- | --- |"]
    for b in bookings[:10]:
        lines.append(
            f"| {b.get('date','?')} | {b.get('tcode','?')} | {b.get('status','?')} |"
        )
    text = "\n".join(lines)
    return send_message(text, title=f"Buchungsübersicht ({len(bookings)} Einträge)")


# ── Eingehend: Teams → YCONN (Token-Verifikation) ────────────────────────────

def verify_teams_token(auth_header: str, body: bytes) -> bool:
    """
    Verifiziert die HMAC-Signatur eines eingehenden Teams Outgoing Webhook.

    Args:
        auth_header: Wert des Authorization-Headers
        body:        Roher Request-Body als Bytes

    Returns:
        True wenn Signatur korrekt
    """
    if not TEAMS_BOT_TOKEN:
        log.warning("TEAMS_BOT_TOKEN nicht konfiguriert – Token-Verifikation übersprungen")
        return True   # Im Dev-Modus durchlassen

    try:
        # Teams sendet: "HMAC <base64-hash>"
        if not auth_header.startswith("HMAC "):
            return False
        received_b64 = auth_header[5:].strip()

        import base64
        key   = base64.b64decode(TEAMS_BOT_TOKEN)
        mac   = hmac.new(key, body, hashlib.sha256)
        expected_b64 = base64.b64encode(mac.digest()).decode()

        return hmac.compare_digest(received_b64, expected_b64)
    except Exception as e:
        log.error("Token-Verifikation Fehler: %s", e)
        return False


def parse_teams_message(body: dict) -> str:
    """Extrahiert den Nachrichtentext aus einem Teams Outgoing Webhook Payload."""
    # Teams sendet text mit HTML-Tags (<at>BotName</at> Nachricht)
    text = body.get("text") or ""

    # <at>...</at> Tag entfernen (Bot-Mention)
    import re
    text = re.sub(r"<at[^>]*>.*?</at>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)   # alle HTML-Tags
    text = " ".join(text.split()).strip()   # Whitespace normalisieren

    return text


# ── Status ───────────────────────────────────────────────────────────────────

def is_configured() -> bool:
    return bool(TEAMS_WEBHOOK_URL)


def config_info() -> dict:
    return {
        "webhook_url":  bool(TEAMS_WEBHOOK_URL),
        "bot_token":    bool(TEAMS_BOT_TOKEN),
        "bot_name":     TEAMS_BOT_NAME,
        "configured":   is_configured(),
    }
