"""
check_voice.py  –  Diagnose für Voice/Mikrofon-Probleme mit Esra
Aufruf: python check_voice.py
"""
import os, json, sys

print("=" * 60)
print("  Esra Voice-Bot – Diagnose")
print("=" * 60)

# 1. anthropic-Paket
print("\n[1] Python-Pakete")
try:
    import anthropic
    print(f"  ✅ anthropic {anthropic.__version__}")
except ImportError:
    print("  ❌ anthropic FEHLT  →  pip install anthropic")

try:
    import openai
    print(f"  ✅ openai {openai.__version__}")
except ImportError:
    print("  ⚠  openai nicht installiert (optional)")

# 2. API Keys
print("\n[2] API Keys")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

claude_env = os.getenv("ANTHROPIC_API_KEY", "").strip()
openai_env = os.getenv("OPENAI_API_KEY", "").strip()
print(f"  ANTHROPIC_API_KEY (.env): {'✅ gesetzt' if claude_env else '❌ leer'}")
print(f"  OPENAI_API_KEY    (.env): {'✅ gesetzt' if openai_env else '⚪ leer (optional)'}")

# esra_config.json
esra_cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "esra", "esra_config.json")
if os.path.isfile(esra_cfg_path):
    with open(esra_cfg_path, "r") as f:
        esra_cfg = json.load(f)
    ck = esra_cfg.get("claude_key", "").strip()
    ok = esra_cfg.get("openai_key", "").strip()
    print(f"  esra_config.json Claude Key: {'✅ gesetzt' if ck else '❌ leer'}")
    print(f"  esra_config.json OpenAI Key: {'✅ gesetzt' if ok else '⚪ leer'}")
else:
    print(f"  ⚠  esra_config.json nicht gefunden: {esra_cfg_path}")

# 3. Bridge erreichbar?
print("\n[3] Bridge (Port 8765)")
try:
    import urllib.request
    r = urllib.request.urlopen("http://localhost:8765/voice/status", timeout=3)
    d = json.loads(r.read())
    prov = d.get("provider", "?")
    key_ok = d.get("api_key_set", False)
    print(f"  ✅ Bridge läuft  |  Provider: {prov}  |  API-Key: {'✅' if key_ok else '❌ fehlt'}")
except Exception as e:
    print(f"  ❌ Bridge nicht erreichbar: {e}")
    print("     → 'Bridge starten.bat' ausführen")

# 4. Orchestrator erreichbar?
print("\n[4] Orchestrator (Port 8000)")
try:
    r2 = urllib.request.urlopen("http://localhost:8000/ai_config/full", timeout=3)
    d2 = json.loads(r2.read())
    print(f"  ✅ Orchestrator läuft  |  Provider: {d2.get('provider','?')}  |  Key: {'✅' if d2.get('api_key') else '⚪ nicht gesetzt'}")
except Exception as e:
    print(f"  ❌ Orchestrator nicht erreichbar: {e}")

# 5. Kurztest Claude API
print("\n[5] Claude API Test")
key_to_test = claude_env
if not key_to_test and os.path.isfile(esra_cfg_path):
    key_to_test = esra_cfg.get("claude_key", "").strip()

if key_to_test:
    try:
        import anthropic as _a
        c = _a.Anthropic(api_key=key_to_test)
        r = c.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=30,
            messages=[{"role":"user","content":"Sag nur: OK"}]
        )
        print(f"  ✅ Claude API antwortet: {r.content[0].text.strip()}")
    except Exception as e:
        print(f"  ❌ Claude API Fehler: {e}")
else:
    print("  ⚠  Kein Claude-Key – Test übersprungen")
    print("     → In Esra Desktop App: ⚙ Einstellungen → Claude API Key eintragen")
    print("     → ODER in worker/.env:  ANTHROPIC_API_KEY=sk-ant-...")

print("\n" + "=" * 60)
print("  Lösung bei ❌ KI-Key fehlt:")
print("  1. Esra Desktop App öffnen")
print("  2. ⚙ Einstellungen klicken")
print("  3. Claude (Anthropic) API Key eintragen")
print("  4. 💾 Speichern")
print("  5. Bridge neu starten ('Bridge starten.bat')")
print("=" * 60)
input("\nDrücke Enter zum Beenden...")
