"""
ESRA – Intelligenter SAP/YCONN Assistent
=========================================
Python Desktop-App mit:
  • Ollama (lokal, kostenlos) als primären LLM
  • OpenAI GPT-4o-mini als Fallback
  • Sprachsteuerung via Mikrofon (SpeechRecognition)
  • Text-to-Speech via edge-tts
  • YCONN Orchestrator-API Integration
  • Intelligenter Router Ollama → OpenAI
"""

import os
import json
import time
import threading
import asyncio
import tempfile
import requests
import customtkinter as ctk
import speech_recognition as sr
from datetime import datetime

# ─── Konfigurationsdatei ──────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esra_config.json")

def _load_config() -> dict:
    """Lädt gespeicherte Einstellungen aus esra_config.json."""
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_config(cfg: dict):
    """Speichert Einstellungen nach esra_config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def _list_mic_devices() -> list:
    """Gibt verfügbare Mikrofon-Geräte zurück: [(index, name), ...]"""
    devices = []
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                devices.append((i, info["name"]))
        pa.terminate()
    except Exception:
        pass
    return devices

_cfg = _load_config()

# ─── Konfiguration ────────────────────────────────────────────
OLLAMA_URL    = _cfg.get("ollama_url",   os.getenv("OLLAMA_URL",   "http://localhost:11434"))
OLLAMA_MODEL  = _cfg.get("ollama_model", os.getenv("OLLAMA_MODEL", "llama3.2"))
ORCH_URL      = _cfg.get("orch_url",     os.getenv("ORCH_URL",     "http://localhost:8000"))
OPENAI_KEY    = _cfg.get("openai_key",   os.getenv("OPENAI_API_KEY", ""))
CLAUDE_KEY    = _cfg.get("claude_key",   os.getenv("ANTHROPIC_API_KEY", ""))
CLAUDE_MODEL  = _cfg.get("claude_model", os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"))
TTS_VOICE     = os.getenv("ESRA_VOICE",  "de-DE-KatjaNeural")
TTS_ENABLED   = os.getenv("ESRA_TTS",    "1") == "1"

SYSTEM_PROMPT = """Du bist Esra, eine intelligente Assistentin für das YCONN SAP Finance-Cockpit.
Du hilfst dem Benutzer mit Fragen zu Rechnungen, Buchungen, SAP-Daten und dem Cockpit-System.
Antworte immer auf Deutsch, präzise, freundlich und kompakt (max. 3-4 Sätze wenn möglich).

Wenn der Benutzer nach Rechnungsdaten fragt, werden dir automatisch aktuelle Daten aus YCONN
im Kontext mitgegeben – nutze diese für eine präzise Antwort.

