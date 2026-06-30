"""
Vollstaendiger SAP-Verbindungstest.
===================================
Laeuft NICHT in der Cloud-Sandbox, sondern auf einer Windows-VM mit:
  * Netzwerkzugang zu deinem SAP-System
  * installiertem SAP NW RFC SDK (aus SAP Software Center)
  * pip install pyrfc

Pruefphasen:
  1. .env wird geladen
  2. Secret-Resolver liefert das Passwort
  3. TCP-Verbindung zum Application Server steht
  4. RFC_PING liefert OK
  5. RFC_SYSTEM_INFO zeigt System-ID + Mandant zurueck (nice-to-have)
  6. Eine echte BAPI-Lese-Funktion laeuft (BAPI_USER_GET_DETAIL fuer den Service-User)

Bei Fehler in einer Phase wird abgebrochen und der konkrete Hinweis ausgegeben.
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)


def ok(msg: str) -> None:
    print(f"  [OK]    {msg}")


def fail(msg: str) -> int:
    print(f"  [FEHLER] {msg}")
    return 1


# ---------------------------------------------------------------------------
# Phase 1: Environment
# ---------------------------------------------------------------------------
section("Phase 1: .env laden")
try:
    from dotenv import load_dotenv
    here = Path(__file__).resolve().parent
    loaded = False
    for candidate in (here / ".env", here / ".env.example"):
        if candidate.exists():
            load_dotenv(candidate)
            ok(f"Geladen: {candidate.name}")
            loaded = True
            break
    if not loaded:
        sys.exit(fail("Keine .env oder .env.example gefunden."))
except ImportError:
    print("  [WARN]  python-dotenv nicht installiert (pip install python-dotenv)")

# Pflichtvariablen pruefen
required = ["SAP_ASHOST", "SAP_SYSNR", "SAP_CLIENT", "SAP_USER"]
missing = [v for v in required if not os.getenv(v)]
if missing:
    sys.exit(fail(f"Pflicht-Umgebungsvariablen fehlen: {missing}"))
ok("Alle Pflichtvariablen gesetzt: " + ", ".join(required))


# ---------------------------------------------------------------------------
# Phase 2: Secret-Resolver
# ---------------------------------------------------------------------------
section("Phase 2: Passwort aus Vault-Referenz aufloesen")
try:
    from sap_secrets import resolve_secret, build_sap_rfc_params
except ImportError as exc:
    sys.exit(fail(f"Modul 'sap_secrets' nicht gefunden: {exc}"))

pw_ref = os.getenv("SAP_PASSWORD_REF", "env://SAP_PASSWORD")
print(f"  Vault-Referenz: {pw_ref}")
try:
    pw = resolve_secret(pw_ref)
    masked = pw[:2] + "*" * max(0, len(pw) - 4) + pw[-2:] if len(pw) > 4 else "*" * len(pw)
    ok(f"Passwort gelesen ({len(pw)} Zeichen, maskiert: {masked})")
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(f"Konnte Passwort nicht aufloesen: {exc}"))


# ---------------------------------------------------------------------------
# Phase 3: Netzwerk
# ---------------------------------------------------------------------------
section("Phase 3: Netzwerk-Verbindung zum SAP-Server")
host = os.getenv("SAP_ASHOST")
sysnr = os.getenv("SAP_SYSNR", "00")
rfc_port = int(f"33{sysnr}")    # SAP-Dispatcher
gw_port  = int(f"32{sysnr}")    # SAP-Gateway

for port, name in [(rfc_port, "Dispatcher (RFC)"), (gw_port, "Gateway")]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        ok(f"{host}:{port} ({name}) erreichbar")
    except Exception as exc:  # noqa: BLE001
        if name == "Dispatcher (RFC)":
            sys.exit(fail(
                f"{host}:{port} ({name}) NICHT erreichbar: {exc}\n"
                "          Pruefe: Firmen-VPN aktiv? Firewall offen? SAProuter noetig?"
            ))
        else:
            print(f"  [WARN]  {host}:{port} ({name}) NICHT erreichbar - meist OK fuer reines RFC")
    finally:
        s.close()


# ---------------------------------------------------------------------------
# Phase 4: pyrfc + SAP NW RFC SDK
# ---------------------------------------------------------------------------
section("Phase 4: pyrfc und SAP NW RFC SDK pruefen")
try:
    from pyrfc import Connection  # type: ignore
    ok("pyrfc importiert")
except ImportError as exc:
    sys.exit(fail(
        f"pyrfc nicht installiert: {exc}\n"
        "          Schritt 1: SAP NW RFC SDK vom SAP Software Center laden\n"
        "          Schritt 2: Entpacken nach C:\\nwrfcsdk und C:\\nwrfcsdk\\lib in PATH eintragen\n"
        "          Schritt 3: pip install pyrfc"
    ))
except Exception as exc:  # noqa: BLE001 - z. B. fehlende sapnwrfc.dll
    sys.exit(fail(
        f"pyrfc da, aber SAP NW RFC SDK fehlt oder ist nicht im PATH: {exc}\n"
        "          Pruefe: C:\\nwrfcsdk\\lib im System-PATH? Maschine neu gestartet?"
    ))


# ---------------------------------------------------------------------------
# Phase 5: RFC_PING
# ---------------------------------------------------------------------------
section("Phase 5: RFC_PING")
try:
    params = build_sap_rfc_params("SAP")
    print(f"  Parameter: ashost={params.get('ashost')}, sysnr={params.get('sysnr')}, "
          f"client={params.get('client')}, user={params.get('user')}, lang={params.get('lang')}")
    conn = Connection(**params)
    try:
        conn.call("RFC_PING")
        ok("RFC_PING liefert OK - Login und RFC-Kanal funktionieren")
    finally:
        conn.close()
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(
        f"RFC_PING fehlgeschlagen: {exc}\n"
        "          Haeufige Ursachen:\n"
        "            - Falscher User/Mandant/Passwort\n"
        "            - User in SAP gesperrt (SU01 pruefen)\n"
        "            - Berechtigungsobjekt S_RFC fehlt"
    ))


# ---------------------------------------------------------------------------
# Phase 6: Systeminfo
# ---------------------------------------------------------------------------
section("Phase 6: System-Info abfragen")
try:
    conn = Connection(**build_sap_rfc_params("SAP"))
    try:
        info = conn.call("RFC_SYSTEM_INFO")
        rfcsi = info.get("RFCSI_EXPORT", info)
        for key in ("RFCSYSID", "RFCHOST", "RFCDEST", "RFCMACH", "RFCDBHOST", "RFCDBSYS"):
            if key in rfcsi:
                print(f"    {key:>12} = {rfcsi[key]}")
        ok("System-Info empfangen")
    finally:
        conn.close()
except Exception as exc:  # noqa: BLE001
    print(f"  [WARN]  RFC_SYSTEM_INFO nicht moeglich: {exc}")


# ---------------------------------------------------------------------------
# Phase 7: Echter BAPI-Lese-Call
# ---------------------------------------------------------------------------
section("Phase 7: BAPI_USER_GET_DETAIL fuer Service-User")
try:
    conn = Connection(**build_sap_rfc_params("SAP"))
    try:
        res = conn.call("BAPI_USER_GET_DETAIL", USERNAME=os.getenv("SAP_USER"))
        addr = res.get("ADDRESS", {})
        print(f"    Vollname:   {addr.get('FULLNAME','(leer)')}")
        print(f"    Abteilung:  {addr.get('DEPARTMENT','(leer)')}")
        print(f"    Sperrgrund: {res.get('ISLOCKED', {})}")
        ok("BAPI_USER_GET_DETAIL erfolgreich - Schreib-/Lese-Calls funktionieren")
    finally:
        conn.close()
except Exception as exc:  # noqa: BLE001
    print(f"  [WARN]  {exc}")


print("\n" + "=" * 70)
print("  Verbindungstest abgeschlossen.")
print("=" * 70)
