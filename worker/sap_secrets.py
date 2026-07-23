"""
Secret-Resolver
===============
Loest URI-Referenzen aus dem Cockpit (z. B. ``azure-kv://sap-prd/RPA_AP_SERVICE``)
zur Laufzeit in echte Geheimnisse auf.

Unterstuetzte Schemata
----------------------
* ``env://VAR_NAME``                           - Umgebungsvariable (einfachster Fall, .env-Datei)
* ``file:///absoluter/pfad.txt``               - Klartext aus Datei (erste Zeile)
* ``windows-dpapi://C:/secrets/datei.dat``     - DPAPI-verschluesselte Datei (Windows)
* ``azure-kv://<vault-name>/<secret-name>``    - Azure Key Vault
* ``hashicorp-vault://<engine>/<pfad>#<key>``  - HashiCorp Vault (KV v2)
* ``aws-sm://<region>/<secret-name>``          - AWS Secrets Manager
* ``gcp-sm://<projekt>/<secret-name>``         - Google Secret Manager

Die optionalen Abhaengigkeiten werden lazy importiert, damit der Worker auch
ohne installierte Cloud-SDKs startet, solange du nur ``env://`` oder ``file://``
nutzt.

Schnellstart fuer lokale Tests
------------------------------
* In ``.env`` setzt du ``SAP_PASSWORD=...`` und im Cockpit traegst du als
  Passwort-Vault-Ref ``env://SAP_PASSWORD`` ein.
* Der Worker laedt ``.env`` automatisch, ``resolve_secret("env://SAP_PASSWORD")``
  gibt dann dein Passwort zurueck.

Beispiel
--------
>>> from secrets_resolver import resolve_secret
>>> pw = resolve_secret("azure-kv://sap-prd/RPA_AP_SERVICE")
>>> conn = Connection(passwd=pw, ...)
"""
from __future__ import annotations

import logging
import os
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

log = logging.getLogger("secrets")

# ── Fernet-Modul aus dem Projektstamm laden ──────────────────────────────────
_PROJ_ROOT = Path(__file__).parent.parent  # worker/../  → Projektstamm
if str(_PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def resolve_secret(uri: str) -> str:
    """
    Loest eine Vault-URI in das echte Geheimnis auf.

    Wirft ``ValueError`` bei unbekanntem Schema oder fehlender URI,
    ``RuntimeError`` wenn der Lookup beim Backend scheitert.
    """
    if not uri:
        raise ValueError("Secret-URI ist leer.")

    if "://" not in uri:
        raise ValueError(
            f"URI '{uri}' enthaelt kein Schema. "
            f"Erwartet etwa 'env://VAR' oder 'azure-kv://vault/secret'."
        )

    scheme = uri.split("://", 1)[0].lower()
    handler = _HANDLERS.get(scheme)
    if not handler:
        raise ValueError(
            f"Unbekanntes Vault-Schema '{scheme}'. Bekannt: {sorted(_HANDLERS)}"
        )

    try:
        secret = handler(uri)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Konnte Secret '{uri}' nicht aufloesen: {exc}") from exc

    if not secret:
        raise RuntimeError(f"Secret '{uri}' aufgeloest, aber leer.")
    return secret


@lru_cache(maxsize=64)
def resolve_secret_cached(uri: str) -> str:
    """Wie ``resolve_secret``, aber merkt sich Ergebnisse pro URI."""
    return resolve_secret(uri)


def clear_cache() -> None:
    """Leert den Cache, z. B. nach Secret-Rotation."""
    resolve_secret_cached.cache_clear()


# ---------------------------------------------------------------------------
# Handler je Schema
# ---------------------------------------------------------------------------
def _h_enc(uri: str) -> str:
    """Entschlüsselt einen Fernet-verschlüsselten Wert (ENC:-Präfix).
    URI-Form: enc://ENC:gAAAAA...   oder   enc://ENC:...
    Wird verwendet wenn .env-Datei Werte mit ENC:-Präfix enthält."""
    try:
        from crypto import decrypt  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "crypto.py nicht gefunden. Liegt secret.key im Projektstamm? "
            f"({exc})"
        ) from exc
    # enc://ENC:xxx  →  ENC:xxx
    raw = uri[len("enc://"):]
    return decrypt(raw)


