"""
Listet alle SAPLogon-Verbindungen aus SAPUILandscape.xml.
=========================================================
Hilft, wenn ``OpenConnection('XYZ')`` mit
``SAP Logon connection entry not found`` scheitert -- zeigt dir den exakten
Namen, den du als ``SAP_GUI_CONNECTION`` in .env eintragen musst.

Sucht in den ueblichen Pfaden:
  %APPDATA%\\SAP\\Common\\SAPUILandscape.xml     (modernes SAPLogon, per-User)
  %APPDATA%\\SAP\\Common\\SAPUILandscapeGlobal.xml (zentral)
  %PROGRAMDATA%\\SAP\\Common\\*.xml                (alte Variante)
  Pfad aus Umgebungsvariable SAPLOGON_INI_FILE
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def find_xml_files() -> list:
    candidates = []
    appdata = os.environ.get("APPDATA")
    progdata = os.environ.get("PROGRAMDATA")
    if appdata:
        candidates += [
            Path(appdata) / "SAP" / "Common" / "SAPUILandscape.xml",
            Path(appdata) / "SAP" / "Common" / "SAPUILandscapeGlobal.xml",
        ]
    if progdata:
        candidates += [
            Path(progdata) / "SAP" / "Common" / "SAPUILandscape.xml",
            Path(progdata) / "SAP" / "Common" / "SAPUILandscapeGlobal.xml",
        ]
    if os.environ.get("SAPLOGON_INI_FILE"):
        candidates.append(Path(os.environ["SAPLOGON_INI_FILE"]))
    return [p for p in candidates if p.exists()]


def parse_xml(path: Path):
    print(f"\n=== Datei: {path} ===")
    try:
        tree = ET.parse(path)
    except Exception as exc:  # noqa: BLE001
        print(f"  [FEHLER] {exc}")
        return
    root = tree.getroot()
    services = root.findall(".//Service")
    if not services:
        print("  (keine Service-Eintraege gefunden)")
        return
    print(f"  Gefundene Verbindungen: {len(services)}\n")
    print(f"  {'NAME (genau so in .env eintragen)':<45} {'SYSID':<6} {'SERVER:PORT/MSHOST':<35} {'CLIENT'}")
    print(f"  {'-'*44:<45} {'-'*5:<6} {'-'*34:<35} {'-'*6}")
    for s in services:
        name   = s.get("name", "")
        sysid  = s.get("systemid", "")
        client = ""
        # Client steckt entweder im SID-Attribut oder in einem Unter-Element
        client = s.get("client", "")
        # Server-Info
        srv = ""
        if s.get("server"):
            srv = s.get("server")
        elif s.find("Router") is not None and s.find("Router").get("name"):
            srv = s.find("Router").get("name")
        elif s.get("msid"):
            srv = f"MS={s.get('msid')}"
        print(f"  {name:<45} {sysid:<6} {srv:<35} {client}")


def main() -> int:
    files = find_xml_files()
    if not files:
        print("Keine SAPUILandscape.xml gefunden.")
        print("Pruefe in deinem Browser: %APPDATA%\\SAP\\Common\\")
        return 1
    for f in files:
        parse_xml(f)
    print("\nTrage den gewuenschten NAME (linke Spalte) exakt in .env unter")
    print("SAP_GUI_CONNECTION=<name> ein - inkl. Leerzeichen und Schreibweise.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
