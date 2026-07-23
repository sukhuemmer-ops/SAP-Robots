"""
Repariert orchestrator\main.py bei Syntax-Fehlern durch Zeilenkorruption.
Wird automatisch von fix_orchestrator.bat aufgerufen.
"""
import ast, re, shutil, sys
from pathlib import Path

MAIN = Path(__file__).parent / "orchestrator" / "main.py"
if not MAIN.exists():
    print(f"FEHLER: {MAIN} nicht gefunden.")
    sys.exit(1)

shutil.copy2(MAIN, MAIN.with_suffix(".py.bak"))
text = MAIN.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines(keepends=True)
print(f"  Datei: {len(lines)} Zeilen")

fixed = 0
for i, line in enumerate(lines):
    s = line.lstrip()
    # Korruption: "rn Response..." statt "return Response..."
    if re.match(r"rn Response\(", s):
        indent = " " * (len(line) - len(line.lstrip()))
        lines[i] = indent + "return Response(status_code=204)\n"
        print(f"  Fix Zeile {i+1}: 'rn Response...' -> 'return Response(status_code=204)'")
        fixed += 1
    # Abgebrochenes "retu" oder "retur" am Zeilenende
    elif re.match(r"retu[rn]?\s*$", s):
        indent = " " * (len(line) - len(line.lstrip()))
        lines[i] = indent + "return Response(status_code=204)\n"
        print(f"  Fix Zeile {i+1}: unvollstaendiges '{s.strip()}' -> 'return Response(status_code=204)'")
        fixed += 1

if fixed == 0:
    print("  Kein bekanntes Fehlermuster gefunden.")
    sys.exit(1)

MAIN.write_text("".join(lines), encoding="utf-8")
print(f"  {fixed} Korrektur(en) gespeichert.")

# Abschliessende Syntax-Pruefung
try:
    ast.parse(MAIN.read_text(encoding="utf-8"))
    print("  Syntax OK nach Reparatur.")
except SyntaxError as e:
    print(f"  Noch Fehler: Zeile {e.lineno}: {e.msg}")
    sys.exit(1)
