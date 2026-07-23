"""
Einmalig ausfuehren: bereinigt handlers.py (loescht doppelten Code nach dem HANDLERS-Dict).
Ausfuehren: python fix_handlers.py
"""
import re, sys

path = r"C:\WF\sap-robots\worker\handlers.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

# Finde das ERSTE korrekte Ende des HANDLERS-Dicts:
#   ("BAPI", "COPA_SALES_REPORT"):       copa_sales_report,
# }
# danach kommt Muell - wir schneiden alles danach weg.

marker = '    ("BAPI", "COPA_SALES_REPORT"):       copa_sales_report,\n}'

idx = content.find(marker)
if idx == -1:
    print("FEHLER: Marker nicht gefunden. Datei unveraendert.")
    sys.exit(1)

# Alles bis einschliesslich des Markers behalten
clean = content[:idx + len(marker)] + "\n"

with open(path, "w", encoding="utf-8") as f:
    f.write(clean)

lines = clean.count("\n")
print(f"OK – handlers.py auf {lines} Zeilen bereinigt.")
