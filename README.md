# YCONN — Komplettlösung

Dieses Repository enthält das Grundgerüst für vier SAP-Finance-Robots
(Robot-AP, Robot-AR, Robot-GL, Robot-AA), die wiederkehrende Aufgaben in
SAP automatisiert ausführen.

## Architektur in 3 Schichten

```
┌─────────────────────┐    HTTPS / WebSocket    ┌──────────────────────────┐
│  Cockpit (Web-UI)   │ ◄──────────────────────►│  Orchestrator (FastAPI)  │
│  sap-robot-cockpit  │                          │  REST + APScheduler      │
│  Live-Artifact      │                          │  SQLite                  │
└─────────────────────┘                          └────────────┬─────────────┘
                                                              │ Poll/Result
                                                              ▼
                                            ┌─────────────────────────────────┐
                                            │  Worker (Windows-VM pro Robot)  │
                                            │  Python + pyrfc + pywin32       │
                                            └────────────┬────────────────────┘
                                                              │ RFC / GUI Scripting
                                                              ▼
                                                  ┌─────────────────────────┐
                                                  │     SAP ECC / S/4HANA   │
                                                  └─────────────────────────┘
```

## Verzeichnisstruktur

```
sap-robots/
├── orchestrator/        # FastAPI-Backend
│   ├── main.py          # Robots, Tasks, Schedules, Runs, Worker-API
│   └── requirements.txt
└── worker/              # Python-Worker (pro Robot ein Prozess)
    ├── worker.py        # Polling-Loop
    ├── handlers.py      # Konkrete SAP-Handler (BAPI / GUI / Batch)
    ├── requirements.txt
    └── .env.example     # Umgebungsvariablen-Vorlage
```

Das **Cockpit** läuft separat im Cowork-Artifact `sap-robot-cockpit`.

## Schnellstart (Entwicklung)

### 1. Orchestrator starten

```bash
cd orchestrator
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Die API-Doku ist nun unter <http://localhost:8000/docs> erreichbar.
Die SQLite-DB `orchestrator.db` wird automatisch angelegt und mit den vier
Robots (AP/AR/GL/AA) befüllt.

### 2. Eine erste Task anlegen

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"robot_id\":\"AP\",\"name\":\"Test-Buchung\",\"tcode\":\"BAPI_ACC_DOCUMENT_POST\",\"method\":\"BAPI\",\"description\":\"Testbeleg im QAS-Mandant\",\"parameters\":\"{}\"}"
```

### 3. Worker starten (auf Windows-VM mit SAP GUI)

```bat
cd worker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pywin32 pyrfc                  REM nur auf Windows-VM mit SAP GUI / RFC SDK
copy .env.example .env
notepad .env                               REM Werte eintragen, NIEMALS commiten
python worker.py
```

### 4. Lauf anstoßen

Cockpit öffnen → Aufgabe → ► Start. Oder per API:

```bash
curl -X POST http://localhost:8000/tasks/1/run
```

Der Worker übernimmt den Job innerhalb des nächsten Poll-Intervalls und
meldet das Ergebnis zurück.

## Cockpit an den Orchestrator anbinden

Das aktuelle Cockpit-Artifact simuliert die Ausführung im Browser. Um es an
das echte Backend anzuschließen, in `sap-robot-cockpit.html` die Funktion
`runTask()` so abändern:

```js
function runTask(id) {
  fetch(`http://localhost:8000/tasks/${id}/run`, { method: "POST" })
    .then(r => r.json())
    .then(run => log("info", `Run ${run.id} eingereiht (Server-seitig).`));
  pollRunStatus(id);
}
```

und `pollRunStatus()` ergänzen, das alle paar Sekunden `/runs?task_id=…` lädt
und den UI-Status aktualisiert.

## Sicherheit (Pflicht vor Produktion!)

* **Service-User pro Robot** im SAP-System mit minimalen Berechtigungen
  (Berechtigungsobjekte F_BKPF_BUK / F_BKPF_BLA / A_S_ANLA etc. nur lesend/schreibend
  für die jeweilige Domäne).
* **Geheimnisse** in Azure Key Vault / HashiCorp Vault / Windows-DPAPI ablegen,
  nicht in `.env` auf der VM. Die `.env.example` zeigt nur die Variablennamen.
* **Audit-Log** im Orchestrator: wer hat wann welchen Task gestartet, was kam
  zurück. Der `Run`-Tabelle reicht das fast — ergänze ein `triggered_by`-Feld
  und eine eigene Audit-Tabelle für sicherheitsrelevante Aktionen.
* **Vier-Augen-Prinzip** für kritische Buchungen (z. B. Zahllauf F110):
  Cockpit-Button löst nur den Vorschlag aus, die Durchführung erfordert eine
  zweite Bestätigung eines Approvers.
* **TLS + Auth** zwischen Cockpit ↔ Orchestrator und Orchestrator ↔ Worker
  (z. B. mTLS oder signierte JWTs). Im Skelett bewusst weggelassen, um den
  Code lesbar zu halten — _vor_ Produktivnahme nachrüsten.
* **Test-Mandant zuerst!** Erste 1-2 Perioden ausschließlich gegen QAS,
  Ergebnisse mit dem fachlichen Owner abnehmen, erst dann Cut-Over.

## Implementierungs-Reihenfolge (empfohlen)

1. **Process Discovery** je Bereich: welche Tasks, welche Volumina, welche
   Inputs, welche Ausnahmen. 1-2 Wochen pro Bereich.
2. **Robot-AP zuerst** — meist die höchste Last und am besten geeignet
   (klare Inputs aus E-Mail/EDI, klares Erfolgskriterium = Belegnummer).
3. **Erst BAPI**, dann GUI-Scripting. BAPIs sind stabiler über
   SAP-Releasewechsel hinweg.
4. **Monitoring von Tag 1** — jeder Lauf produziert Log + Status. Alerts an
   den fachlichen Owner bei `status=error`.
5. **Robot-AR / -GL / -AA** in dieser Reihenfolge, jeweils mit
   Parallelbetrieb 1 Periode bevor manuelle Tätigkeit eingestellt wird.

## Alternativen

Falls dein Unternehmen bereits eine RPA-Plattform betreibt, lohnt es sich
zu prüfen, ob die Worker-Schicht durch **UiPath**, **Power Automate** oder
**Blue Prism** ersetzt wird — der Orchestrator und das Cockpit bleiben dann
identisch und sprechen statt eines Custom-Workers die jeweilige RPA-API an.
