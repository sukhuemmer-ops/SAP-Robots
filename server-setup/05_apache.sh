#!/bin/bash
# ============================================================
#  YCONN – Schritt 5: Apache als Reverse Proxy konfigurieren
#  Browser → Apache :80 → uvicorn :8000
#  Ausführen als root: bash 05_apache.sh
# ============================================================
set -e

SERVER_NAME="yconn.firma.local"   # <-- Hostname oder IP anpassen

# Apache VirtualHost schreiben
cat > /etc/apache2/sites-available/yconn.conf <<EOF
<VirtualHost *:80>
    ServerName $SERVER_NAME

    # Alle Anfragen an uvicorn weiterleiten
    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # WebSocket-Support (für spätere Nutzung)
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://127.0.0.1:8000/\$1" [P,L]

    # Echte Client-IP an uvicorn durchreichen
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Real-IP "%{REMOTE_ADDR}s"

    ErrorLog  \${APACHE_LOG_DIR}/yconn_error.log
    CustomLog \${APACHE_LOG_DIR}/yconn_access.log combined
</VirtualHost>
EOF

# Standard-Site deaktivieren, YCONN aktivieren
a2dissite 000-default.conf 2>/dev/null || true
a2ensite yconn.conf

# Apache testen + neu laden
apache2ctl configtest
systemctl reload apache2

echo ""
echo "=== Apache Reverse Proxy aktiv ==="
echo "  http://$SERVER_NAME  →  http://127.0.0.1:8000"
echo ""
echo "Benutzer öffnen im Browser:"
echo "  http://$SERVER_NAME/cockpit/login.html"
