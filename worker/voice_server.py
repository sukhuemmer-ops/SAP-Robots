"""
YCONN Voice Server – Phase 2 + 3
===================================
FastAPI-Dienst auf Port 8766.

Endpoints:
  GET  /status            — Server-Status (STT, TTS, Wake-Word, Teams)
  POST /transcribe        — Whisper STT: Audio → Text
  POST /synthesize        — TTS: Text → MP3-Audio
  POST /chat              — STT+LLM+TTS komplett
  GET  /voices            — verfügbare TTS-Stimmen
  WS   /ws                — Wake-Word Push + Echtzeit-Chat

Phase 3:
  POST /teams/message     — Teams Outgoing Webhook Empfänger
  POST /teams/send        — Nachricht an Teams senden

Start:
  uvicorn voice_server:app --host 0.0.0.0 --port 8766 --reload

  oder als Teil der Bridge:
  python voice_server.py
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
from typing import Set

import uvicorn
from fastapi import (
    FastAPI, File, Form, Request, Response,
    UploadFile, WebSocket, WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import stt_engine
import tts_engine
import teams_integration
from voice_bot import chat as bot_chat

log = logging.getLogger("voice_server")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-20s %(levelname)s %(message)s",
)

HOST = os.getenv("VOICE_SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("VOICE_SERVER_PORT", "8766"))

app = FastAPI(title="YCONN Voice Server", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket Hub ─────────────────────────────────────────────────────────────

_ws_clients: Set[WebSocket] = set()
_event_loop: asyncio.AbstractEventLoop | None = None


async def _broadcast(msg: dict) -> None:
    dead: Set[WebSocket] = set()
    for ws in list(_ws_clients):
        try:
            await ws.send_json(msg)
        except Exception:
            dead.add(ws)
    _ws_clients -= dead


def broadcast_sync(msg: dict) -> None:
    """Thread-safe broadcast (für Wake-Word-Thread)."""
    if _event_loop and not _event_loop.is_closed():
        asyncio.run_coroutine_threadsafe(_broadcast(msg), _event_loop)


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    global _event_loop
    _event_loop = asyncio.get_event_loop()

    wake_enabled = os.getenv("WAKE_WORD_ENABLED", "1") == "1"
    if wake_enabled:
        try:
            import wake_word_detector
            wake_word_detector.add_callback(
                lambda: broadcast_sync({
                    "type":    "wake_word",
                    "message": "Esra erkannt – bitte sprechen",
                })
            )
            started = wake_word_detector.start()
            if started:
                log.info("Wake-Word Detektor aktiv")
            else:
                log.warning("Wake-Word Detektor nicht verfügbar (SpeechRecognition fehlt)")
        except Exception as e:
            log.warning("Wake-Word Init Fehler: %s", e)

    log.info("YCONN Voice Server gestartet auf %s:%d", HOST, PORT)


# ── Status ────────────────────────────────────────────────────────────────────

@app.get("/status")
def status():
    stt = stt_engine.backend_info()
    tts = tts_engine.backend_info()
    try:
        import wake_word_detector
        ww_running = wake_word_detector.is_running()
    except Exception:
        ww_running = False

    return {
        "status":      "ok",
        "version":     "2.1.0",
        "stt":         stt,
        "tts":         tts,
        "wake_word":   {"running": ww_running, "enabled": os.getenv("WAKE_WORD_ENABLED", "1") == "1"},
        "teams":       teams_integration.config_info(),
        "ws_clients":  len(_ws_clients),
    }


# ── Transkription (STT) ───────────────────────────────────────────────────────

@app.post("/transcribe")
async def transcribe(
    audio:    UploadFile = File(...),
    language: str        = Form("de"),
):
    """
    POST /transcribe
    Body: multipart/form-data
      audio    = Audio-Blob (WebM / WAV / MP3)
      language = ISO-639-1 (default: de)
    Returns: { "text": "...", "language": "de" }
    """
    data = await audio.read()
    if not data:
        return JSONResponse({"error": "Keine Audio-Daten"}, status_code=400)

    if not stt_engine.is_available():
        return JSONResponse(
            {"error": "Whisper nicht installiert. pip install faster-whisper"},
            status_code=503,
        )

    try:
        text = stt_engine.transcribe(data, language=language)
        log.info("STT: '%s'", text[:100])
        return {"text": text, "language": language, "chars": len(text)}
    except Exception as e:
        log.error("STT Fehler: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Sprachsynthese (TTS) ──────────────────────────────────────────────────────

@app.post("/synthesize")
async def synthesize(request: Request):
    """
    POST /synthesize
    Body JSON: { "text": "...", "voice": "de-DE-KatjaNeural" }
    Returns: audio/mpeg
    """
    body  = await request.json()
    text  = (body.get("text") or "").strip()
    voice = body.get("voice") or None

    if not text:
        return JSONResponse({"error": "Kein Text"}, status_code=400)

    if not tts_engine.is_available():
        return JSONResponse(
            {"error": "Kein TTS-Backend. pip install edge-tts"},
            status_code=503,
        )

    try:
        audio = tts_engine.synthesize(text, voice=voice)
        if not audio:
            return JSONResponse({"error": "TTS hat leere Ausgabe"}, status_code=500)
        media_type = "audio/mpeg" if audio[:3] != b"RIF" else "audio/wav"
        return Response(content=audio, media_type=media_type)
    except Exception as e:
        log.error("TTS Fehler: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


# ── Vollständiger Chat (STT + LLM + TTS) ─────────────────────────────────────

@app.post("/chat")
async def chat(request: Request):
    """
    POST /chat
    Body JSON: {
      "text":    "Nutzerfrage (bereits transkribiert)",
      "history": [{role, content}, ...],
      "tts":     true | false
    }
    Returns: {
      "status": "ok",
      "text":   "Antworttext",
      "intent": "query|sap_action|...",
      "action": null | {...},
      "audio_b64":  "<base64 MP3>",   (nur wenn tts=true)
      "audio_type": "audio/mpeg"
    }
    """
    body    = await request.json()
    text    = (body.get("text") or "").strip()
    history = body.get("history") or []
    do_tts  = body.get("tts", True)

    if not text:
        return JSONResponse({"error": "Kein Text"}, status_code=400)

    try:
        result = bot_chat(text, history)
    except Exception as e:
        log.error("Chat Fehler: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)

    response: dict = {
        "status": "ok",
        "text":   result.get("text", ""),
        "intent": result.get("intent", "unknown"),
        "action": result.get("action"),
    }

    if do_tts and tts_engine.is_available():
        try:
            audio = tts_engine.synthesize(result.get("text", ""))
            if audio:
                response["audio_b64"]  = base64.b64encode(audio).decode()
                response["audio_type"] = "audio/mpeg"
        except Exception as e:
            log.warning("TTS in /chat fehlgeschlagen: %s", e)

    return response


# ── TTS-Stimmen ───────────────────────────────────────────────────────────────

@app.get("/voices")
async def voices():
    vlist = tts_engine.list_voices()
    return {"voices": vlist, "current": os.getenv("TTS_VOICE", "de-DE-KatjaNeural")}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Bidirektionaler WebSocket-Kanal.

    Client → Server Nachrichten:
      { "type": "ping" }
      { "type": "chat", "text": "...", "history": [...], "id": "..." }
      { "type": "subscribe", "events": ["wake_word", "sap_result"] }

    Server → Client Nachrichten:
      { "type": "pong" }
      { "type": "wake_word", "message": "..." }
      { "type": "chat_response", "text": "...", "intent": "...", "action": ..., "id": "..." }
      { "type": "sap_result", "tcode": "...", "ok": true, "message": "..." }
    """
    await ws.accept()
    _ws_clients.add(ws)
    client_id = id(ws)
    log.info("WS verbunden: #%s (%d gesamt)", client_id, len(_ws_clients))

    # Willkommens-Nachricht
    await ws.send_json({
        "type":    "connected",
        "message": "YCONN Voice Server verbunden",
        "version": "2.1.0",
    })

    try:
        while True:
            raw  = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            t = msg.get("type")

            if t == "ping":
                await ws.send_json({"type": "pong"})

            elif t == "chat":
                user_text = (msg.get("text") or "").strip()
                history   = msg.get("history") or []
                msg_id    = msg.get("id")

                if not user_text:
                    continue

                try:
                    result = bot_chat(user_text, history)
                    payload: dict = {
                        "type":   "chat_response",
                        "text":   result.get("text", ""),
                        "intent": result.get("intent", "unknown"),
                        "action": result.get("action"),
                        "id":     msg_id,
                    }
                    # Optional: Audio inline
                    if msg.get("tts") and tts_engine.is_available():
                        try:
                            audio = tts_engine.synthesize(result.get("text", ""))
                            if audio:
                                payload["audio_b64"]  = base64.b64encode(audio).decode()
                                payload["audio_type"] = "audio/mpeg"
                        except Exception:
                            pass
                    await ws.send_json(payload)
                except Exception as e:
                    await ws.send_json({"type": "error", "message": str(e), "id": msg_id})

            elif t == "subscribe":
                # Für zukünftige selektive Event-Subscriptions
                await ws.send_json({"type": "subscribed", "events": msg.get("events", [])})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        log.warning("WS Fehler #%s: %s", client_id, e)
    finally:
        _ws_clients.discard(ws)
        log.info("WS getrennt: #%s (%d gesamt)", client_id, len(_ws_clients))


