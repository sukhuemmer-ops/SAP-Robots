# 🗓️ Zinsbuchungs-Erinnerung — Juni 2026

**Buchungsmonat:** Juni 2026  
**Buchungsdatum:** 30.06.2026 (letzter Kalendertag)  
**SAP-User:** HUEMMKMA  
**System:** SEQ (Produktivsystem) — 172.28.189.11 | Sysnr 05 | Mandant 600

---

## ✅ Checkliste Vorbereitung

- [ ] Bridge starten: `C:\WF\sap-robots\Bridge starten.bat`
- [ ] Cockpit öffnen: `C:\WF\sap-robots\cockpit\zinsen.html`
- [ ] Periode im Cockpit prüfen: **06 / 2026**
- [ ] SAP-System **SEQ** ausgewählt (nicht SEP!)
- [ ] SAP-Passwort bereithalten (HUEMMKMA / SEQ)

---

## 📋 Buchungsübersicht

| Darlehen | Partner-BK | Gesellschaft | Währung |
|----------|-----------|--------------|---------|
| 014      | VV9       | Catensys Holding | EUR |
| 015      | VV9       | Catensys Holding | EUR |
| 011      | VV9       | Catensys Holding | EUR |
| 020      | VV9       | Catensys Holding | EUR |
| 021      | VV9       | Catensys Holding | EUR |
| 022      | VV9       | Catensys Holding | EUR |
| 023      | VV9       | Catensys Holding | EUR |
| 024      | VV9       | Catensys Holding | EUR |
| 025      | VV9       | Catensys Holding | EUR |
| 013      | 0436      | Catensys China   | CNY |
| 009      | 0438      | Catensys Korea   | USD |

**Darlehensgeber (DG):** 0435 — Catensys Germany GmbH  
→ Konto 120000/120020 | GK 570200 | keine Kostenstelle

**Darlehensnehmer (DN):** VV9 / 0436 / 0438  
→ Konto 420200 | GK 759200 | Kostenstelle + Profitcenter A-0101-000

---

## 🖱️ Buchungsschritte im Cockpit

- [ ] Button **"▶ Alle buchen"** klicken
- [ ] SAP-Passwort eingeben → Buchung starten
- [ ] Alle Statuszeilen auf **✓ Grün** prüfen
- [ ] Bei Fehler: SAP-Log und Bridge-Log prüfen

---

## ⚠️ Wichtige Hinweise

- **Ausschließlich SEQ (Produktivsystem)** verwenden — kein SEP
- Bei `RFC_NO_AUTHORITY` für RFCPING: Bridge verwendet automatisch Service-Account-Fallback (.env)
- Buchungsdatum = **30.06.2026** (letzter Kalendertag des Buchungsmonats)
- Konto 570200 (DG): **keine Kostenrechnungsrelevanz**
- Konto 759200 (DN): **Kostenstelle + Profitcenter A-0101-000 erforderlich**

---

*Erstellt automatisch am 30.06.2026*
