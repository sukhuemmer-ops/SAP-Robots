"""
check_saplogon.py  –  Findet alle SAP Logon Verbindungseinträge auf diesem PC.
Aufruf: python check_saplogon.py
"""
import os
import xml.etree.ElementTree as ET

SEQ_HOST = "172.28.189.11"
SEP_HOST = "172.28.189.8"

def collect_landscape_files():
    """Sammelt alle relevanten SAP Landscape XML-Dateien inkl. Includes."""
    seen = set()
    result = []

    def _add(path):
        path = os.path.normpath(path)
        if not os.path.isfile(path) or path in seen:
            return
        seen.add(path)
        result.append(path)
        # <Include url="file:///..."> folgen
        try:
            root = ET.parse(path).getroot()
            for inc in root.iter("Include"):
                url = inc.get("url", "")
                if url.startswith("file:///"):
                    inc_path = url[8:].replace("/", os.sep)
                    _add(inc_path)
        except Exception:
            pass

    candidates = [
        os.path.expandvars(r"%APPDATA%\SAP\Common\SAPUILandscape.xml"),
        os.path.expandvars(r"%APPDATA%\SAP\Common\SAPUILandscapeGlobal.xml"),
    ]
    try:
        sysdrive = os.environ.get("SYSTEMDRIVE", "C:")
        for uname in os.listdir(sysdrive + r"\Users"):
            base = os.path.join(sysdrive, "Users", uname, r"AppData\Roaming\SAP\Common")
            candidates += [os.path.join(base, "SAPUILandscape.xml"),
                           os.path.join(base, "SAPUILandscapeGlobal.xml")]
    except Exception:
        pass

    for c in candidates:
        _add(c)
    return result

def parse_entries(path):
    entries = []
    try:
        root = ET.parse(path).getroot()
        for svc in root.iter():
            name = svc.get("name", "")
            if not name:
                continue
            server = (svc.get("server", "") or svc.get("applicationserver", "")
                      or svc.get("host", ""))
            host = server.split(":")[0].strip()
            sysid = svc.get("systemid", "") or svc.get("sid", "")
            entries.append({"tag": svc.tag, "name": name, "host": host, "sysid": sysid})
    except Exception as e:
        print(f"  [Parse-Fehler]: {e}")
    return entries

print("=" * 65)
print("  SAP Logon Einträge – Diagnose")
print("=" * 65)

files = collect_landscape_files()
all_entries = []

for path in files:
    print(f"\n[Datei] {path}")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        for i, line in enumerate(content.splitlines()[:60], 1):
            print(f"    {i:3d}: {line}")
    except Exception as e:
        print(f"  Lesefehler: {e}")
    entries = parse_entries(path)
    all_entries += entries
    if entries:
        print(f"\n  Gefundene Einträge ({len(entries)}):")
        for e in entries:
            marker = ""
            if e["host"] and (SEQ_HOST in e["host"] or e["host"] in SEQ_HOST):
                marker = "  ←── SEQ"
            elif e["host"] and (SEP_HOST in e["host"] or e["host"] in SEP_HOST):
                marker = "  ←── SEP"
            print(f"    name='{e['name']}'  host='{e['host']}'  sid='{e['sysid']}'{marker}")

# ── SAP GUI COM ────────────────────────────────────────────────
print("\n[SAP GUI COM – laufende Sessions]")
try:
    import win32com.client as wc
    app = wc.GetActiveObject("SAPGUI").GetScriptingEngine
    for ci in range(app.Children.Count):
        conn = app.Children(ci)
        for si in range(conn.Children.Count):
            sess = conn.Children(si)
            try:
                print(f"  conn[{ci}]/sess[{si}]  server={sess.info.applicationServer}  sys={sess.info.system}")
            except Exception:
                print(f"  conn[{ci}]/sess[{si}]  (info nicht lesbar)")
except Exception as e:
    print(f"  Nicht verfügbar: {e}")

# ── Empfehlung ────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  Empfehlung für worker/.env:")
if all_entries:
    for e in all_entries:
        if SEQ_HOST in e["host"] or e["host"] in SEQ_HOST:
            print(f"  SAP_GUI_CONNECTION_SEQ={e['name']}")
        elif SEP_HOST in e["host"] or e["host"] in SEP_HOST:
            print(f"  SAP_GUI_CONNECTION_SEP={e['name']}")
else:
    print("  Keine Einträge gefunden.")

print()
input("Drücke Enter zum Beenden...")