# ── Phase 3: Teams-Endpoints ──────────────────────────────────────────────────

@app.post("/teams/message")
async def teams_incoming(request: Request):
    """
    Teams Outgoing Webhook Empfänger.
    Teams sendet POST wenn jemand @YCONN schreibt.
    """
    body_bytes = await request.body()
    auth       = request.headers.get("Authorization", "")

    # Token verifizieren
    if not teams_integration.verify_teams_token(auth, body_bytes):
        log.warning("Teams: ungültiger Token")
        return JSONResponse({"type": "message", "text": "❌ Ungültige Authentifizierung"})

    try:
        body = json.loads(body_bytes)
    except Exception:
        return JSONResponse({"type": "message", "text": "❌ Ungültiger JSON-Body"})

    # Nachricht extrahieren
    user_text = teams_integration.parse_teams_message(body)
    sender    = body.get("from", {}).get("name", "Teams-Nutzer")

    if not user_text:
        return JSONResponse({"type": "message", "text": "❓ Keine Nachricht erkannt"})

    log.info("Teams-Nachricht von %s: '%s'", sender, user_text[:80])

    # Durch Finance-Assistenten verarbeiten
    try:
        result  = bot_chat(user_text, [])
        reply   = result.get("text", "Keine Antwort")
        intent  = result.get("intent", "unknown")
        action  = result.get("action")

        # SAP-Aktionen ankündigen (Teams kann keine direkten SAP-Aktionen ausführen)
        if intent == "sap_action" and action:
            reply += f"\n\n⚡ *SAP-Aktion erkannt:* `{action.get('tcode', '?')}` – bitte im Cockpit bestätigen."

        # WebSocket-Clients informieren (z.B. offene voice.html)
        await _broadcast({
            "type":    "teams_message",
            "sender":  sender,
            "text":    user_text,
            "reply":   reply,
        })

        # Teams erwartet diese Antwortstruktur
        return {"type": "message", "text": f"🤖 {reply}"}

    except Exception as e:
        log.error("Teams Chat-Fehler: %s", e)
        return JSONResponse({"type": "message", "text": f"❌ Fehler: {e}"})


@app.post("/teams/send")
async def teams_send(request: Request):
    """
    Sendet manuell eine Nachricht an Teams.
    Body: { "text": "...", "title": "..." }
    """
    body  = await request.json()
    text  = (body.get("text") or "").strip()
    title = body.get("title", "")

    if not text:
        return JSONResponse({"error": "Kein Text"}, status_code=400)

    ok = teams_integration.send_message(text, title=title)
    return {"ok": ok, "configured": teams_integration.is_configured()}


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("voice_server:app", host=HOST, port=PORT, reload=False, log_level="info")
     