def _h_env(uri: str) -> str:
    var = uri[len("env://"):]
    val = os.getenv(var)
    if val is None:
        raise RuntimeError(f"Umgebungsvariable '{var}' nicht gesetzt.")
    # Automatisch entschlüsseln wenn der .env-Wert mit ENC: anfängt
    if val.startswith("ENC:"):
        try:
            from crypto import decrypt  # type: ignore
            return decrypt(val)
        except Exception as exc:
            raise RuntimeError(
                f"Entschlüsselung von '{var}' fehlgeschlagen: {exc}"
            ) from exc
    return val


def _h_file(uri: str) -> str:
    # file:///abs/path
    parts = urlsplit(uri)
    path = parts.path
    # Windows: file:///C:/secrets/foo.txt -> path = "/C:/secrets/foo.txt"
    if os.name == "nt" and path.startswith("/") and len(path) > 2 and path[2] == ":":
        path = path[1:]
    with open(path, "r", encoding="utf-8") as f:
        return f.readline().rstrip("\r\n")


def _h_windows_dpapi(uri: str) -> str:
    path = uri[len("windows-dpapi://"):]
    if os.name == "nt" and path.startswith("/"):
        path = path.lstrip("/")
    try:
        import win32crypt  # type: ignore  # pip install pywin32
    except ImportError as exc:
        raise RuntimeError(
            "Modul 'win32crypt' fehlt. Installiere pywin32: pip install pywin32"
        ) from exc
    with open(path, "rb") as f:
        blob = f.read()
    description, plaintext = win32crypt.CryptUnprotectData(blob, None, None, None, 0)
    log.debug("DPAPI entschluesselt: %s", description)
    return plaintext.decode("utf-8")


def _h_azure_kv(uri: str) -> str:
    # azure-kv://<vault-name>/<secret-name>[/<version>]
    rest = uri[len("azure-kv://"):]
    parts = rest.split("/")
    if len(parts) < 2:
        raise ValueError("Azure-KV-URI: erwarte vault-name/secret-name")
    vault_name, secret_name = parts[0], parts[1]
    version = parts[2] if len(parts) > 2 else None
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
    except ImportError as exc:
        raise RuntimeError(
            "Module fehlen. Installiere: "
            "pip install azure-identity azure-keyvault-secrets"
        ) from exc
    vault_url = f"https://{vault_name}.vault.azure.net"
    client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
    return client.get_secret(secret_name, version=version).value


def _h_hashicorp_vault(uri: str) -> str:
    # hashicorp-vault://<mount>/<path>#<key>
    rest = uri[len("hashicorp-vault://"):]
    if "#" not in rest:
        raise ValueError(
            "HashiCorp-Vault-URI braucht '#<key>' am Ende, "
            "z. B. hashicorp-vault://secret/sap/prd#password"
        )
    path_part, key = rest.rsplit("#", 1)
    mount, _, secret_path = path_part.partition("/")
    try:
        import hvac  # type: ignore  # pip install hvac
    except ImportError as exc:
        raise RuntimeError("Modul fehlt: pip install hvac") from exc
    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")
    if not (vault_addr and vault_token):
        raise RuntimeError("VAULT_ADDR und VAULT_TOKEN muessen gesetzt sein.")
    client = hvac.Client(url=vault_addr, token=vault_token)
    resp = client.secrets.kv.v2.read_secret_version(path=secret_path, mount_point=mount)
    data = resp["data"]["data"]
    if key not in data:
        raise RuntimeError(f"Key '{key}' nicht im Vault-Secret gefunden.")
    return data[key]


def _h_aws_sm(uri: str) -> str:
    # aws-sm://<region>/<secret-name>
    rest = uri[len("aws-sm://"):]
    region, _, name = rest.partition("/")
    if not (region and name):
        raise ValueError("AWS-SM-URI: erwarte region/secret-name")
    try:
        import boto3  # type: ignore  # pip install boto3
    except ImportError as exc:
        raise RuntimeError("Modul fehlt: pip install boto3") from exc
    client = boto3.client("secretsmanager", region_name=region)
    resp = client.get_secret_value(SecretId=name)
    return resp.get("SecretString") or resp["SecretBinary"].decode("utf-8")


