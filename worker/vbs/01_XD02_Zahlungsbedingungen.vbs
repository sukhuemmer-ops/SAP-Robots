' ============================================================
' SAP GUI Scripting Robot
' Projekt : Zahlungsbedingungen Korrektur
' BK      : 0439 India
' Trans.  : XD02 (Kundenstamm Vertrieb)
' Erstellt: 2026-06-29
' ============================================================

Option Explicit

' ============================================================
' KONFIGURATION – bitte vor erstem Lauf anpassen
' ============================================================
Const CFG_EXCEL_FILE  = "C:\WF\sap-robots\worker\vbs\Customer Payment Terms -0439 India.xlsx"
Const CFG_LOG_FILE    = "C:\WF\sap-robots\worker\vbs\Log_XD02.txt"
Const CFG_VERKAUFSORG = "0439"   ' Verkaufsorganisation
Const CFG_VTWEG       = "10"     ' Vertriebsweg – anpassen
Const CFG_SPART       = "00"     ' Sparte – anpassen
Const CFG_TESTMODUS   = True     ' True = Dry-Run (kein Sichern), False = echte Änderung
' ============================================================

Dim fso, logFile
Dim SapGuiAuto, application, connection, session
Dim oExcel, oWB, oWS
Dim successCount, errorCount, skipCount, i
Dim compCode, custNum, custName, currentTerm, matchStatus, newTerm

' --- Log initialisieren ---
Set fso = CreateObject("Scripting.FileSystemObject")
Set logFile = fso.OpenTextFile(CFG_LOG_FILE, 8, True)
LogWrite "========================================================"
LogWrite "SAP Robot: XD02 Zahlungsbedingungen Korrektur"
LogWrite "Start: " & Now()
If CFG_TESTMODUS Then LogWrite "*** TESTMODUS AKTIV – keine Änderungen werden gesichert ***"
LogWrite "========================================================"

' --- SAP GUI Verbindung prüfen ---
On Error Resume Next
Set SapGuiAuto = GetObject("SAPGUI")
If Err.Number <> 0 Then
    MsgBox "SAP GUI ist nicht gestartet oder Scripting ist deaktiviert." & vbCrLf & vbCrLf & _
           "Bitte prüfen:" & vbCrLf & _
           "  SAP GUI → Optionen → Barrierefreiheit & Scripting → Scripting aktivieren", _
           vbCritical, "SAP Robot – XD02"
    LogWrite "ABBRUCH: SAP GUI nicht verfügbar."
    logFile.Close : WScript.Quit 1
End If
On Error GoTo 0

Set application = SapGuiAuto.GetScriptingEngine
If application.Children.Count = 0 Then
    MsgBox "Keine aktive SAP-Verbindung. Bitte zuerst anmelden.", vbCritical, "SAP Robot – XD02"
    WScript.Quit 1
End If
Set connection = application.Children(0)
Set session    = connection.Children(0)

LogWrite "SAP-Verbindung: OK | System=" & connection.Description

' --- Excel öffnen ---
If Not fso.FileExists(CFG_EXCEL_FILE) Then
    MsgBox "Excel-Datei nicht gefunden:" & vbCrLf & CFG_EXCEL_FILE, vbCritical, "SAP Robot – XD02"
    WScript.Quit 1
End If

Set oExcel = CreateObject("Excel.Application")
oExcel.Visible = False
oExcel.DisplayAlerts = False
Set oWB = oExcel.Workbooks.Open(CFG_EXCEL_FILE)
Set oWS = oWB.Sheets(1)   ' Sheet "KNVV--BSEG"

successCount = 0 : errorCount = 0 : skipCount = 0

' --- Zeilen verarbeiten (ab Zeile 2, Zeile 1 = Header) ---
i = 2
Do While Trim(CStr(oWS.Cells(i, 1).Value)) <> ""
    compCode    = Trim(CStr(oWS.Cells(i, 1).Value))
    custNum     = Trim(CStr(oWS.Cells(i, 2).Value))
    custName    = Trim(CStr(oWS.Cells(i, 3).Value))
    currentTerm = Trim(CStr(oWS.Cells(i, 4).Value))
    matchStatus = Trim(CStr(oWS.Cells(i, 11).Value))
    newTerm     = Trim(CStr(oWS.Cells(i, 12).Value))

    If matchStatus = "Not Matched" And newTerm <> "" And newTerm <> "False" Then
        LogWrite ""
        LogWrite ">>> Kunde " & custNum & " – " & custName
        LogWrite "    Alt: " & currentTerm & "  Neu: " & newTerm & "  BK: " & compCode
        Call XD02_AendereZTERM(custNum, compCode, newTerm)
    Else
        skipCount = skipCount + 1
        LogWrite "SKIP | " & custNum & " – " & custName & " (" & matchStatus & ")"
    End If
    i = i + 1
