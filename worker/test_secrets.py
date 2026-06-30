"""
Schneller Test fuer den Secret-Resolver.
========================================
Laeuft offline, braucht weder SAP noch pyrfc.

Beispiele:
    python test_secrets.py env://SAP_PASSWORD
    python test_secrets.py file:///C:/secrets/sap.txt
    python test_secrets.py azure-kv://my-vault/RPA_PRD_SERVICE
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    here = Path(__file__).resolve().parent
    for candidate in (here / ".env", here / ".env.example"):
        if candidate.exists():
            load_dotenv(candidate)
            print(f"[ok] .env geladen aus {candidate}")
            break
except ImportError:
    print("[warn] python-dotenv nicht installiert (pip install python-dotenv)")

from sap_secrets import resolve_secret, build_sap_rfc_params


def mask(s: str) -> str:
    """Maskiert das Geheimnis fuer die Konsolen-Ausgabe."""
    if not s:
        return "(leer)"
    if len(s) <= 4:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 4) + s[-2:]


def main() -> int:
    if len(sys.argv) < 2:
        # Default-Demo: zeige die SAP-Verbindungsparameter
        print("Verwendung: python test_secrets.py <vault-uri>")
        print()
        print("=== Demo: build_sap_rfc_params('SAP') ===")
        try:
            params = build_sap_rfc_params("SAP")
            for k, v in params.items():
                print(f"  {k:>10} = {mask(str(v)) if 'pass' in k.lower() else v}")
            print()
            print("Wenn alle Felder gefuellt sind, kann der Worker eine RFC-Verbindung oeffnen.")
        except Exception as exc:  # noqa: BLE001
            print(f"  FEHLER: {exc}")
        return 0

    uri = sys.argv[1]
    print(f"Loese auf: {uri}")
    try:
        secret = resolve_secret(uri)
        print(f"  OK -> {mask(secret)} (Laenge: {len(secret)})")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"  FEHLER: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
