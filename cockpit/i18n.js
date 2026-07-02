/**
 * YCONN i18n — Bilingual Support (EN default / DE toggle)
 * Usage:
 *   T('Deutscher Text')         → returns EN text if lang=en
 *   applyI18n(rootElement)      → translates DOM subtree
 *   window.toggleLang()         → switch EN↔DE
 *   localStorage 'yconn_lang'   → 'en' | 'de'
 */
(function () {
  'use strict';

  const LS_KEY = 'yconn_lang';

  /* ── helpers ─────────────────────────────────────── */
  function getLang() { return localStorage.getItem(LS_KEY) || 'en'; }
  function setLang(l) {
    localStorage.setItem(LS_KEY, l);
    document.documentElement.lang = l;
    applyI18n();
    updateToggleBtn();
  }

  /* ── Translation Dictionary  DE → EN ─────────────── */
  const DE_EN = {
    /* ── General App & Navigation ──────────────────── */
    'Übersicht': 'Overview',
    'YCONN — Übersicht': 'YCONN — Overview',
    'Startseite': 'Home',
    'Abmelden': 'Logout',
    'Anmelden': 'Login',
    'Verbindungen': 'Connections',
    'Benutzer': 'Users',
    'Benutzerverwaltung': 'User Management',
    'Benutzer-\nverwaltung': 'User\nManagement',
    'Benutzer-verwaltung': 'User Management',
    'App-Regeln': 'App Rules',
    'Digitales Gehirn': 'Digital Brain',
    'Kontrollzentrum': 'Control Center',
    'Stammdaten': 'Master Data',
    'Sprachassistent': 'Voice Assistant',
    'Hintergrund': 'Background',
    'Bereit': 'Ready',
    'Lädt…': 'Loading…',
    'Laden...': 'Loading...',
    'Wird geladen…': 'Loading…',
    'Prüfe...': 'Checking...',
    'Prüfe…': 'Checking…',
    'Aktualisieren': 'Refresh',
    '↻ Jetzt': '↻ Now',
    '← Startseite': '← Home',
    '← Start': '← Home',
    'Zurück': 'Back',
    'Abbrechen': 'Cancel',
    'Speichern': 'Save',
    'Schließen': 'Close',
    'Löschen': 'Delete',
    'Bearbeiten': 'Edit',
    'Hinzufügen': 'Add',
    'Suchen': 'Search',
    'Weiter': 'Next',
    'Bestätigen': 'Confirm',
    'Ja': 'Yes',
    'Nein': 'No',
    'Offen': 'Open',
    'Erledigt': 'Done',
    'Fehler': 'Error',
    'Erfolg': 'Success',
    'Warnung': 'Warning',
    'Aktiv': 'Active',
    'Inaktiv': 'Inactive',
    'Alle': 'All',
    'Keine Daten.': 'No data.',
    'Keine Einträge.': 'No entries.',
    'Nicht verfügbar': 'Not available',
    '● Aktiv': '● Active',
    '○ Inaktiv': '○ Inactive',
    'Gesamt': 'Total',
    'Anzahl': 'Count',
    'Status': 'Status',
    'Name': 'Name',
    'Beschreibung': 'Description',
    'Typ': 'Type',
    'Erstellt': 'Created',
    'Geändert': 'Modified',
    'Datum': 'Date',
    'Von': 'From',
    'Bis': 'To',
    'Aktion': 'Action',
    'Aktionen': 'Actions',
    'Notizen': 'Notes',
    'Neu laden': 'Reload',
    '↺ Neu laden': '↺ Reload',
    '↺ Zurücksetzen': '↺ Reset',
    '✓ Übernehmen': '✓ Apply',

    /* ── SAP General ────────────────────────────────── */
    'Buchungskreis': 'Company Code',
    'Buchung': 'Posting',
    'Buchungen': 'Postings',
    'Buchungsperiode': 'Posting Period',
    'Buchungsdatum': 'Posting Date',
    'Belegdatum': 'Document Date',
    'Geschäftsjahr': 'Fiscal Year',
    'Periode': 'Period',
    'Betrag': 'Amount',
    'Währung': 'Currency',
    'Belegnummer': 'Document Number',
    'Belegtyp': 'Document Type',
    'Belegtext': 'Document Text',
    'Sachkonto': 'G/L Account',
    'Gegenkonto': 'Offset Account',
    'Kostenstelle': 'Cost Center',
    'Profitcenter': 'Profit Center',
    'Zahlungsbedingung': 'Payment Terms',
    'Zahlungsbedingungen': 'Payment Terms',
    'Verkaufsorganisation': 'Sales Organization',
    'Vertriebsweg': 'Distribution Channel',
    'Sparte': 'Division',
    'Mandant': 'Client',
    'SAP-System': 'SAP System',
    'SAP-Verbindungen': 'SAP Connections',
    'SAP-Benutzer': 'SAP User',
    'SAP-Passwort': 'SAP Password',
    'Passwort': 'Password',
    'Passwort eingeben…': 'Enter password…',
    'SAP-Anmeldung': 'SAP Login',
    'Bridge verbunden': 'Bridge connected',
    'Bridge prüfen': 'Check bridge',
    'SIM-Modus': 'SIM mode',
    'SIM-Modus (Bridge offline)': 'SIM mode (Bridge offline)',
    'Verbunden': 'Connected',
    'Getrennt': 'Disconnected',
    'Produktivsystem': 'Production system',
    'Qualitätssystem': 'Quality system',

    /* ── Login ──────────────────────────────────────── */
    'YCONN – Anmeldung': 'YCONN – Login',
    'SAP Finance Robots': 'SAP Finance Robots',
    'Anmeldung': 'Login',
    'Benutzer': 'User',
    '– Benutzer auswählen –': '– Select user –',
    'Passwort eingeben…': 'Enter password…',
    'Lade Benutzerliste…': 'Loading user list…',
    'Orchestrator nicht erreichbar.': 'Orchestrator not reachable.',
    'Bitte Benutzer auswählen.': 'Please select a user.',
    'Bitte Passwort eingeben.': 'Please enter password.',
    '✓ Anmeldung erfolgreich…': '✓ Login successful…',
    '✗ Anmeldung fehlgeschlagen.': '✗ Login failed.',
    '⚠ Bridge offline – Anmeldung ohne Verbindungstest.': '⚠ Bridge offline – login without connection test.',

    /* ── Startseite ─────────────────────────────────── */
    'Robots gesamt': 'Robots total',
    'Aufgaben gesamt': 'Tasks total',
    'Konfiguriert': 'Configured',
    'Zuletzt OK': 'Last OK',
    'Letzte 24 Stunden': 'Last 24 hours',
    'Aufgaben': 'Tasks',
    'Robots': 'Robots',
    'Aktivitätslog': 'Activity log',
    'Letzte Ereignisse': 'Recent events',
    'Leeren': 'Clear',
    'Keine Logs.': 'No logs.',
    'Logs geleert': 'Logs cleared',
    'Robot starten': 'Start robot',
    'Starten': 'Start',
    'Geplant': 'Scheduled',
    '▶ Alle starten': '▶ Start all',
    'Keine Aufgaben konfiguriert.': 'No tasks configured.',
    'Schnellzugriff': 'Quick access',
    'Alle Aufgaben': 'All tasks',
    'Zeitpläne': 'Schedules',
    'Reports': 'Reports',
    'Buchung Zinsen': 'Interest Posting',
    'Verbindungs-editor': 'Connection editor',
    'Bridge prüfen': 'Check Bridge',
    'Logs leeren': 'Clear logs',
    '● Verfügbar': '● Available',
    '● Sprachsteuerung': '● Voice control',
    '⚙ In Entwicklung': '⚙ In development',
    'Finance-Assistentin · SAP · Buchungen · Rechnungen · Darlehen': 'Finance Assistant · SAP · Postings · Invoices · Loans',
    'Zahlungsbedingungen prüfen und korrigieren (XD02 / VK12)': 'Check and correct payment terms (XD02 / VK12)',
    'Ausgangsrechnungen automatisch erstellen': 'Create outgoing invoices automatically',
    'Lohn- und Gehaltsabrechnungen buchen': 'Post payroll accounting',
    'Abgrenzungen, AP/AR-Buchungen verarbeiten': 'Process accruals, AP/AR postings',
    'Rückstellungen planen und buchen': 'Plan and post provisions',
    'Abschreibungslauf ausführen und buchen': 'Execute and post depreciation run',

    /* ── Zinsen (Interest) ──────────────────────────── */
    'YCONN – Buchung Zinsen': 'YCONN – Interest Posting',
    'Buchung Zinsen': 'Interest Posting',
    '💶 Buchung Zinsen': '💶 Interest Posting',
    'Zinsbuchung': 'Interest posting',
    'Zinsbuchungen': 'Interest postings',
    'Darlehen': 'Loan',
    'Darlehens-Nr.': 'Loan No.',
    'Darlehensgeber': 'Lender',
    'Darlehensnehmer': 'Borrower',
    'Darlehensbetrag': 'Loan amount',
    'Zinssatz': 'Interest rate',
    'Laufzeit von': 'Term from',
    'Laufzeit bis': 'Term to',
    'Darlehensart': 'Loan type',
    '🔗 IC-Darlehen': '🔗 IC Loan',
    '🌐 Externes Darlehen': '🌐 External Loan',
    'Restschuld': 'Remaining balance',
    'Zinsen EUR': 'Interest EUR',
    'Zinsen CNY': 'Interest CNY',
    'Zinsen USD': 'Interest USD',
    'Aktive Darlehen': 'Active loans',
    'Buchungsstatus': 'Posting status',
    '💶 Zinsen-Buchungsliste': '💶 Interest Posting List',
    'Bearbeitungsmodus aktiv – Zinsbeträge können direkt in der Tabelle geändert werden': 'Edit mode active – interest amounts can be changed directly in the table',
    '✏️ Beträge bearbeiten': '✏️ Edit amounts',
    '📥 Excel Export': '📥 Excel Export',
    '🗑 Zurücksetzen': '🗑 Reset',
    '➕ Darlehen anlegen': '➕ Create loan',
    '🔖 SAP Buchungs-Log': '🔖 SAP Posting Log',
    'Storno': 'Reversal',
    '⟲ Storno': '⟲ Reverse',
    '🗑 Bereinigen': '🗑 Clean up',
    '▶ SAP Buchen': '▶ Post to SAP',
    '▶ Jetzt buchen': '▶ Post now',
    '📦 Nachholbuchung': '📦 Catch-up posting',
    '➕ Neues Darlehen anlegen': '➕ Create new loan',
    'Stammdaten': 'Master data',
    'Darlehensnummer': 'Loan number',
    'Buchungskreis (Darlehensnehmer)': 'Company Code (Borrower)',
    'Monatlicher Zinsbetrag (auto-berechnet, überschreibbar)': 'Monthly interest amount (auto-calculated, overridable)',
    'IC-Buchung (Intercompany)': 'IC Posting (Intercompany)',
    '🏦 Darlehensgeber (DG) – Kreditgeber': '🏦 Lender (DG) – Creditor',
    '🏢 Darlehensnehmer (DN) – Kreditnehmer': '🏢 Borrower (DN) – Debtor',
    'Sachkonto DG (Forderungen IC / Interco Receivable)': 'G/L Account DG (IC Receivable)',
    'Ertragskonto DG (Zinserträge IC)': 'Revenue Account DG (IC Interest Income)',
    'Verbindlichkeitskonto DN (Interco Payable)': 'Liability Account DN (Interco Payable)',
    'Aufwandskonto DN (Zinsaufwand IC)': 'Expense Account DN (IC Interest Expense)',
    'Kostenstelle DN': 'Cost Center DN',
    'Profitcenter DN': 'Profit Center DN',
    '💾 Speichern': '💾 Save',
    '⚡ Produktivsystem': '⚡ Production system',
    '🔬 Qualitätssystem': '🔬 Quality system',
    'Aktive Verbindung:': 'Active connection:',
    '✓ Übernehmen': '✓ Apply',
    'TEST-MODUS AKTIV – Keine echten SAP-Buchungen werden durchgeführt': 'TEST MODE ACTIVE – No real SAP postings are performed',
    '🧪 TEST-MODUS': '🧪 TEST MODE',
    'Warte auf Ausführung...': 'Waiting for execution...',
    '📊 Simulierte Belege (TEST – keine echten SAP-Dokumente)': '📊 Simulated documents (TEST – no real SAP documents)',
    'SAP-Buchung noch nicht verfügbar': 'SAP posting not yet available',
    '✅ SAP Buchung – Bestätigung': '✅ SAP Posting – Confirmation',
    'Von Periode': 'From period',
    'Buchungsperiode (= Bis)': 'Posting period (= To)',
    'BERECHNUNG – Zinsdetails': 'CALCULATION – Interest details',
    'Gesamtbetrag (auto-berechnet, überschreibbar)': 'Total amount (auto-calculated, overridable)',
    '🗑 Nachholbuchung entfernen': '🗑 Remove catch-up posting',
    'Modus': 'Mode',
    'Belegart': 'Document type',
    '⚙ Einstellungen': '⚙ Settings',
    '⚙ SAP System auswählen': '⚙ Select SAP system',
    'Transaktion': 'Transaction',
    'Host': 'Host',
    'Mandant': 'Client',
    'Instance': 'Instance',
    'Inst.': 'Inst.',
    'RFC-Port': 'RFC port',
    '📋 Darlehen': '📋 Loans',
    '📂 Darlehen-Stammdaten': '📂 Loan Master Data',
    '🔌 Schnittstelle': '🔌 Interface',
    '🗄 Stammdaten': '🗄 Master Data',
    '📅 Zeitpläne': '📅 Schedules',
    '🔎 SAP-Übergabe': '🔎 SAP Transfer',
    'Monate': 'Months',
    'Januar': 'January',
    'Februar': 'February',
    'März': 'March',
    'April': 'April',
    'Mai': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'August': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Dezember': 'December',
    'Nr.': 'No.',
    'Partner': 'Partner',
    'Konto': 'Account',
    'Text': 'Text',
    'Währ.': 'Curr.',
    'Test-Belegnr.': 'Test doc. no.',
    'Partner Code': 'Partner code',
    'Company Code': 'Company Code',
    'Buchungstext': 'Posting text',
    'SAP Belegnr.': 'SAP doc. no.',

    /* ── Rechnungen (Invoices) ──────────────────────── */
    'Rechnungserstellung – YCONN Cockpit': 'Invoice Creation – YCONN Cockpit',
    '🧾 Rechnungserstellung': '🧾 Invoice Creation',
    'Rechnungen': 'Invoices',
    'Rechnungserstellung': 'Invoice Creation',
    'Rechnungsliste': 'Invoice list',
    '📋 Rechnungsliste': '📋 Invoice List',
    'Kunden-Nr': 'Customer No.',
    'Kunden-Nr.': 'Customer No.',
    'Kunden-Nr *': 'Customer No. *',
    'Kundenname': 'Customer name',
    'Pos.': 'Pos.',
    'Leistungsart': 'Service type',
    'MWSt-Code': 'Tax code',
    'Rechnungsnr.': 'Invoice no.',
    'Auftragsnr.': 'Order no.',
    'Alle Status': 'All statuses',
    'Erstellt ✓': 'Created ✓',
    'Storniert': 'Reversed',
    'Alle Perioden': 'All periods',
    '📅 Akt. + Vormonat': '📅 Current + previous month',
    '📥 Excel': '📥 Excel',
    '➕ Neue Rechnung': '➕ New invoice',
    '📋 MS → Akt. Monat': '📋 MS → Current month',
    '📦 Batch buchen': '📦 Batch post',
    '🗑 Daten löschen': '🗑 Delete data',
    'Bitte XLSM-Datei hochladen, um die Rechnungsliste anzuzeigen.': 'Please upload XLSM file to display the invoice list.',
    '➕ Neue Rechnung erfassen': '➕ Create new invoice',
    'Periode (MM/YYYY)': 'Period (MM/YYYY)',
    'SAP-Datum (YYYYMMDD)': 'SAP date (YYYYMMDD)',
    'POSITIONEN': 'LINE ITEMS',
    '+ Position': '+ Item',
    'Gesamt:': 'Total:',
    '📧 E-Mail Konfiguration': '📧 Email Configuration',
    'Empfänger': 'Recipient',
    'Absender': 'Sender',
    'SMTP-Host': 'SMTP Host',
    'Auto-Send': 'Auto-Send',
    '➕ Konfiguration hinzufügen': '➕ Add configuration',
    'Auto-Versand nach Rechnungserstellung': 'Auto-send after invoice creation',
    'Betreff-Vorlage': 'Subject template',
    'E-Mail Text-Vorlage': 'Email body template',
    'Verschlüsselung': 'Encryption',
    '✅ Aktiv': '✅ Active',
    '⏸ Inaktiv': '⏸ Inactive',
    'Manuell (kein Auto-Send)': 'Manual (no auto-send)',
    'Automatisch senden': 'Send automatically',
    '📬 Versand-Historie': '📬 Send History',
    'Alle Kunden': 'All customers',
    '🔄 Aktualisieren': '🔄 Refresh',
    'Fehlermeldung': 'Error message',
    '📨 Rechnung in SAP erstellen': '📨 Create invoice in SAP',
    '🔍 Vorübergabe-Prüfung': '🔍 Pre-transfer check',
    'SAP-Passwort für': 'SAP password for',
    '✕ Abbrechen': '✕ Cancel',
    '🔬 Debug-Lauf': '🔬 Debug run',
    '📨 Jetzt erstellen': '📨 Create now',
    '⛔ Bitte Fehler beheben': '⛔ Please fix errors',
    '✏️ SAP-Belegnummer eintragen': '✏️ Enter SAP document number',
    'Auftragsnr. (VA01) – optional': 'Order no. (VA01) – optional',
    'Faktura-Nr. (VF01) – optional': 'Invoice no. (VF01) – optional',
    '✓ Erstellt': '✓ Created',
    '● Offen': '● Open',
    '↩ Storniert': '↩ Reversed',
    '📦 Batch-Buchung — Excel Control-Sheet': '📦 Batch Posting — Excel Control Sheet',
    'Buchungsprotokoll': 'Posting log',
    'Zeile': 'Line',
    'Kunde': 'Customer',
    '✕ Schließen': '✕ Close',
    '🔬 Debug (1. Zeile)': '🔬 Debug (1st row)',
    '📦 Alle buchen': '📦 Post all',
    '📨 Rechnungen erstellen': '📨 Create invoices',
    '📨 Alle buchen': '📨 Post all',
    '✓ Konfiguration gespeichert': '✓ Configuration saved',
    'Kein Treffer für aktuelle Filter.': 'No match for current filters.',
    '↺ Filter zurücksetzen': '↺ Reset filters',
    'Bitte XLSM-Datei hochladen oder Rechnung manuell erfassen.': 'Please upload XLSM file or enter invoice manually.',

    /* ── Payroll ────────────────────────────────────── */
    'YCONN – PayRoll-Buchungen': 'YCONN – Payroll Postings',
    'PayRoll-Buchungen': 'Payroll Postings',
    'FIBU LOGA – Lohn & Gehalt SAP-Buchung': 'FIBU LOGA – Payroll SAP Posting',
    '🔍 SAP-Übergabe prüfen': '🔍 Check SAP transfer',
    '▶ In SEQ buchen': '▶ Post to SEQ',
    'FIBU LOGA CSV-Datei hochladen': 'Upload FIBU LOGA CSV file',
    'Noch keine Datei geladen': 'No file loaded yet',
    'Bitte lade eine FIBU LOGA CSV-Datei hoch.': 'Please upload a FIBU LOGA CSV file.',
    '📋 Input': '📋 Input',
    '📒 Buchungsliste': '📒 Posting list',
    '✅ Plausibilität': '✅ Plausibility',
    '🔌 SAP-Übergabe': '🔌 SAP Transfer',
    '📂 Importhistorie': '📂 Import history',
    '⚠ Kostenstellen-Pflicht verletzt': '⚠ Cost center requirement violated',
    '✏ Kostenstellen anpassen': '✏ Adjust cost centers',
    '✓ Kostenstellen wurden übernommen – Buchungsliste aktualisiert': '✓ Cost centers applied – posting list updated',
    '✏ Kostenstellen korrigieren': '✏ Correct cost centers',
    '⚠ Monats-Import bereits vorhanden': '⚠ Monthly import already exists',
    'Abbrechen (nicht speichern)': 'Cancel (do not save)',
    '⚠ Trotzdem importieren': '⚠ Import anyway',
    'Eingabedaten (LOGA)': 'Input data (LOGA)',
    'Buchungsliste – SAP Output': 'Posting list – SAP output',
    '⬇ CSV Export': '⬇ CSV Export',
    'Referenz': 'Reference',
    'Belegkopftext': 'Document header text',
    'Buchungsschlüssel': 'Posting key',
    'Soll (Debit) Σ': 'Debit Σ',
    'Haben (Credit) Σ': 'Credit Σ',
    'Differenz': 'Difference',
    'Soll – Haben': 'Debit – Credit',
    'Ausgeglichen?': 'Balanced?',
    'Kostenstellen 6*/7*': 'Cost centers 6*/7*',
    'Zeilen mit KST-Pflicht': 'Lines requiring cost center',
    'Auto-ergänzt': 'Auto-supplemented',
    'Kontensalden Übersicht': 'Account balances overview',
    'Bezeichnung': 'Description',
    'Summe': 'Total',
    'Zeilen': 'Lines',
    'Buchungsdatum': 'Posting date',
    'Belegdatum': 'Document date',
    'App-Regel: PayRoll-Buchungen immer Belegtyp SA (gesperrt)': 'App rule: Payroll postings always document type SA (locked)',
    '← Zurück zur Plausibilität': '← Back to plausibility',
    '▶ Jetzt in SEQ buchen': '▶ Post to SEQ now',
    '📋 JSON kopieren': '📋 Copy JSON',
    '⬇ JSON Download': '⬇ JSON download',
    '📂 Importhistorie': '📂 Import history',
    'Suche Datei, Monat, Status…': 'Search file, month, status…',
    'Importiert': 'Imported',
    'Gebucht': 'Posted',
    'Fehler': 'Error',
    '⏳ Lade Importhistorie…': '⏳ Loading import history…',
    'Noch keine Importe vorhanden': 'No imports yet',
    'Änderungen ausstehend': 'Changes pending',
    'SAP-Buchung – BAPI_ACC_DOCUMENT_POST': 'SAP Posting – BAPI_ACC_DOCUMENT_POST',
    'SAP-Übergabe prüfen – Storno': 'Check SAP transfer – Reversal',
    '↩ Jetzt in SAP stornieren': '↩ Reverse in SAP now',
    'Prüfung': 'Check',
    'Buchungsrichtung': 'Posting direction',
    'Steuerkennzeichen': 'Tax key',
    'Erläuterung': 'Explanation',
    'Vorzeichen': 'Sign',
    'Einzel': 'Individual',
    'Eintrag': 'Entry',

    /* ── Kundenstamm ────────────────────────────────── */
    'SAP Kundenstamm': 'SAP Customer Master',
    '🗃 SAP Kundenstamm': '🗃 SAP Customer Master',
    'Kundenübersicht': 'Customer overview',
    'Zu ändern': 'To change',
    'Teilweise': 'Partial',
    '0 von 0 erledigt': '0 of 0 done',
    'Zu ändern': 'To change',
    'Korrekt': 'Correct',
    '📋 Änderungsübersicht': '📋 Change overview',
    '🔍 Kunden-Detail': '🔍 Customer detail',
    '📜 Änderungsprotokoll': '📜 Change log',
    'Zahlungsbedingungen – Änderungsprotokoll': 'Payment Terms – Change Log',
    'Kundennummer filtern…': 'Filter customer no.…',
    'Datum / Zeit': 'Date / Time',
    'Kunden-Nr': 'Customer No.',
    'TCode': 'TCode',
    'BK': 'CC',
    'Vertrag': 'Contract',
    'Alt': 'Old',
    '→ Neu': '→ New',
    'System': 'System',
    'Benutzer': 'User',
    'Zahlungsbedingungen – Änderungsübersicht': 'Payment Terms – Change Overview',
    '✓ Alle als erledigt': '✓ Mark all as done',
    '↺ Zurücksetzen': '↺ Reset',
    'Transaktion / Bereich': 'Transaction / Area',
    'Alte Zahlungsbedingung': 'Old payment terms',
    'Neue Zahlungsbedingung': 'New payment terms',
    'Ausführen': 'Execute',
    'Kunden-Detailansicht': 'Customer detail view',
    'Wählen Sie einen Kunden aus der Seitenleiste.': 'Select a customer from the sidebar.',
    '🔐 SAP-Anmeldung': '🔐 SAP Login',
    'SAP GUI wird automatisch gestartet. Eingaben werden gespeichert.': 'SAP GUI will be started automatically. Inputs will be saved.',
    'SAP Logon Eintrag': 'SAP Logon entry',
    'Alle Checks bestanden': 'All checks passed',
    'Mind. ein Check fehlgeschlagen': 'At least one check failed',
    'Stammdaten – Kundenstamm (KNVV)': 'Master Data – Customer Master (KNVV)',
    'Konditionssätze – ZB00': 'Condition Records – ZB00',
    'Kundenverträge & Fakturaliste (VF04)': 'Customer Contracts & Invoice List (VF04)',

    /* ── Verbindungen ───────────────────────────────── */
    'SAP Verbindungen Konfiguration': 'SAP Connections Configuration',
    'Felder anzeigen / bearbeiten': 'Show / edit fields',
    'Verbindung pruefen': 'Test connection',
    'Als JSON': 'As JSON',
    'SNC aktiviert': 'SNC enabled',
    'Sprache': 'Language',
    'Auto-Login': 'Auto-Login',
    'Scripting auf Client': 'Scripting on client',
    'Scripting auf Server (RZ11)': 'Scripting on server (RZ11)',
    'Wartezeit bis ready (Sek)': 'Wait time until ready (sec)',
    'Auth-Methode': 'Auth method',
    'TLS-Validierung': 'TLS validation',
    'Host gesetzt': 'Host set',
    'Mandant gesetzt': 'Client set',
    'Vault-Referenz': 'Vault reference',
    'SNC in PRD': 'SNC in PRD',
    'SAPLogon-Verbindung': 'SAPLogon connection',
    'Scripting Client': 'Scripting client',
    'Basis-URL https://': 'Base URL https://',
    'Secret-Ref': 'Secret ref',
    'TLS PRD': 'TLS PRD',

    /* ── Benutzer ───────────────────────────────────── */
    'SAP Benutzerverwaltung – YCONN': 'SAP User Management – YCONN',
    'Verbinde mit Orchestrator…': 'Connecting to Orchestrator…',
    '✓ Orchestrator verbunden': '✓ Orchestrator connected',
    '✗ Orchestrator nicht erreichbar – Bitte starten': '✗ Orchestrator not reachable – Please start',
    'Benutzer gesamt': 'Total users',
    'SAP-Systeme': 'SAP systems',
    'Suche nach Name, Benutzername, System…': 'Search by name, username, system…',
    'Alle Rollen': 'All roles',
    'Alle Status': 'All statuses',
    '⟳ Laden': '⟳ Load',
    'SAP-Login': 'SAP login',
    'Wird geladen…': 'Loading…',
    '✏ Bearbeiten': '✏ Edit',
    '⧉ Kopieren': '⧉ Copy',
    '🗑 Löschen': '🗑 Delete',
    'Keine Benutzer gefunden.': 'No users found.',
    'Benutzer anlegen': 'Create user',
    'Anzeigename': 'Display name',
    'z. B. Max Mustermann': 'e.g. John Smith',
    'SAP-Benutzername': 'SAP username',
    'Rolle': 'Role',
    'SAP-Verbindung': 'SAP connection',
    'System-ID': 'System ID',
    'Application Server (ashost)': 'Application Server (ashost)',
    'System-Nr.': 'System No.',
    'DE – Deutsch': 'DE – German',
    'EN – English': 'EN – English',
    'Zuständigkeitsbereich, Berechtigungen, etc.': 'Area of responsibility, permissions, etc.',
    '🔑 Verbindungstest (Passwort wird nicht gespeichert)': '🔑 Connection test (password not saved)',
    'SAP-Passwort eingeben…': 'Enter SAP password…',
    'Testen': 'Test',
    '🔑 Verbindungstest': '🔑 Connection test',
    'Fehler beim Laden:': 'Error loading:',
    '✗ Orchestrator nicht erreichbar': '✗ Orchestrator not reachable',

    /* ── App-Regeln ─────────────────────────────────── */
    'YCONN — App-Regeln': 'YCONN — App Rules',
    '📋 App-Regeln': '📋 App Rules',
    'Verbindliche Regeln und Konfigurationsparameter je Modul': 'Binding rules and configuration parameters per module',
    'Legende:': 'Legend:',
    'gesperrt': 'locked',
    'Fest kodiert, nicht änderbar': 'Hard-coded, cannot be changed',
    'auto': 'auto',
    'Automatisch gesetzt/korrigiert': 'Automatically set/corrected',
    'validiert': 'validated',
    'Wird aktiv geprüft': 'Actively checked',
    '● Aktiv': '● Active',
    'In Betrieb': 'In operation',
    '⚙ Geplant': '⚙ Planned',
    'In Entwicklung': 'In development',
    '🔒 Global': '🔒 Global',
    '💼 PayRoll': '💼 PayRoll',
    '💶 Darlehen / Zinsen': '💶 Loans / Interest',
    '🧾 Rechnungserstellung': '🧾 Invoice creation',
    '🏗 Zukünftige Module': '🏗 Future modules',
    '🔒 Globale App-Regeln': '🔒 Global App Rules',
    'Gelten für alle Module und Gesellschaften': 'Apply to all modules and companies',
    'Kürzel': 'Code',
    'Systemtyp': 'System type',
    'SysNr': 'SysNo',
    'Zweck': 'Purpose',

    /* ── Cockpit ────────────────────────────────────── */
    'YCONN Cockpit': 'YCONN Cockpit',
    'Uebersicht': 'Overview',
    'Verbindungen': 'Connections',
    'Darlehen': 'Loans',
    'Logs': 'Logs',
    '📋 Buchungshistorie': '📋 Posting History',
    'Alle': 'All',
    'Abgelaufen': 'Expired',
    'Borrower': 'Borrower',
    'DARLEHEN-NR.': 'LOAN NO.',
    'BORROWER': 'BORROWER',
    'URSPRUNGSBETRAG': 'ORIGINAL AMOUNT',
    'RESTSCHULD': 'REMAINING BALANCE',
    'ZINSSATZ': 'INTEREST RATE',
    'LAUFZEIT': 'TERM',
    '✏️ Bearbeiten': '✏️ Edit',
    '💰 Rückzahlung': '💰 Repayment',
    'Berechnungsparameter': 'Calculation parameters',
    'Betrag (Restschuld)': 'Amount (remaining balance)',
    'Beginn': 'Start',
    'Ende (überschreibbar)': 'End (overridable)',
    'Methode': 'Method',
    '360-Tage': '360-day',
    '365-Tage': '365-day',
    'Tilgung mtl. (0 = endfällig)': 'Monthly repayment (0 = bullet)',
    '💰 Erfasste Rückzahlungen / Tilgungen': '💰 Recorded repayments / amortizations',
    'Darlehen-Enddatum': 'Loan end date',
    'Monatliche Tilgung (0 = endfällig)': 'Monthly repayment (0 = bullet)',
    'Aktuelle Restschuld': 'Current remaining balance',
    '💰 Neue Einzeltilgung / Sondertilgung': '💰 New individual / special repayment',
    'Notiz': 'Note',
    'z.B. Sondertilgung Q2': 'e.g. Special repayment Q2',
    '+ Tilgung speichern & neu berechnen': '+ Save repayment & recalculate',
    '✏️ Stammdaten bearbeiten & neu berechnen': '✏️ Edit master data & recalculate',
    '▸ Enddatum überschrieben': '▸ End date overridden',
    '— Bestehendes Darlehen wählen —': '— Select existing loan —',
    '▶ Berechnen': '▶ Calculate',
    '⬇ CSV': '⬇ CSV',
    '✕ Filter zurücksetzen': '✕ Reset filters',

    /* ── Brain ──────────────────────────────────────── */
    'Digitales Gehirn — YCONN Intelligence': 'Digital Brain — YCONN Intelligence',
    '🧠 Digitales Gehirn': '🧠 Digital Brain',
    'YCONN Knowledge Intelligence System': 'YCONN Knowledge Intelligence System',
    'Knowledge Universe': 'Knowledge Universe',
    'Alle Schichten': 'All layers',
    '+ Wissen hinzufügen': '+ Add knowledge',
    '🧩 Entscheidung': '🧩 Decision',
    '🔍 10W-Audit': '🔍 10W Audit',
    'Decision Engine': 'Decision Engine',
    'Entscheidungs-History': 'Decision History',
    '10W-Audit': '10W Audit',
    'Neuen Wissenseintrag erstellen': 'Create new knowledge entry',
    'Schicht (Layer)': 'Layer',
    'Konzept': 'Concept',
    'Regel': 'Rule',
    'Muster': 'Pattern',
    'Risiko': 'Risk',
    'Prozess': 'Process',
    'Erfahrung': 'Experience',
    'Vorhersage': 'Prediction',
    'Fakt': 'Fact',
    'Schlüssel (eindeutig)': 'Key (unique)',
    'Konfidenz (1–5)': 'Confidence (1–5)',
    '3 — Mittel': '3 — Medium',
    '4 — Hoch': '4 — High',
    '5 — Sehr hoch': '5 — Very high',
    '2 — Niedrig': '2 — Low',
    '1 — Sehr niedrig': '1 — Very low',
    'Titel': 'Title',
    'Zusammenfassung': 'Summary',
    'Quell-Modul': 'Source module',
    'Tags (kommagetrennt)': 'Tags (comma-separated)',
    'Wissen durchsuchen…': 'Search knowledge…',
    'Alle Typen': 'All types',
    'Entscheidung': 'Decision',
    'Lade Knowledge Universe…': 'Loading Knowledge Universe…',
    '🧩 Knowledge Decision Engine': '🧩 Knowledge Decision Engine',
    'Frage / Entscheidungsbedarf': 'Question / decision need',
    'Modul-Kontext': 'Module context',
    'Kein Modul': 'No module',
    'Zinsbuchung': 'Interest posting',
    'Lohnbuchung': 'Payroll posting',
    'SAP allgemein': 'SAP general',
    '🧠 Entscheidung anfragen': '🧠 Request decision',
    'Alle Module': 'All modules',
    'Lade Entscheidungs-History…': 'Loading decision history…',
    'Alle Systeme': 'All systems',
    'Lade 10W-Auditeinträge…': 'Loading 10W audit entries…',
    'Wissenseintrag': 'Knowledge entry',

    /* ── Voice ──────────────────────────────────────── */
    'Esra – Finance-Assistentin': 'Esra – Finance Assistant',
    'Esra hört zu…': 'Esra is listening…',
    'Bitte sprechen...': 'Please speak...',
    'Finance-Assistentin': 'Finance Assistant',
    'Sprachsteuerung': 'Voice control',
    'SCHNELLBEFEHLE': 'QUICK COMMANDS',
    'ABFRAGEN': 'QUERIES',
    'NAVIGATION': 'NAVIGATION',
    '📋 Letzte Buchungen': '📋 Recent postings',
    '📅 Nächste Fälligkeit': '📅 Next due date',
    '💰 Zinsstatus': '💰 Interest status',
    '📄 Rechnungen': '📄 Invoices',
    '⏰ Zeitpläne': '⏰ Schedules',
    '📈 Zinsen öffnen': '📈 Open interest',
    '🧾 Rechnungen öffnen': '🧾 Open invoices',
    '🗃 Kundenstamm': '🗃 Customer master',
    '⚙ ZTERM ändern': '⚙ Change ZTERM',
    '❓ Hilfe': '❓ Help',
    'Modus:': 'Mode:',
    'Stimme:': 'Voice:',
    'WS:': 'WS:',
    'Senden ›': 'Send ›',
    'Verbinde mit Voice Server…': 'Connecting to voice server…',
    'ℹ Browser-Modus': 'ℹ Browser mode',
    'KI-Chat über Bridge aktiv': 'AI chat via Bridge active',
    'Sprache via Web Speech API': 'Voice via Web Speech API',
    '⚠ Bridge (8765) und Voice Server (8766) nicht erreichbar — nur Offline-Modus verfügbar.': '⚠ Bridge (8765) and Voice Server (8766) not reachable — only offline mode available.',

    /* ── Stammdaten ─────────────────────────────────── */
    'YCONN – SAP Stammdaten': 'YCONN – SAP Master Data',
    'SAP Stammdaten Kategorien': 'SAP Master Data Categories',
    'Debitoren': 'Customers (AR)',
    'Kreditoren': 'Vendors (AP)',
    'Sachkonten': 'G/L Accounts',
    'Kostenstellen': 'Cost Centers',
    'Intercompany-Stammdaten': 'Intercompany Master Data',
    'Profit Center': 'Profit Center',
    '⚙ In Vorbereitung': '⚙ In preparation',
    '○ Geplant': '○ Planned',
    'IC-Darlehen Kontenrahmen': 'IC Loan Chart of Accounts',
    'Sachkonto-Zuordnungen': 'G/L account assignments',
    'Buchungsseite': 'Posting side',
    'Darlehensgeber (DG)': 'Lender (DG)',
    'Darlehensnehmer (DN)': 'Borrower (DN)',
    'Zinsertrag IC-Darlehen': 'Interest income IC loan',
    'Zinsaufwand IC-Darlehen': 'Interest expense IC loan',
    'Buchungskreise': 'Company codes',
    'Aktive Buchungskreise': 'Active company codes',
    'Code': 'Code',
    'Filter': 'Filter',
    'Verwendung': 'Usage',
    'Modul': 'Module',

    /* ── DB Admin ───────────────────────────────────── */
    'YCONN — 3W Smart Database': 'YCONN — 3W Smart Database',
    '📊 Übersicht': '📊 Overview',
    '📋 Buchungs-Audit (WHO/WHAT/WHY)': '📋 Posting Audit (WHO/WHAT/WHY)',
    '📚 Wissensbasis': '📚 Knowledge Base',
    '⚖️ App-Regeln': '⚖️ App Rules',
    '💡 Verbesserungsvorschläge': '💡 Improvement suggestions',
    '🔍 Lernmuster': '🔍 Learning patterns',
    'Schichtenübersicht': 'Layer overview',
    'Architektur': 'Architecture',
    'WHO did WHAT and WHY — vollständiger Buchungs-Audit-Trail': 'WHO did WHAT and WHY — complete posting audit trail',
    'Strukturiertes Domänenwissen: BAPI-Muster, Fehlerlösungen, Regeln': 'Structured domain knowledge: BAPI patterns, error solutions, rules',
    'Automatisch erkannte Buchungsmuster und Statistiken': 'Automatically detected posting patterns and statistics',
    'Verbesserungsvorschläge — niemals automatisch umgesetzt': 'Improvement suggestions — never applied automatically',
    'App-Regeln persistent in DB — Single Source of Truth': 'App rules persistent in DB — Single Source of Truth',
    'Alle Module': 'All modules',
    'Periode z.B. 06/2026': 'Period e.g. 06/2026',
    '↻ Aktualisieren': '↻ Refresh',
    'Wann': 'When',
    'WER': 'WHO',
    'WAS': 'WHAT',
    'WARUM': 'WHY',
    'Objekt': 'Object',
    'Kategorie': 'Category',
    'Schlüssel': 'Key',
    'Vertrauen': 'Confidence',
    'Regel-ID': 'Rule ID',
    'Priorität': 'Priority',
    '5 – Kritisch': '5 – Critical',
    '4 – Hoch': '4 – High',
    '3 – Mittel': '3 – Medium',
    '2 – Niedrig': '2 – Low',
    '1 – Info': '1 – Info',
    'DB-Schema': 'DB schema',
    'Workflow': 'Workflow',
    'Benutzeroberfläche': 'User interface',
    'Datenqualität': 'Data quality',
    'Kurze Beschreibung des Vorschlags': 'Brief description of the suggestion',
    'Detaillierte Beschreibung und Begründung': 'Detailed description and rationale',
    'Einreichen': 'Submit',
    'Eingereicht': 'Submitted',
    'Akzeptiert': 'Accepted',
    'Abgelehnt': 'Rejected',
    'Buchungsfrequenz': 'Posting frequency',
    'Betragsabweichung': 'Amount deviation',
    'Fehlerquote': 'Error rate',

    /* ── Kontrollzentrum ────────────────────────────── */
    'YCONN — 3W Kontrollzentrum': 'YCONN — 3W Control Center',
    '⬡ 3W Kontrollzentrum': '⬡ 3W Control Center',
    'Bereit — Auto-Refresh alle 30s': 'Ready — Auto-refresh every 30s',
    'Zuletzt aktualisiert:': 'Last updated:',
    'Core-Datensätze': 'Core records',
    '3W Audit-Einträge': '3W audit entries',
    'Wissensbasis': 'Knowledge base',
    'Erkannte Muster': 'Detected patterns',
    'Vorschläge': 'Suggestions',
    'Governance Layer 6': 'Governance Layer 6',
    'Schichtenarchitektur': 'Layer architecture',
    'Details →': 'Details →',
    'System-Health': 'System health',
    '↻ Prüfen': '↻ Check',
    'Live Buchungs-Audit': 'Live posting audit',
    'Schnell-Aktionen': 'Quick actions',
    '📝 Wissen eintragen': '📝 Add knowledge',
    '💡 Vorschlag einreichen': '💡 Submit suggestion',
    '🔍 Audit-Eintrag': '🔍 Audit entry',
    '📡 API Explorer': '📡 API Explorer',
    'DB-Verteilung': 'DB distribution',
    'Offene Vorschläge': 'Open suggestions',
    '📝 Neuer Wissenseintrag': '📝 New knowledge entry',
    'Offen': 'Open',
    'Akzeptiert': 'Accepted',
    'Erledigt': 'Done',

    /* ── Page Titles ─────────────────────────────────── */
    'Cockpit v2': 'Cockpit v2',
    'Cockpit v1': 'Cockpit v1',
    'API Docs': 'API Docs',
    '3W-Kontrollzentrum': '3W Control Center',
    '3W-Details': '3W Details',
    'Bridge': 'Bridge',
  };

  /* ── Build reverse map EN → DE ───────────────────── */
  const EN_DE = {};
  Object.entries(DE_EN).forEach(([de, en]) => { if (!EN_DE[en]) EN_DE[en] = de; });

  /* ── T() translation function ────────────────────── */
  /**
   * Returns text in the current language.
   * Pass the German string; gets EN equivalent when lang=en.
   * @param {string} de - German source text
   * @returns {string}
   */
  window.T = function (de) {
    if (getLang() === 'de') return de;
    return DE_EN[de] !== undefined ? DE_EN[de] : de;
  };

  /* ── translate a single text node ───────────────────*/
  function translateNode(node, map) {
    const orig = node.nodeValue;
    if (!orig) return;
    const trimmed = orig.trim();
    if (!trimmed) return;
    const translated = map[trimmed];
    if (translated !== undefined && translated !== trimmed) {
      node.nodeValue = orig.replace(trimmed, translated);
    }
  }

  /* ── applyI18n(root) ─────────────────────────────── */
  /**
   * Walks DOM under root and translates text nodes + attributes.
   * Call after dynamic HTML insertion to translate new content.
   * @param {Element} [root=document.body]
   */
  window.applyI18n = function (root) {
    root = root || document.body;
    if (!root) return;

    const lang = getLang();
    const map = lang === 'en' ? DE_EN : EN_DE;

    /* text nodes */
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        const p = n.parentElement;
        /* skip script, style, code blocks */
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CODE' || tag === 'PRE') {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    let node;
    while ((node = walker.nextNode())) {
      translateNode(node, map);
    }

    /* placeholder attributes */
    root.querySelectorAll && root.querySelectorAll('[placeholder]').forEach(function (el) {
      const v = el.getAttribute('placeholder');
      const t = map[v];
      if (t !== undefined) el.setAttribute('placeholder', t);
    });

    /* title attributes */
    root.querySelectorAll && root.querySelectorAll('[title]').forEach(function (el) {
      const v = el.getAttribute('title');
      const t = map[v];
      if (t !== undefined) el.setAttribute('title', t);
    });

    /* <title> tag */
    if (root === document.body || root === document.documentElement) {
      const titleEl = document.querySelector('title');
      if (titleEl) {
        const v = titleEl.textContent.trim();
        const t = map[v];
        if (t !== undefined) titleEl.textContent = t;
      }
    }
  };

  /* ── MutationObserver – auto-translate dynamic DOM ── */
  let _observing = false;
  function startObserver() {
    if (_observing || typeof MutationObserver === 'undefined') return;
    _observing = true;
    const obs = new MutationObserver(function (mutations) {
      if (getLang() !== 'en') return; /* only translate when EN is active */
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (n) {
          if (n.nodeType === 1) {          /* ELEMENT_NODE */
            applyI18n(n);
          } else if (n.nodeType === 3) {   /* TEXT_NODE */
            translateNode(n, DE_EN);
          }
        });
      });
    });
    obs.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  /* ── Language toggle button ──────────────────────── */
  function buildToggleBtn() {
    const btn = document.createElement('button');
    btn.id = 'yconn-lang-btn';
    btn.title = 'Toggle language / Sprache wechseln';
    btn.onclick = function () { setLang(getLang() === 'en' ? 'de' : 'en'); };
    stylizeBtn(btn);
    return btn;
  }

  function stylizeBtn(btn) {
    const lang = getLang();
    btn.textContent = lang === 'en' ? '🇩🇪 DE' : '🇬🇧 EN';
    btn.style.cssText = [
      'position:fixed',
      'bottom:18px',
      'left:18px',
      'z-index:99999',
      'background:rgba(22,27,34,.95)',
      'color:#e6edf3',
      'border:1px solid #444c56',
      'border-radius:999px',
      'padding:5px 14px',
      'font-size:12px',
      'font-weight:700',
      'cursor:pointer',
      'letter-spacing:.4px',
      'box-shadow:0 2px 12px rgba(0,0,0,.45)',
      'transition:background .15s,border-color .15s',
    ].join(';');
  }

  function updateToggleBtn() {
    const btn = document.getElementById('yconn-lang-btn');
    if (btn) stylizeBtn(btn);
  }

  /* ── Init on DOM ready ───────────────────────────── */
  function init() {
    document.documentElement.lang = getLang();
    /* inject toggle button */
    if (!document.getElementById('yconn-lang-btn')) {
      document.body.appendChild(buildToggleBtn());
    }
    /* translate static content if EN */
    if (getLang() === 'en') {
      applyI18n();
    }
    /* watch for dynamic DOM changes */
    startObserver();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* ── Public API ─────────────────────────────────────*/
  window.toggleLang = function () { setLang(getLang() === 'en' ? 'de' : 'en'); };
  window.YCONN_I18N = { getLang: getLang, setLang: setLang, dict: DE_EN };

})();