Loop

' --- Aufräumen ---
oWB.Close False
oExcel.Quit
Set oExcel = Nothing

' --- Abschluss ---
LogWrite ""
LogWrite "========================================================"
LogWrite "Ergebnis: Erfolgreich=" & successCount & "  Fehler=" & errorCount & "  Übersprungen=" & skipCount
LogWrite "Ende: " & Now()
LogWrite "========================================================"
logFile.Close

MsgBox "SAP Robot abgeschlossen." & vbCrLf & vbCrLf & _
       "✅ Erfolgreich : " & successCount & vbCrLf & _
       "❌ Fehler      : " & errorCount & vbCrLf & _
       "⏭  Übersprungen: " & skipCount & vbCrLf & vbCrLf & _
       "Log: " & CFG_LOG_FILE, vbInformation, "SAP Robot – XD02"


' ============================================================
' SUBROUTINE: XD02 – Zahlungsbedingung (ZTERM) im Kundenstamm ändern
' ============================================================
Sub XD02_AendereZTERM(custNum, compCode, newTerm)
    On Error Resume Next

    ' Transaktion XD02 aufrufen
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nXD02"
    session.findById("wnd[0]").sendVKey 0
    WScript.Sleep 1500

    If Err.Number <> 0 Then
        LogWrite "  FEHLER: Navigation XD02 – " & Err.Description
        errorCount = errorCount + 1 : Err.Clear : Exit Sub
    End If

    ' Einstiegsmaske: Kundennummer, Buchungskreis, Verkaufsbereich
    SafeSet session, "wnd[0]/usr/ctxtRF02D-KUNNR", custNum
    SafeSet session, "wnd[0]/usr/ctxtRF02D-BUKRS", compCode
    SafeSet session, "wnd[0]/usr/ctxtRF02D-VKORG", CFG_VERKAUFSORG
    SafeSet session, "wnd[0]/usr/ctxtRF02D-VTWEG", CFG_VTWEG
    SafeSet session, "wnd[0]/usr/ctxtRF02D-SPART", CFG_SPART

    session.findById("wnd[0]").sendVKey 0   ' Enter
    WScript.Sleep 1500

    If Err.Number <> 0 Then
        LogWrite "  FEHLER: Einstiegsmaske – " & Err.Description
        errorCount = errorCount + 1 : Err.Clear : Exit Sub
    End If

    ' Evtl. Popup (Sichtenauswahl o.ä.) bestätigen
    Call AkzeptierePopup()

    ' Tab "Faktura" (Vertriebsbereich-Daten → Faktura) ansteuern
    ' Tab-ID T\03 = Faktura in SAPMF02D (SAP-Standard)
    Err.Clear
    session.findById("wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\03").select
    WScript.Sleep 800

    If Err.Number <> 0 Then
        Err.Clear
        ' Fallback: Menü Springen → Vertriebsbereich → Faktura
        session.findById("wnd[0]/mbar/menu[2]/menu[1]/menu[2]").select
        WScript.Sleep 800
        If Err.Number <> 0 Then
            LogWrite "  FEHLER: Faktura-Tab nicht gefunden. GUI-ID im Skript anpassen."
            LogWrite "  Tipp  : SAP GUI Recorder starten (Extras → Skript aufzeichnen)"
            errorCount = errorCount + 1
            session.findById("wnd[0]").sendVKey 12   ' F12 = Abbrechen
            Err.Clear : Exit Sub
        End If
    End If

    ' ZTERM-Feld suchen und setzen
    Dim zTermCtrl
    Err.Clear

    ' Pfad 1 – Standard SAPMF02D Tab Faktura
    Set zTermCtrl = session.findById( _
        "wnd[0]/usr/tabsTAXI_TABSTRIP_HEAD/tabpT\03" & _
        "/ssubSUBSCREEN_BODY:SAPMF02D:7325/ctxtKNVV-ZTERM")

    If Err.Number <> 0 Or zTermCtrl Is Nothing Then
        Err.Clear
        ' Pfad 2 – ohne Tabstreifen-Wrapper
        Set zTermCtrl = session.findById( _
            "wnd[0]/usr/subSUBSCREEN_BODY:SAPMF02D:7325/ctxtKNVV-ZTERM")
    End If

    If Err.Number <> 0 Or zTermCtrl Is Nothing Then
        LogWrite "  FEHLER: ZTERM-Feld (KNVV-ZTERM) nicht gefunden."
        LogWrite "  Bitte mit SAP GUI Recorder die korrekte Element-ID ermitteln."
        errorCount = errorCount + 1
        session.findById("wnd[0]").sendVKey 12
        Err.Clear : Exit Sub
    End If

    Dim altWert : altWert = zTermCtrl.text
    zTermCtrl.text = newTerm

    ' Testmodus: nur prüfen, nicht sichern
    If CFG_TESTMODUS Then
        LogWrite "  TEST OK: ZTERM-Feld gefunden | " & altWert & " → " & newTerm & " (nicht gesichert)"
        session.findById("wnd[0]").sendVKey 12   ' Abbrechen
        successCount = successCount + 1
    Else
        ' Sichern (Ctrl+S = VKey 11)
        session.findById("wnd[0]").sendVKey 11
        WScript.Sleep 1200

        Dim statusMsg : statusMsg = ""
        On Error Resume Next
        statusMsg = session.findById("wnd[0]/sbar").text
        On Error GoTo 0

        Dim statusLower : statusLower = LCase(statusMsg)
        If InStr(statusLower, "gesichert") > 0 Or InStr(statusLower, "saved") > 0 Or _
           InStr(statusLower, "geändert")  > 0 Or InStr(statusLower, "changed") > 0 Then
            LogWrite "  OK: " & statusMsg
            successCount = successCount + 1
        ElseIf InStr(statusLower, "fehler") > 0 Or InStr(statusLower, "error") > 0 Then
            LogWrite "  FEHLER: SAP-Meldung: " & statusMsg
            errorCount = errorCount + 1
            session.findById("wnd[0]").sendVKey 12
        Else
            LogWrite "  WARNUNG: SAP-Meldung: " & statusMsg & " – bitte manuell prüfen"
            successCount = successCount + 1
        End If
    End If

    On Error GoTo 0
    WScript.Sleep 400
