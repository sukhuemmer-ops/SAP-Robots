"""
TTS Engine – Text-to-Speech
=============================
Synthetisiert deutschen Text zu Audio-MP3-Bytes.

Priorität:
  1. edge-tts   (pip install edge-tts)   — Microsoft Edge TTS, hohe Qualität, braucht Internet
  2. pyttsx3    (pip install pyttsx3)    — Windows SAPI, offline, geringere Qualität
  3. Leere bytes (kein TTS verfügbar)

Env:
  TTS_VOICE   = de-DE-KatjaNeural | de-DE-ConradNeural | ...  (Default: de-DE-KatjaNeural)
  TTS_RATE    = +0% | +20% | -10%   (Sprechgeschwindigkeit)
  TTS_VOLUME  = +0% | +10%          (Lautstärke)
"""
from __future__ import annotations

import asyncio
import io
import logging
import os
import tempfile

log = logging.getLogger("tts_engine")

TTS_VOICE:  str = os.getenv("TTS_VOICE",  "de-DE-KatjaNeural")
TTS_RATE:   str = os.getenv("TTS_RATE",   "+0%")
TTS_VOLUME: str = os.getenv("TTS_VOLUME", "+0%")

# Max Zeichen für Sprachausgabe (vermeidet sehr lange Audio-Generierung)
MAX_CHARS = 400


# ── edge-tts ─────────────────────────────────────────────────────────────────

async def _edge_tts_async(text: str, voice: str) -> bytes:
    import edge_tts  # type: ignore
    buf = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice, rate=TTS_RATE, volume=TTS_VOLUME)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


def _synthesize_edge(text: str, voice: str) -> bytes:
    try:
        loop = asyncio.new_event_loop()
        data = loop.run_until_complete(_edge_tts_async(text, voice))
        loop.close()
        return data
    except Exception as e:
        log.warning("edge-tts Fehler: %s", e)
        return b""


# ── pyttsx3 (Windows SAPI Fallback) ──────────────────────────────────────────

def _synthesize_pyttsx3(text: str) -> bytes:
    try:
        import pyttsx3  # type: ignore
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        # Deutsche Stimme suchen
        for v in engine.getProperty("voices"):
            name = getattr(v, "name", "") or ""
            if any(k in name.lower() for k in ("german", "deutsch", "helena", "katja", "anna")):
                engine.setProperty("voice", v.id)
                break
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        engine.save_to_file(text, tmp)
        engine.runAndWait()
        with open(tmp, "rb") as f:
            data = f.read()
        os.unlink(tmp)
        log.info("pyttsx3 TTS: %d Bytes", len(data))
        return data
    except Exception as e:
        log.warning("pyttsx3 Fehler: %s", e)
        return b""


# ── Öffentliche API ──────────────────────────────────────────────────────────

def synthesize(text: str, voice: str | None = None) -> bytes:
    """
    Synthetisiert Text zu Audio-Bytes.

    Args:
        text:  Zu sprechender Text
        voice: Optional TTS-Stimme (überschreibt TTS_VOICE aus .env)

    Returns:
        Audio-Bytes (MP3 bei edge-tts, WAV bei pyttsx3), oder b"" bei Fehler
    """
    text = (text or "").strip()
    if not text:
        return b""

    # Kürzen falls zu lang
    if len(text) > MAX_CHARS:
        # Abschneiden am letzten Satzzeichen
        cut = text[:MAX_CHARS].rfind(".")
        if cut < MAX_CHARS // 2:
            cut = MAX_CHARS
        text = text[:cut].strip()

    _voice = voice or TTS_VOICE

    # 1. edge-tts versuchen
    try:
        import edge_tts  # type: ignore  # noqa: F401
        data = _synthesize_edge(text, _voice)
        if data:
            log.info("TTS (edge-tts / %s): %d Zeichen → %d Bytes", _voice, len(text), len(data))
            return data
    except ImportError:
        pass

    # 2. pyttsx3 Fallback
    try:
        import pyttsx3  # type: ignore  # noqa: F401
        data = _synthesize_pyttsx3(text)
        if data:
            log.info("TTS (pyttsx3): %d Zeichen → %d Bytes", len(text), len(data))
        return data
    except ImportError:
        pass

    log.warning("Kein TTS-Backend verfügbar")
    return b""


def is_available() -> bool:
    """True wenn edge-tts oder pyttsx3 installiert ist."""
    try:
        import edge_tts  # type: ignore  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        import pyttsx3  # type: ignore  # noqa: F401
        return True
    except ImportError:
        pass
    return False


async def list_voices_async() -> list[dict]:
    """Listet verfügbare edge-tts Stimmen auf (Deutsch bevorzugt)."""
    try:
        import edge_tts  # type: ignore
        voices = await edge_tts.list_voices()
        de = [v for v in voices if v.get("Locale", "").startswith("de")]
        return de
    except Exception:
        return []


def list_voices() -> list[dict]:
    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(list_voices_async())
        loop.close()
        return result
    except Exception:
        return []


def backend_info() -> dict:
    backends = []
    try:
        import edge_tts  # type: ignore  # noqa: F401
        backends.append("edge-tts")
    except ImportError:
        pass
    try:
        import pyttsx3  # type: ignore  # noqa: F401
        backends.append("pyttsx3")
    except ImportError:
        pass
    return {
        "backends": backends,
        "active":   backends[0] if backends else None,
        "voice":    TTS_VOICE,
        "rate":     TTS_RATE,
        "ok":       bool(backends),
    }
