"""
STT Engine – Whisper (lokal)
=============================
Transkribiert Audio-Bytes zu deutschem Text.

Priorität:
  1. faster-whisper  (pip install faster-whisper)  — schnell, int8
  2. openai-whisper  (pip install openai-whisper)  — Standard
  3. RuntimeError falls nichts installiert

Env:
  WHISPER_MODEL = tiny | base | small | medium | large  (Default: base)
"""
from __future__ import annotations

import logging
import os
import tempfile

log = logging.getLogger("stt_engine")

WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

_model = None
_backend: str = ""   # "faster" | "openai"


# ── Modell laden (lazy, einmalig) ────────────────────────────────────────────

def _load_model():
    global _model, _backend
    if _model is not None:
        return _model

    # 1. faster-whisper
    try:
        from faster_whisper import WhisperModel  # type: ignore
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        _backend = "faster"
        log.info("faster-whisper geladen: Modell=%s", WHISPER_MODEL)
        return _model
    except ImportError:
        pass
    except Exception as e:
        log.warning("faster-whisper Fehler beim Laden: %s", e)

    # 2. openai-whisper
    try:
        import whisper as _ow  # type: ignore
        _model = _ow.load_model(WHISPER_MODEL)
        _backend = "openai"
        log.info("openai-whisper geladen: Modell=%s", WHISPER_MODEL)
        return _model
    except ImportError:
        pass
    except Exception as e:
        log.warning("openai-whisper Fehler beim Laden: %s", e)

    raise RuntimeError(
        "Kein Whisper-Backend gefunden. Bitte installieren:\n"
        "  pip install faster-whisper\n"
        "oder:\n"
        "  pip install openai-whisper"
    )


# ── Öffentliche API ──────────────────────────────────────────────────────────

def transcribe(audio_data: bytes, language: str = "de") -> str:
    """
    Transkribiert Audio-Bytes zu Text.

    Args:
        audio_data: Rohe Audio-Bytes (WebM / WAV / MP3 / OGG)
        language:   ISO-639-1 Sprachcode, Default „de" (Deutsch)

    Returns:
        Transkribierter Text (str), oder "" bei Fehler
    """
    if not audio_data:
        return ""

    model = _load_model()

    # Temp-Datei (Whisper braucht einen Dateipfad)
    suffix = _guess_suffix(audio_data)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_data)
        tmp = f.name

    try:
        if _backend == "faster":
            segments, _ = model.transcribe(
                tmp,
                language=language,
                beam_size=5,
                vad_filter=True,           # Voice Activity Detection
                vad_parameters={"min_silence_duration_ms": 500},
            )
            text = " ".join(s.text for s in segments).strip()
        else:
            # openai-whisper
            result = model.transcribe(tmp, language=language)
            text = (result.get("text") or "").strip()

        log.info("STT [%s] '%s'", _backend, text[:100])
        return text

    except Exception as e:
        log.error("STT Fehler: %s", e)
        return ""
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def is_available() -> bool:
    """True wenn mindestens ein Whisper-Backend geladen werden kann."""
    try:
        _load_model()
        return True
    except RuntimeError:
        return False


def backend_info() -> dict:
    """Gibt Infos über das aktive Backend zurück."""
    try:
        _load_model()
        return {"backend": _backend, "model": WHISPER_MODEL, "ok": True}
    except RuntimeError as e:
        return {"backend": None, "model": WHISPER_MODEL, "ok": False, "error": str(e)}


# ── Interne Hilfsfunktionen ──────────────────────────────────────────────────

def _guess_suffix(data: bytes) -> str:
    """Erkennt Audio-Format anhand Magic Bytes."""
    if data[:4] == b"RIFF":
        return ".wav"
    if data[:3] == b"ID3" or data[:2] == b"\xff\xfb":
        return ".mp3"
    if data[:4] == b"OggS":
        return ".ogg"
    if data[:4] == b"fLaC":
        return ".flac"
    # WebM / EBML
    if data[:4] == b"\x1a\x45\xdf\xa3":
        return ".webm"
    return ".webm"   # Browser-Standard
