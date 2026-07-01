"""
Wake-Word Detektor – „Hey YCONN"
==================================
Hintergrund-Thread der permanent auf das Mikrofon lauscht.
Bei Erkennung eines Wake-Words werden alle registrierten Callbacks
aufgerufen (z.B. WebSocket-Broadcast im voice_server).

Abhängigkeiten:
  pip install SpeechRecognition pyaudio

Env:
  WAKE_WORD_ENABLED   = 1 | 0           (Default: 1)
  WAKE_WORD_THRESHOLD = 300             (Energie-Schwellwert)
  WAKE_WORD_TIMEOUT   = 5              (Sekunden bis Timeout)
"""
from __future__ import annotations

import logging
import os
import threading
import time
from typing import Callable

log = logging.getLogger("wake_word")

# Varianten, die erkannt werden sollen (alles Kleinbuchstaben)
WAKE_WORDS: list[str] = [
    "hey elsa", "hallo elsa", "hi elsa",
    "elsa",
    "okay elsa", "ok elsa",
    "else",   # phonetische Variante (de-DE STT)
    "elza",   # phonetische Variante
]

ENERGY_THRESHOLD: int = int(os.getenv("WAKE_WORD_THRESHOLD", "300"))
LISTEN_TIMEOUT:   int = int(os.getenv("WAKE_WORD_TIMEOUT",   "5"))

_running   = False
_thread: threading.Thread | None = None
_callbacks: list[Callable[[], None]] = []
_lock = threading.Lock()


# ── Öffentliche API ──────────────────────────────────────────────────────────

def add_callback(fn: Callable[[], None]) -> None:
    """Registriert eine Funktion die bei Wake-Word-Erkennung aufgerufen wird."""
    with _lock:
        if fn not in _callbacks:
            _callbacks.append(fn)


def remove_callback(fn: Callable[[], None]) -> None:
    with _lock:
        _callbacks[:] = [c for c in _callbacks if c is not fn]


def start() -> bool:
    """Startet den Detektor-Thread. Gibt False zurück wenn nicht verfügbar."""
    global _running, _thread
    if _running:
        return True
    if not _check_deps():
        return False
    _running = True
    _thread = threading.Thread(target=_detect_loop, daemon=True, name="wake-word-detector")
    _thread.start()
    log.info("Elsa Wake-Word Detektor gestartet (Schwelle=%d)", ENERGY_THRESHOLD)
    return True


def stop() -> None:
    global _running
    _running = False
    log.info("Wake-Word Detektor gestoppt")


def is_running() -> bool:
    return _running and (_thread is not None) and _thread.is_alive()


# ── Interne Logik ─────────────────────────────────────────────────────────────

def _notify() -> None:
    with _lock:
        cbs = list(_callbacks)
    for fn in cbs:
        try:
            fn()
        except Exception as e:
            log.warning("Wake-word Callback Fehler: %s", e)


def _check_deps() -> bool:
    try:
        import speech_recognition  # type: ignore  # noqa: F401
        return True
    except ImportError:
        log.warning(
            "speech_recognition nicht installiert – Wake-Word deaktiviert.\n"
            "  pip install SpeechRecognition pyaudio"
        )
        return False


def _detect_loop() -> None:
    global _running
    try:
        import speech_recognition as sr  # type: ignore
    except ImportError:
        _running = False
        return

    r = sr.Recognizer()
    r.energy_threshold       = ENERGY_THRESHOLD
    r.dynamic_energy_threshold = True
    r.pause_threshold        = 0.6

    # Mikrofon öffnen
    try:
        mic = sr.Microphone()
    except Exception as e:
        log.error("Mikrofon nicht gefunden: %s", e)
        _running = False
        return

    # Umgebungsgeräusche kalibrieren
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1.5)
        log.info("Mikrofon kalibriert (Schwelle jetzt: %.0f)", r.energy_threshold)
    except Exception as e:
        log.warning("Kalibrierung fehlgeschlagen: %s", e)

    log.info("Lausche auf Wake-Words: %s", WAKE_WORDS[:4])

    while _running:
        try:
            with mic as source:
                try:
                    audio = r.listen(
                        source,
                        timeout=LISTEN_TIMEOUT,
                        phrase_time_limit=4,
                    )
                except sr.WaitTimeoutError:
                    continue

            # Online-Erkennung (Google, schnell)
            text = ""
            try:
                text = r.recognize_google(audio, language="de-DE").lower()
                log.debug("Wake-check: '%s'", text)
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                # Kein Internet → Sphinx Fallback
                try:
                    text = r.recognize_sphinx(audio, language="de-de").lower()
                except Exception:
                    pass
            except Exception as e:
                log.debug("Erkennungs-Fehler: %s", e)

            if text and any(w in text for w in WAKE_WORDS):
                log.info("🎤 Wake-Word erkannt: '%s'", text)
                _notify()

        except Exception as e:
            log.warning("Wake-loop Fehler: %s", e)
            time.sleep(2)

    log.info("Wake-Word Detektor beendet")
