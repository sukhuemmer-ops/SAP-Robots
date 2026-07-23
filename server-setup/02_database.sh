#!/bin/bash
# ============================================================
#  YCONN – Schritt 2: PostgreSQL Datenbank einrichten
#  Ausführen als root: bash 02_database.sh
# ============================================================
set -e

DB_NAME="yconn"
DB_USER="yconn_app"
DB_PASS="YconnDB#2026!"   # <-- hier dein Passwort setzen

echo "=== PostgreSQL: Datenbank '$DB_NAME' einrichten ==="

# PostgreSQL starten + Autostart
systemctl enable postgresql
systemctl start postgresql

# Datenbank + Benutzer anlegen
sudo -u postgres psql <<EOF
-- Benutzer anlegen (falls nicht vorhanden)
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASS';
  END IF;
END
\$\$;

-- Datenbank anlegen (falls nicht vorhanden)
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Rechte vergeben
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo ""
echo "=== Datenbank eingerichtet ==="
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Datenbank: $DB_NAME"
echo "  Benutzer:  $DB_USER"
echo "  Passwort:  $DB_PASS"
echo ""
echo "  Connection URL für .env:"
echo "  DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
