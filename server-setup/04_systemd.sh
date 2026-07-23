#!/bin/bash
# ============================================================
#  YCONN – Schritt 4: Systemd-Dienst einrichten
#  App startet automatisch beim Serverboot
#  Ausführen als root: bash 04_systemd.sh
# ============================================================
set -e

APP_DIR="/opt/yconn"

# Systemd Service-Datei schreiben
cat > /etc/systemd/system/yconn.service <<'EOF'
[Unit]
Description=YCONN Finance Orchestrator (FastAPI)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=yconn
WorkingDirectory=/opt/yconn/orchestrator
Environment="PATH=/opt/yconn/orchestrator/.venv/bin"
ExecStart=/opt/yconn/orchestrator/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Dienst aktivieren + starten
systemctl daemon-reload
systemctl enable yconn
systemctl start yconn

echo ""
echo "=== Dienst eingerichtet ==="
systemctl status yconn --no-pager
echo ""
echo "Logs anzeigen: journalctl -u yconn -f"