def _h_gcp_sm(uri: str) -> str:
    # gcp-sm://<project>/<secret-name>[/versions/<v>]
    rest = uri[len("gcp-sm://"):]
    parts = rest.split("/")
    if len(parts) < 2:
        raise ValueError("GCP-SM-URI: erwarte project/secret-name")
    project, name = parts[0], parts[1]
    version = parts[3] if len(parts) >= 4 and parts[2] == "versions" else "latest"
    try:
        from google.cloud import secretmanager  # type: ignore  # pip install google-cloud-secret-manager
    except ImportError as exc:
        raise RuntimeError(
            "Modul fehlt: pip install google-cloud-secret-manager"
        ) from exc
    client = secretmanager.SecretManagerServiceClient()
    full = f"projects/{project}/secrets/{name}/versions/{version}"
    return client.access_secret_version(request={"name": full}).payload.data.decode("utf-8")


_HANDLERS = {
    "enc":               _h_enc,           # Fernet – lokale Verschlüsselung
    "env":               _h_env,
    "file":              _h_file,
    "windows-dpapi":     _h_windows_dpapi,
    "azure-kv":          _h_azure_kv,
    "hashicorp-vault":   _h_hashicorp_vault,
    "aws-sm":            _h_aws_sm,
    "gcp-sm":            _h_gcp_sm,
}


# ---------------------------------------------------------------------------
# Convenience: SAP-Verbindungsparameter bauen
# ---------------------------------------------------------------------------
def build_sap_rfc_params(prefix: str = "SAP") -> dict:
    """
    Baut den Parameter-Dict fuer ``pyrfc.Connection``. Liest die Konfiguration
    aus Umgebungsvariablen <PREFIX>_ASHOST, <PREFIX>_SYSNR, ...

    Das Passwort kommt aus <PREFIX>_PASSWORD_REF (Vault-URI). Falls die nicht
    gesetzt ist, faellt der Code auf ``env://<PREFIX>_PASSWORD`` zurueck,
    sodass eine einfache .env-Datei mit ``SAP_PASSWORD=...`` direkt funktioniert.
    """
    def must(name: str) -> str:
        val = os.getenv(name)
        if not val:
            raise RuntimeError(f"Umgebungsvariable {name} fehlt.")
        return val

    password_ref = os.getenv(f"{prefix}_PASSWORD_REF") or f"env://{prefix}_PASSWORD"
    params = {
        "ashost": must(f"{prefix}_ASHOST"),
        "sysnr":  os.getenv(f"{prefix}_SYSNR", "00"),
        "client": must(f"{prefix}_CLIENT"),
        "user":   must(f"{prefix}_USER"),
        "passwd": resolve_secret_cached(password_ref),
        "lang":   os.getenv(f"{prefix}_LANG", "DE"),
    }
    # Optionale Felder
    if os.getenv(f"{prefix}_SAPROUTER"):
        params["saprouter"] = os.getenv(f"{prefix}_SAPROUTER")
    if os.getenv(f"{prefix}_MSHOST"):
        params["mshost"] = os.getenv(f"{prefix}_MSHOST")
        params["group"]  = os.getenv(f"{prefix}_GROUP", "PUBLIC")
        params["sysid"]  = os.getenv(f"{prefix}_SYSID", "")
        params.pop("ashost", None)
    if os.getenv(f"{prefix}_SNC_PARTNERNAME"):
        params.update({
            "snc_qop":         os.getenv(f"{prefix}_SNC_QOP", "9"),
            "snc_myname":      os.getenv(f"{prefix}_SNC_MYNAME", ""),
            "snc_partnername": os.getenv(f"{prefix}_SNC_PARTNERNAME"),
            "snc_lib":         os.getenv(f"{prefix}_SNC_LIB", ""),
        })
    return params


def build_sap_gui_params(prefix: str = "SAP_GUI") -> dict:
    """Analog zu ``build_sap_rfc_params`` fuer SAP GUI Scripting."""
    password_ref = (
        os.getenv(f"{prefix}_PASSWORD_REF")
        or f"env://{prefix.replace('_GUI', '')}_PASSWORD"
    )
    return {
        "connection": os.getenv(f"{prefix}_CONNECTION") or os.getenv("SAP_GUI_CONNECTION"),
        "user":       os.getenv(f"{prefix}_USER") or os.getenv("SAP_USER"),
        "password":   resolve_secret_cached(password_ref),
        "client":     os.getenv("SAP_CLIENT"),
        "lang":       os.getenv("SAP_LANG", "DE"),
    }