End Sub


' ============================================================
' HILFSFUNKTIONEN
' ============================================================

Sub SafeSet(session, path, value)
    On Error Resume Next
    session.findById(path).text = value
    Err.Clear
    On Error GoTo 0
End Sub

Sub AkzeptierePopup()
    ' App-Regel G-8: Mehrfachanmeldungs-Dialog → Option 2 wählen
    ' Exakt nach dem funktionierenden Muster:
    '   radMULTI_LOGON_OPT2.select
    '   radMULTI_LOGON_OPT2.setFocus
    '   btn[0].press  (1. Mal)
    '   btn[0].press  (2. Mal – SAP-Eigenheit)
    On Error Resume Next
    Dim popup : Set popup = session.findById("wnd[1]")
    If popup Is Nothing Or Err.Number <> 0 Then
        Err.Clear : On Error GoTo 0 : Exit Sub
    End If
    Err.Clear

    ' ── Prüfen ob Mehrfachanmeldungs-Dialog (radMULTI_LOGON_OPT2 vorhanden?) ──
    Dim radio2
    Set radio2 = session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2")
    Dim isMultiLogon : isMultiLogon = (Err.Number = 0 And Not radio2 Is Nothing)
    Err.Clear

    If isMultiLogon Then
        LogWrite "  INFO: Mehrfachanmeldungs-Dialog – wähle Option 2 (ohne andere Sessions zu beenden)"

        ' 1. Radio-Button selektieren UND Fokus setzen (beide Schritte erforderlich)
        radio2.select
        Err.Clear
        radio2.setFocus
        Err.Clear
        WScript.Sleep 300

        ' 2. OK-Button ZWEIMAL drücken (SAP-Eigenheit bei diesem Dialog)
        Dim okBtn
        Set okBtn = session.findById("wnd[1]/tbar[0]/btn[0]")
        If Err.Number = 0 And Not okBtn Is Nothing Then
            okBtn.press
            WScript.Sleep 300
            okBtn.press   ' zweiter Druck – wie im getesteten Muster
            Err.Clear
        Else
            Err.Clear
            popup.sendVKey 0
        End If
    Else
        ' Standard-Popup (Sichtenauswahl, Hinweis etc.) → Enter
        popup.sendVKey 0
    End If

    WScript.Sleep 600
    Err.Clear
    On Error GoTo 0
End Sub

Sub LogWrite(text)
    logFile.WriteLine text
End Sub
