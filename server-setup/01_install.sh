#!/bin/bash
# ============================================================
#  YCONN – Debian/TurnKey Core Setup
#  Schritt 1: System, Python, PostgreSQL, Apache installieren
#  Ausführen als root: bash 01_install.sh
# ============================================================
set -e
echo "=== YCONN Server Setup ==="

# System updaten
apt update && apt upgrade -y

# Python 3.12 + Tools
apt install -y python3 python3-pip python3-venv git curl

# PostgreSQL
apt install -y postgresql postgresql-contrib

# Apache + Module für Reverse Proxy
apt install -y apache2
a2enmod proxy proxy_http headers rewrite

echo ""
echo "=== Installation abgeschlossen ==="
python3 --version
psql --version
apache2 -v
