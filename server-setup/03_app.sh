#!/bin/bash
# ============================================================
#  YCONN – Schritt 3: App deployen + venv einrichten
#  Ausführen als root: bash 03_app.sh
# ============================================================
set -e

APP_DIR="/opt/yconn"
APP_USER="yconn"

echo "=== YCONN App einrichten ==="

# System-Benutzer für den Dienst anlegen (kein Login-Shell)
id -u $APP_USER &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin $APP_USER

# App-Verzeichnis anlegen
mkdir -p $APP_DIR
# Dateien aus dem Repo hierhin kopieren (oder git clone):
# git clone https://github.com/dein-repo/sap-robots.git $APP_DIR
# ODER: Dateien manuell nach $APP_DIR/orchestrator kopieren

# Python venv anlegen
python3 -m venv $APP_DIR/orchestrator/.venv
$APP_DIR/orchestrator/.venv/bin/pip install --upgrade pip
$APP_DIR/orchestrator/.venv/bin/pip install -r $APP_DIR/orchestrator/requirements.txt

# psycopg2 für PostgreSQL (zusätzlich zu requirements.txt)
$APP_DIR/orchestrator/.venv/bin/pip install psycopg2-binary

# Berechtigungen setzen
chown -R $APP_USER:$APP_USER $APP_DIR

echo ""
echo "=== App-Verzeichnis: $APP_DIR ==="
echo "Nächster Schritt: .env anpassen (DATABASE_URL setzen)"