Vermeide lange Listen – antworte in natürlicher Sprache."""

# ─── Themes ───────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "bg3":       "#21262d",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "blue":      "#58a6ff",
    "green":     "#3fb950",
    "red":       "#f85149",
    "amber":     "#e3b341",
    "bubble_ai": "#1c2128",
    "bubble_me": "#1a3a5c",
    "accent":    "#1f6feb",
}


# ══════════════════════════════════════════════════════════════
# LLM Router: Ollama → OpenAI
# ══════════════════════════════════════════════════════════════
class EsraRouter:

    def __init__(self):
        self.ollama_ok  = False
        self.openai_ok  = bool(OPENAI_KEY)
        self.claude_ok  = bool(CLAUDE_KEY)
        self._check_ollama()

    def _check_ollama(self):
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            if r.ok:
                models = [m["name"] for m in r.json().get("models", [])]
                self.ollama_ok = True
                self._ollama_models = models
        except Exception:
            self.ollama_ok = False

    def status(self) -> dict:
        return {"ollama": self.ollama_ok, "openai": self.openai_ok, "claude": self.claude_ok}

    def query(self, messages: list, on_chunk=None) -> str:
        """Ollama → Claude → OpenAI (Auto-Fallback)."""
        if self.ollama_ok:
            try:
                return self._ollama_chat(messages, on_chunk)
            except Exception as e:
                print(f"[Router] Ollama Fehler ({e}) → Claude/OpenAI")
        if self.claude_ok:
            try:
                return self._claude_chat(messages, on_chunk)
            except Exception as e:
                print(f"[Router] Claude Fehler ({e}) → OpenAI")
        if self.openai_ok:
            return self._openai_chat(messages, on_chunk)
        return ("⚠ Kein LLM verfügbar.\n"
                "→ Ollama: ollama serve\n"
                "→ Claude/OpenAI: API Key in ⚙ Einstellungen eintragen.")

    def _ollama_chat(self, messages: list, on_chunk=None) -> str:
        payload = {
            "model":    OLLAMA_MODEL,
            "messages": messages,
            "stream":   bool(on_chunk),
        }
        if on_chunk:
            with requests.post(
                f"{OLLAMA_URL}/api/chat", json=payload,
                stream=True, timeout=120
            ) as resp:
                resp.raise_for_status()
                full = ""
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        data  = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            full += chunk
                            on_chunk(chunk)
                        if data.get("done"):
                            break
                    except Exception:
                        pass
                return full
        else:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat", json=payload, timeout=120
            )
            r.raise_for_status()
            return r.json()["message"]["content"]

    def _openai_chat(self, messages: list, on_chunk=None) -> str:
        import openai
        client = openai.OpenAI(api_key=OPENAI_KEY)
        if on_chunk:
            stream = client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, stream=True
            )
            full = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full += delta
                    on_chunk(delta)
            return full
        resp = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages
        )
        return resp.choices[0].message.content

    def _claude_chat(self, messages: list, on_chunk=None) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_KEY)

        # Anthropic-API trennt system-Nachricht von messages
        system_msg = ""
        chat_msgs  = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                chat_msgs.append({"role": m["role"], "content": m["content"]})

        if on_chunk:
            full = ""
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=system_msg,
                messages=chat_msgs,
            ) as stream:
                for delta in stream.text_stream:
                    full += delta
                    on_chunk(delta)
            return full
        else:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=system_msg,
                messages=chat_msgs,
            )
            return resp.content[0].text


# ══════════════════════════════════════════════════════════════
# YCONN Orchestrator Client
# ══════════════════════════════════════════════════════════════
class YCONNClient:

    def ping(self) -> bool:
        try:
            requests.get(f"{ORCH_URL}/invoice_records", timeout=2)
            return True
        except Exception:
            return False

    def invoice_stats(self) -> dict:
        try:
            r   = requests.get(f"{ORCH_URL}/invoice_records", timeout=5)
            rec = r.json()
            offen    = [x for x in rec if x.get("status") == "offen"]
            erstellt = [x for x in rec if x.get("status") == "erstellt"]

            def _sum(rows):
                total = 0
                for x in rows:
                    for p in x.get("positions", []):
                        total += float(p.get("betrag", 0) or 0)
                return total

            # Perioden offener Rechnungen
            perioden = sorted({x.get("periode", "") for x in offen if x.get("periode")})

            return {
                "ok": True,
                "total":             len(rec),
                "offen":             len(offen),
                "erstellt":          len(erstellt),
                "sum_offen_eur":     _sum(offen),
                "sum_erstellt_eur":  _sum(erstellt),
                "perioden_offen":    perioden,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def build_context(self, user_msg: str) -> str:
        """Hängt Live-Daten an den Prompt wenn der User nach Rechnungen fragt."""
        keywords = ["rechnung", "offen", "erstellt", "betrag", "invoice",
                    "buchen", "buchung", "periode", "kunden"]
        if not any(k in user_msg.lower() for k in keywords):
            return ""
        stats = self.invoice_stats()
        if not stats["ok"]:
            return f"\n\n[YCONN nicht erreichbar: {stats['error']}]"
        p = ", ".join(stats["perioden_offen"]) or "–"
        return (
            f"\n\n[Live-Daten aus YCONN – {datetime.now().strftime('%H:%M')}]\n"
            f"• Rechnungen gesamt: {stats['total']}\n"
            f"• Offen: {stats['offen']} Stück  |  Summe: {stats['sum_offen_eur']:,.2f} EUR\n"
            f"• Erstellt: {stats['erstellt']} Stück  |  Summe: {stats['sum_erstellt_eur']:,.2f} EUR\n"
            f"• Offene Perioden: {p}"
        )


# ══════════════════════════════════════════════════════════════
# TTS (edge-tts + pygame)
# ══════════════════════════════════════════════════════════════
class EsraTTS:

    def __init__(self):
        self._lock = threading.Lock()

    def speak(self, text: str):
        if not TTS_ENABLED:
            return
        threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()

    def _speak_thread(self, text: str):
        with self._lock:
            # Markdown-Symbole und zu langer Text entfernen
            clean = (text.replace("**", "").replace("*", "")
                        .replace("#", "").replace("`", "").strip())
            if len(clean) > 500:
                clean = clean[:500] + "…"
            if not clean:
                return
            try:
                import edge_tts

                async def _gen():
                    com = edge_tts.Communicate(clean, voice=TTS_VOICE)
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                        await com.save(f.name)
                        return f.name

                tmp = asyncio.run(_gen())
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(tmp)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)
                    pygame.mixer.quit()
                except ImportError:
                    os.startfile(tmp)  # Fallback: Windows Mediaplayer
                finally:
                    try:
                        os.unlink(tmp)
                    except Exception:
                        pass
            except Exception as e:
                print(f"[TTS] Fehler: {e}")


# ══════════════════════════════════════════════════════════════
# Einstellungen-Dialog
# ══════════════════════════════════════════════════════════════
class EsraSettings(ctk.CTkToplevel):
    """Modaler Einstellungs-Dialog für Ollama, OpenAI und Mikrofon."""

    _MIC_DEFAULT = "(Standard – Systemvorgabe)"

    def __init__(self, parent: "EsraApp"):
        super().__init__(parent)
        self._parent = parent
        self.title("⚙ Einstellungen – ESRA")
        self.geometry("520x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR["bg2"])
        self.grab_set()
        self.focus_force()
        self.after(50, self._center)
        self._mic_devices = _list_mic_devices()  # [(index, name), ...]
        self._build()

    def _center(self):
        self.update_idletasks()
        pw = self._parent.winfo_x() + self._parent.winfo_width() // 2
        ph = self._parent.winfo_y() + self._parent.winfo_height() // 2
        w, h = 520, 560
        self.geometry(f"{w}x{h}+{pw - w//2}+{ph - h//2}")

    def _build(self):
        pad = {"padx": 28, "pady": 8}

        # ── Titel ──
        ctk.CTkLabel(
            self, text="⚙  Verbindungs-Einstellungen",
            font=("Segoe UI", 15, "bold"), text_color=COLOR["blue"]
        ).pack(**pad, anchor="w", pady=(20, 4))

        ctk.CTkFrame(self, height=1, fg_color=COLOR["border"]).pack(fill="x", padx=28, pady=(0, 8))

        def _row(label, default, show=""):
            ctk.CTkLabel(
                self, text=label,
                font=("Segoe UI", 12), text_color=COLOR["muted"]
            ).pack(padx=28, anchor="w", pady=(6, 0))
            e = ctk.CTkEntry(
                self, width=460, height=38,
                font=("Segoe UI", 12),
                fg_color=COLOR["bg3"], border_color=COLOR["border"],
                text_color=COLOR["text"], show=show,
            )
            e.insert(0, default)
            e.pack(padx=28, pady=(2, 0))
            return e

        self._e_url   = _row("Ollama URL", OLLAMA_URL)
        self._e_model = _row("Ollama Modell", OLLAMA_MODEL)
        self._e_key   = _row("OpenAI API Key (optional)", OPENAI_KEY, show="•")
        self._e_claude = _row("Claude (Anthropic) API Key (optional)", CLAUDE_KEY, show="•")

        # ── Mikrofon-Sektion ──
        ctk.CTkFrame(self, height=1, fg_color=COLOR["border"]).pack(fill="x", padx=28, pady=(14, 8))

        ctk.CTkLabel(
            self, text="🎤  Mikrofon-Zugriff",
            font=("Segoe UI", 13, "bold"), text_color=COLOR["blue"]
        ).pack(padx=28, anchor="w")

        ctk.CTkLabel(
            self, text="Gerät einmal auswählen – wird dauerhaft gespeichert",
            font=("Segoe UI", 11), text_color=COLOR["muted"]
        ).pack(padx=28, anchor="w", pady=(0, 6))

        # Dropdown mit Geräteliste
        mic_names = [self._MIC_DEFAULT] + [n for _, n in self._mic_devices]
        saved_idx = _cfg.get("mic_device_index", None)
        saved_name = self._MIC_DEFAULT
        if saved_idx is not None:
            for idx, name in self._mic_devices:
                if idx == saved_idx:
                    saved_name = name
                    break

        self._mic_var = ctk.StringVar(value=saved_name)
        self._mic_menu = ctk.CTkOptionMenu(
            self, values=mic_names,
            variable=self._mic_var,
            width=460, height=38,
            font=("Segoe UI", 12),
            fg_color=COLOR["bg3"],
            button_color=COLOR["accent"],
            button_hover_color="#388bfd",
            dropdown_fg_color=COLOR["bg3"],
            dropdown_text_color=COLOR["text"],
            text_color=COLOR["text"],
        )
        self._mic_menu.pack(padx=28, pady=(0, 4))

        # Test-Button
        ctk.CTkButton(
            self, text="🎙 Mikrofon testen", width=200, height=34,
            font=("Segoe UI", 11),
            fg_color=COLOR["bg3"], hover_color=COLOR["border"],
            text_color=COLOR["muted"],
            command=self._test_mic
        ).pack(padx=28, anchor="w", pady=(4, 0))

        self._mic_status = ctk.CTkLabel(
            self, text="",
            font=("Segoe UI", 11), text_color=COLOR["muted"]
        )
        self._mic_status.pack(padx=28, anchor="w")

        # ── Buttons ──
        ctk.CTkFrame(self, height=1, fg_color=COLOR["border"]).pack(fill="x", padx=28, pady=(14, 8))

        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.pack(padx=28, pady=(0, 16), fill="x")

        ctk.CTkButton(
            btn_f, text="✕  Abbrechen", width=140, height=38,
            fg_color=COLOR["bg3"], hover_color=COLOR["border"],
            text_color=COLOR["muted"], font=("Segoe UI", 12),
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_f, text="💾  Speichern", width=140, height=38,
            fg_color="#238636", hover_color="#2ea043",
            text_color="#ffffff", font=("Segoe UI", 12, "bold"),
            command=self._save
        ).pack(side="right")

    def _test_mic(self):
        """Kurzer Mikrofon-Test im Hintergrund."""
        def _run():
            try:
                import pyaudio, wave, tempfile
                dev_idx = self._selected_device_index()
                pa = pyaudio.PyAudio()
                stream = pa.open(
                    format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, input_device_index=dev_idx,
                    frames_per_buffer=1024
                )
                frames = [stream.read(1024) for _ in range(10)]
                stream.stop_stream(); stream.close(); pa.terminate()
                # Prüfen ob Signal vorhanden (nicht nur Stille)
                import struct
                samples = struct.unpack(f"{len(frames[0])//2 * len(frames)}h",
                                        b"".join(frames))
                level = max(abs(s) for s in samples)
                if level > 50:
                    msg = f"✅ Mikrofon OK (Pegel: {level})"
                    color = COLOR["green"]
                else:
                    msg = f"⚠ Kein Signal – Mikrofon stumm? (Pegel: {level})"
                    color = COLOR["amber"]
            except Exception as e:
                msg = f"❌ Fehler: {e}"
                color = COLOR["red"]
            self.after(0, lambda: self._mic_status.configure(text=msg, text_color=color))

        self._mic_status.configure(text="⏳ Teste…", text_color=COLOR["muted"])
        threading.Thread(target=_run, daemon=True).start()

    def _selected_device_index(self):
        """Gibt den Index des gewählten Geräts zurück (None = Standard)."""
        sel = self._mic_var.get()
        if sel == self._MIC_DEFAULT:
            return None
        for idx, name in self._mic_devices:
            if name == sel:
                return idx
        return None

    def _save(self):
        global OLLAMA_URL, OLLAMA_MODEL, OPENAI_KEY, CLAUDE_KEY

        new_url    = self._e_url.get().strip()
        new_model  = self._e_model.get().strip()
        new_key    = self._e_key.get().strip()
        new_claude = self._e_claude.get().strip()

        if not new_url:
            self._e_url.configure(border_color=COLOR["red"])
            return
        if not new_model:
            self._e_model.configure(border_color=COLOR["red"])
            return

        OLLAMA_URL  = new_url
        OLLAMA_MODEL = new_model
        OPENAI_KEY  = new_key
        CLAUDE_KEY  = new_claude

        mic_idx = self._selected_device_index()

        _save_config({
            "ollama_url":       OLLAMA_URL,
            "ollama_model":     OLLAMA_MODEL,
            "orch_url":         ORCH_URL,
            "openai_key":       OPENAI_KEY,
            "claude_key":       CLAUDE_KEY,
            "mic_device_index": mic_idx,
        })

        # Router neu initialisieren (liest neue Keys)
        self._parent.router = EsraRouter()
        # Mikrofon-Index sofort anwenden
        self._parent._mic_device_index = mic_idx
        self._parent.after(0, self._parent._refresh_status)

        mic_label  = self._mic_var.get()
        llm_status = []
        if OLLAMA_URL:   llm_status.append(f"Ollama: {OLLAMA_URL}")
        if CLAUDE_KEY:   llm_status.append("Claude: ✓")
        if OPENAI_KEY:   llm_status.append("OpenAI: ✓")
        self.destroy()
        self._parent.after(100, lambda: self._parent._write(
            f"\n✅ Einstellungen gespeichert\n"
            f"   {' | '.join(llm_status)}\n"
            f"   Mikrofon: {mic_label}\n",
            "system_tag"
        ))


# ══════════════════════════════════════════════════════════════
# Haupt-App
# ══════════════════════════════════════════════════════════════
class EsraApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("ESRA – Intelligenter SAP Assistent")
        self.geometry("900x680")
        self.minsize(680, 500)
        self.configure(fg_color=COLOR["bg"])

        self.router  = EsraRouter()
        self.yconn   = YCONNClient()
        self.tts     = EsraTTS()
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold  = 0.8
        self.recognizer.energy_threshold = 300
        self._listening  = False
        self._processing = False
        # Gespeicherter Mikrofon-Geräte-Index (None = Systemvorgabe)
        self._mic_device_index = _cfg.get("mic_device_index", None)

        self._stream_marker = None   # Textbox-Position für Streaming

        self._build_ui()
        self._refresh_status()
        self._greet()

    # ── UI aufbauen ───────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=COLOR["bg2"], corner_radius=0, height=58)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(
            hdr, text="🤖", font=("Segoe UI Emoji", 28)
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        title_f = ctk.CTkFrame(hdr, fg_color="transparent")
        title_f.grid(row=0, column=1, sticky="w", pady=6)
        ctk.CTkLabel(
            title_f, text="ESRA",
            font=("Segoe UI", 18, "bold"), text_color=COLOR["blue"]
        ).pack(side="left")
        ctk.CTkLabel(
            title_f, text="  Intelligenter SAP Assistent",
            font=("Segoe UI", 12), text_color=COLOR["muted"]
        ).pack(side="left", pady=2)

        # Status-Chips
        chip_f = ctk.CTkFrame(hdr, fg_color="transparent")
        chip_f.grid(row=0, column=2, padx=(14, 6), pady=10)
        self._chip_ollama = self._make_chip(chip_f, "⚪ Ollama")
        self._chip_openai = self._make_chip(chip_f, "⚪ OpenAI")
        self._chip_claude = self._make_chip(chip_f, "⚪ Claude")
        self._chip_yconn  = self._make_chip(chip_f, "⚪ YCONN")

        # Modell-Umschalter
        self._llm_var = ctk.StringVar(value=_cfg.get("llm_mode", "🔄 Auto"))
        self._llm_seg = ctk.CTkSegmentedButton(
            hdr,
            values=["🔄 Auto", "🦙 Ollama", "✨ Claude", "🤖 OpenAI"],
            variable=self._llm_var,
            font=("Segoe UI", 11),
            width=230, height=34,
            fg_color=COLOR["bg3"],
            selected_color=COLOR["accent"],
            selected_hover_color="#388bfd",
            unselected_color=COLOR["bg3"],
            unselected_hover_color=COLOR["border"],
            text_color=COLOR["text"],
            text_color_disabled=COLOR["muted"],
            command=self._on_llm_mode_change,
        )
        self._llm_seg.grid(row=0, column=3, padx=6)

        # TTS Toggle
        self._tts_var = ctk.BooleanVar(value=TTS_ENABLED)
        ctk.CTkSwitch(
            hdr, text="🔊", variable=self._tts_var,
            font=("Segoe UI", 11), text_color=COLOR["muted"],
            width=52, command=self._toggle_tts
        ).grid(row=0, column=4, padx=6)

        # Einstellungen-Button
        ctk.CTkButton(
            hdr, text="⚙", width=38, height=38,
            font=("Segoe UI Emoji", 18),
            fg_color=COLOR["bg3"], hover_color=COLOR["border"],
            text_color=COLOR["muted"], corner_radius=8,
            command=self._open_settings
        ).grid(row=0, column=5, padx=(0, 12))

        # ── Chat-Bereich ─────────────────────────────────────
        chat_outer = ctk.CTkFrame(self, fg_color=COLOR["bg"], corner_radius=0)
        chat_outer.grid(row=1, column=0, sticky="nsew")
        chat_outer.grid_rowconfigure(0, weight=1)
        chat_outer.grid_columnconfigure(0, weight=1)

        self._chat = ctk.CTkTextbox(
            chat_outer,
            font=("Segoe UI", 13),
            fg_color=COLOR["bg"],
            text_color=COLOR["text"],
            wrap="word",
            state="disabled",
            corner_radius=0,
            border_width=0,
            scrollbar_button_color=COLOR["bg3"],
        )
        self._chat.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Text-Tags konfigurieren
        self._chat._textbox.tag_configure("esra_hdr",
            foreground=COLOR["blue"], font=("Segoe UI", 12, "bold"))
        self._chat._textbox.tag_configure("user_hdr",
            foreground=COLOR["green"], font=("Segoe UI", 12, "bold"))
        self._chat._textbox.tag_configure("time_tag",
            foreground=COLOR["muted"], font=("Segoe UI", 10))
        self._chat._textbox.tag_configure("system_tag",
            foreground=COLOR["amber"], font=("Segoe UI", 11, "italic"))
        self._chat._textbox.tag_configure("error_tag",
            foreground=COLOR["red"], font=("Segoe UI", 12))

        # Trennlinie
        ctk.CTkFrame(self, height=1, fg_color=COLOR["border"],
                     corner_radius=0).grid(row=2, column=0, sticky="ew")

        # ── Eingabe-Leiste ────────────────────────────────────
        bar = ctk.CTkFrame(self, fg_color=COLOR["bg2"],
                           corner_radius=0, height=74)
        bar.grid(row=3, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        self._mic_btn = ctk.CTkButton(
            bar, text="🎤", width=54, height=50,
            font=("Segoe UI Emoji", 22),
            fg_color=COLOR["accent"], hover_color="#388bfd",
            corner_radius=27,
            command=self._toggle_mic
        )
        self._mic_btn.grid(row=0, column=0, padx=12, pady=12)

        self._entry = ctk.CTkEntry(
            bar,
            placeholder_text="Nachricht tippen oder 🎤 drücken…",
            font=("Segoe UI", 13), height=50, corner_radius=12,
            fg_color=COLOR["bg3"], border_color=COLOR["border"],
            text_color=COLOR["text"],
            placeholder_text_color=COLOR["muted"],
        )
        self._entry.grid(row=0, column=1, padx=4, pady=12, sticky="ew")
        self._entry.bind("<Return>", lambda _: self._send())

        self._send_btn = ctk.CTkButton(
            bar, text="➤", width=54, height=50,
            font=("Segoe UI", 20),
            fg_color="#238636", hover_color="#2ea043",
            corner_radius=12,
            command=self._send
        )
        self._send_btn.grid(row=0, column=2, padx=12, pady=12)

    def _make_chip(self, parent, text: str) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", 11),
            width=108,
            fg_color=COLOR["bg3"],
            corner_radius=20,
            padx=8, pady=4,
            text_color=COLOR["muted"],
        )
        lbl.pack(side="left", padx=3)
        return lbl

    # ── Status ────────────────────────────────────────────────

    def _refresh_status(self):
        # Ollama
        self.router._check_ollama()
        if self.router.ollama_ok:
            self._chip_ollama.configure(text="🟢 Ollama", text_color=COLOR["green"])
        else:
            self._chip_ollama.configure(text="🔴 Ollama", text_color=COLOR["red"])
        # OpenAI
        if self.router.openai_ok:
            self._chip_openai.configure(text="🟢 OpenAI", text_color=COLOR["green"])
        else:
            self._chip_openai.configure(text="⚪ OpenAI", text_color=COLOR["muted"])
        # Claude
        if self.router.claude_ok:
            self._chip_claude.configure(text="🟢 Claude", text_color=COLOR["green"])
        else:
            self._chip_claude.configure(text="⚪ Claude", text_color=COLOR["muted"])
        # YCONN
        if self.yconn.ping():
            self._chip_yconn.configure(text="🟢 YCONN", text_color=COLOR["green"])
        else:
            self._chip_yconn.configure(text="🔴 YCONN", text_color=COLOR["red"])
        # alle 15 Sek. wiederholen
        self.after(15_000, self._refresh_status)

    def _toggle_tts(self):
        global TTS_ENABLED
        TTS_ENABLED = self._tts_var.get()

    def _on_llm_mode_change(self, mode: str):
        """Speichert den gewählten LLM-Modus dauerhaft."""
        cfg = _load_config()
        cfg["llm_mode"] = mode
        _save_config(cfg)

    def _open_settings(self):
        EsraSettings(self)

    # ── Chat-Ausgabe ──────────────────────────────────────────

    def _write(self, text: str, tag: str = ""):
        self._chat.configure(state="normal")
        if tag:
            self._chat._textbox.insert("end", text, tag)
        else:
            self._chat._textbox.insert("end", text)
        self._chat.configure(state="disabled")
        self._chat._textbox.see("end")

    def _add_message_header(self, role: str):
        ts  = datetime.now().strftime("%H:%M")
        self._write("\n")
        if role == "esra":
            self._write("🤖 Esra", "esra_hdr")
        else:
            self._write("👤 Du", "user_hdr")
        self._write(f"  {ts}\n", "time_tag")

    def _start_esra_stream(self):
        """Markiert Einfügeposition für Streaming."""
        self._add_message_header("esra")
        self._chat.configure(state="normal")
        self._stream_marker = self._chat._textbox.index("end")
        self._chat.configure(state="disabled")

    def _append_stream(self, chunk: str):
        """Hängt Streaming-Chunk am Marker an."""
        self._chat.configure(state="normal")
        self._chat._textbox.insert(self._stream_marker, chunk)
        self._stream_marker = self._chat._textbox.index(
            f"{self._stream_marker}+{len(chunk)}c"
        )
        self._chat.configure(state="disabled")
        self._chat._textbox.see("end")

    def _finalize_stream(self):
        self._write("\n")

    # ── Nachricht senden ──────────────────────────────────────

    def _send(self, text: str = ""):
        msg = text or self._entry.get().strip()
        if not msg or self._processing:
            return
        self._entry.delete(0, "end")
        self._add_message_header("user")
        self._write(msg + "\n")
        threading.Thread(target=self._process, args=(msg,), daemon=True).start()

    def _process(self, user_msg: str):
        self._processing = True
        self._set_ui_busy(True)

        # YCONN-Kontext anreichern
        context = self.yconn.build_context(user_msg)
        augmented = user_msg + context
        self.history.append({"role": "user", "content": augmented})

        # Streaming-Bubble vorbereiten
        self.after(0, self._start_esra_stream)
        time.sleep(0.05)

        streamed = ""

        def on_chunk(c):
            nonlocal streamed
            streamed += c
            self.after(0, lambda txt=c: self._append_stream(txt))

        try:
            mode = self._llm_var.get()
            if mode == "🦙 Ollama":
                if not self.router.ollama_ok:
                    raise RuntimeError(
                        "Ollama nicht erreichbar.\n"
                        "→ PowerShell: ollama serve\n"
                        "→ Dann: ollama pull llama3.2"
                    )
                full = self.router._ollama_chat(self.history, on_chunk=on_chunk)
            elif mode == "✨ Claude":
                if not self.router.claude_ok:
                    raise RuntimeError(
                        "Anthropic API Key fehlt.\n"
                        "→ ⚙ Einstellungen öffnen und Claude API Key eintragen."
                    )
                full = self.router._claude_chat(self.history, on_chunk=on_chunk)
            elif mode == "🤖 OpenAI":
                if not self.router.openai_ok:
                    raise RuntimeError(
                        "OpenAI API Key fehlt.\n"
                        "→ ⚙ Einstellungen öffnen und Key eintragen."
                    )
                full = self.router._openai_chat(self.history, on_chunk=on_chunk)
            else:  # 🔄 Auto
                full = self.router.query(self.history, on_chunk=on_chunk)
        except Exception as e:
            full = f"❌ Fehler: {e}"
            self.after(0, lambda t=full: self._append_stream(t))

        self.history.append({"role": "assistant", "content": full})
        self.after(0, self._finalize_stream)

        # TTS
        if TTS_ENABLED:
            self.tts.speak(full)

        self._processing = False
        self.after(0, lambda: self._set_ui_busy(False))

    def _set_ui_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self._send_btn.configure(state=state)
        self._entry.configure(state=state)

    # ── Mikrofon ──────────────────────────────────────────────

    def _toggle_mic(self):
        if self._listening or self._processing:
            return
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        self._listening = True
        self.after(0, lambda: (
            self._mic_btn.configure(text="🔴", fg_color="#da3633"),
            self._write("\n", ""),
            self._write("🎙 Höre zu…\n", "system_tag"),
        ))
        try:
            with sr.Microphone(device_index=self._mic_device_index) as src:
                self.recognizer.adjust_for_ambient_noise(src, duration=0.4)
                self.after(0, lambda: self._mic_btn.configure(text="👂"))
                audio = self.recognizer.listen(src, timeout=8, phrase_time_limit=20)

            # STT: Google (online) → Whisper (offline)
            text = ""
            try:
                text = self.recognizer.recognize_google(audio, language="de-DE")
            except (sr.UnknownValueError, sr.RequestError):
                try:
                    text = self.recognizer.recognize_whisper(
                        audio, language="german", model="base"
                    )
                except Exception:
                    pass

            if text:
                self.after(0, lambda t=text: self._send(t))
            else:
                self.after(0, lambda: self._write("(nichts erkannt)\n", "system_tag"))

        except sr.WaitTimeoutError:
            self.after(0, lambda: self._write("(Timeout – kein Sprechen erkannt)\n", "system_tag"))
        except Exception as e:
            self.after(0, lambda err=str(e): self._write(f"⚠ Mikrofon-Fehler: {err}\n", "error_tag"))
        finally:
            self._listening = False
            self.after(0, lambda: self._mic_btn.configure(
                text="🎤", fg_color=COLOR["accent"]
            ))

    # ── Begrüßung ─────────────────────────────────────────────

    def _greet(self):
        llm = "Ollama" if self.router.ollama_ok else ("OpenAI" if self.router.openai_ok else "–")
        yconn = "✓" if self.yconn.ping() else "✗"
        self._add_message_header("esra")
        self._write(
            f"Hallo! Ich bin Esra, deine intelligente SAP-Assistentin. 👋\n\n"
            f"Status: LLM = {llm}  |  YCONN = {yconn}\n\n"
            f"Stelle mir eine Frage oder drücke 🎤 zum Sprechen.\n"
            f"Beispiele:\n"
            f"  • \"Wie viele offene Rechnungen gibt es?\"\n"
            f"  • \"Was ist der Gesamtbetrag der offenen Rechnungen?\"\n"
            f"  • \"Erkläre mir den Unterschied zwischen SEP und SEQ.\"\n"
        )


# ══════════════════════════════════════════════════════════════
# Start
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = EsraApp()
    app.mainloop()
