' ============================================================
' SAP GUI Scripting Robot
' Projekt : Zahlungsbedingungen Korrektur
' BK      : 0439 India
' Trans.  : VK12 (Konditionsstamm – Zahlungsbedingung)
' Erstellt: 2026-06-29
' ============================================================

Option Explicit

' ============================================================
' KONFIGURATION
' ============================================================
Const CFG_EXCEL_FILE   = "C:\WF\sap-robots\worker\vbs\Customer Payment Terms -0439 India.xlsx"
Const CFG_LOG_FILE     = "C:\WF\sap-robots\worker\vbs\Log_VK12.txt"
Const CFG_KONDART      = "ZB00"   ' Konditionsart für Zahlungsbedingung – anpassen
Const CFG_VERKAUFSORG  = "0439"
Const CFG_VTWEG        = "10"
Const CFG_SPART        = "00"
Const CFG_TESTMODUS    = True     ' True = Dry-Run, False = echte Änderung
' ============================================================

Dim fso, logFile
Dim SapGuiAuto, application, connection, session
Dim oExcel, oWB, oWS
Dim successCount, errorCount, skipCount, i
Dim custNum, custName, matchStatus, newTerm

Set fso = CreateObject("Scripting.FileSystemObject")
Set logFile = fso.OpenTextFile(CFG_LOG_FILE, 8, True)
LogWrite "========================================================"
LogWrite "SAP Robot: VK12 Konditionsstamm Zahlungsbedingungen"
LogWrite "Start: " & Now()
If CFG_TESTMODUS Then LogWrite "*** TESTMODUS AKTIV ***"
LogWrite "========================================================"

On Error Resume Next
Set SapGuiAuto = GetObject("SAPGUI")
If Err.Number <> 0 Then
    MsgBox "SAP GUI nicht erreichbar oder Scripting deaktiviert.", vbCritical, "SAP Robot – VK12"
    logFile.Close : WScript.Quit 1
End If
On Error GoTo 0

Set application = SapGuiAuto.GetScriptingEngine
Set connection  = application.Children(0)
Set session     = connection.Children(0)

If Not fso.FileExists(CFG_EXCEL_FILE) Then
    MsgBox "Excel-Datei nicht gefunden:" & vbCrLf & CFG_EXCEL_FILE, vbCritical, "SAP Robot – VK12"
    WScript.Quit 1
End If

Set oExcel = CreateObject("Excel.Application")
oExcel.Visible = False
oExcel.DisplayAlerts = False
Set oWB = oExcel.Workbooks.Open(CFG_EXCEL_FILE)
Set oWS = oWB.Sheets(1)

successCount = 0 : errorCount = 0 : skipCount = 0

i = 2
Do While Trim(CStr(oWS.Cells(i, 1).Value)) <> ""
    custNum     = Trim(CStr(oWS.Cells(i, 2).Value))
    custName    = Trim(CStr(oWS.Cells(i, 3).Value))
    matchStatus = Trim(CStr(oWS.Cells(i, 11).Value))
    newTerm     = Trim(CStr(oWS.Cells(i, 12).Value))

    If matchStatus = "Not Matched" And newTerm <> "" And newTerm <> "False" Then
        LogWrite ""
        LogWrite ">>> VK12 Kunde " & custNum & " – " & custName & " → " & newTerm
        Call VK12_AendereKondition(custNum, newTerm)
    Else
        skipCount = skipCount + 1
    End If
    i = i + 1
Loop

oWB.Close False
oExcel.Quit
Set oExcel = Nothing

LogWrite ""
LogWrite "========================================================"
LogWrite "Ergebnis: Erfolgreich=" & successCount & "  Fehler=" & errorCount & "  Übersprungen=" & skipCount
LogWrite "Ende: " & Now()
LogWrite "========================================================"
logFile.Close

MsgBox "SAP Robot VK12 abgeschlossen." & vbCrLf & vbCrLf & _
       "✅ Erfolgreich : " & successCount & vbCrLf & _
       "❌ Fehler      : " & errorCount & vbCrLf & _
       "⏭  Übersprungen: " & skipCount & vbCrLf & vbCrLf & _
       "Log: " & CFG_LOG_FILE, vbInformation, "SAP Robot – VK12"


' ============================================================
' SUBROUTINE: VK12 – Konditionssatz Zahlungsbedingung ändern
' ============================================================
Sub VK12_AendereKondition(custNum, newTerm)
    On Error Resume Next

    ' VK12 aufrufen
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nVK12"
    session.findById("wnd[0]").sendVKey 0
    WScript.Sleep 1500

    If Err.Number <> 0 Then
        LogWrite "  FEHLER: Navigation VK12 – " & Err.Description
        errorCount = errorCount + 1 : Err.Clear : Exit Sub
    End If

    ' Konditionsart eingeben
    SafeSet session, "wnd[0]/usr/ctxtKOMG-KOZGF", CFG_KONDART
    session.findById("wnd[0]").sendVKey 0   ' Enter
    WScript.Sleep 1500

    If Err.Number <> 0 Then
        LogWrite "  FEHLER: Konditionsart-Eingabe – " & Err.Description
        errorCount = errorCount + 1 : Err.Clear : Exit Sub
    End If

    ' Schlüsselkombination: Verkaufsbereich + Kunde
    SafeSet session, "wnd[0]/usr/ctxtKOMG-VKORG", CFG_VERKAUFSORG
    SafeSet session, "wnd[0]/usr/ctxtKOMG-VTWEG", CFG_VTWEG
    SafeSet session, "wnd[0]/usr/ctxtKOMG-SPART", CFG_SPART
    SafeSet session, "wnd[0]/usr/ctxtKOMG-KUNNR", custNum

    session.findById("wnd[0]").sendVKey 0   ' Enter
    WScript.Sleep 1500

    Call AkzeptierePopup()

    If Err.Number <> 0 Then
        LogWrite "  FEHLER: Konditionssatz nicht gefunden oder Fehler – " & Err.Description
        LogWrite "  INFO  : Konditionssatz für Kunde " & custNum & " existiert möglicherweise nicht."
        errorCount = errorCount + 1 : Err.Clear : Exit Sub
    End If

    ' Konditionswert (ZTERM) in der Tabelle suchen und ändern
    ' Typischerweise in der ersten Zeile der Ergebnistabelle
    Dim zTermCtrl
    Err.Clear

    Set zTermCtrl = session.findById("wnd[0]/usr/tblSAPMV13ATCTRL_U_KO004/ctxtKOMP-ZTERM[0,0]")
    If Err.Number <> 0 Or zTermCtrl Is Nothing Then
        Err.Clear
        ' Fallback: andere Tabellenstruktur
        Set zTermCtrl = session.findById("wnd[0]/usr/tblSAPMV13AT_KOTAB/ctxtKOMP-ZTERM[0,0]")
    End If

    If Err.Number <> 0 Or zTermCtrl Is Nothing Then
        LogWrite "  FEHLER: ZTERM-Feld in VK12-Tabelle nicht gefunden."
        LogWrite "  Tipp  : GUI-Element-ID per SAP Recorder ermitteln."
        errorCount = errorCount + 1
        session.findById("wnd[0]").sendVKey 12
        Err.Clear : Exit Sub
    End If

    Dim altWert : altWert = zTermCtrl.text
    zTermCtrl.text = newTerm

    If CFG_TESTMODUS Then
        LogWrite "  TEST OK: " & altWert & " → " & newTerm & " (nicht gesichert)"
        session.findById("wnd[0]").sendVKey 12
        successCount = successCount + 1
    Else
        session.findById("wnd[0]").sendVKey 11   ' Sichern
        WScript.Sleep 1200

        Dim statusMsg : statusMsg = ""
        On Error Resume Next
        statusMsg = session.findById("wnd[0]/sbar").text
        On Error GoTo 0

        Dim sl : sl = LCase(statusMsg)
        If InStr(sl, "gesichert") > 0 Or InStr(sl, "saved") > 0 Then
            LogWrite "  OK: " & statusMsg
            successCount = successCount + 1
        ElseIf InStr(sl, "fehler") > 0 Or InStr(sl, "error") > 0 Then
            LogWrite "  FEHLER: " & statusMsg
            errorCount = errorCount + 1
            session.findById("wnd[0]").sendVKey 12
        Else
            LogWrite "  WARNUNG: " & statusMsg
            successCount = successCount + 1
        End If
    End If

    On Error GoTo 0
    WScript.Sleep 400
End Sub


Sub SafeSet(session, path, value)
    On Error Resume Next
    session.findById(path).text = value
    Err.Clear
    On Error GoTo 0
End Sub

Sub AkzeptierePopup()
    On Error Resume Next
    Dim popup : Set popup = session.findById("wnd[1]")
    If Not popup Is Nothing And Err.Number = 0 Then
        popup.sendVKey 0 : WScript.Sleep 500
    End If
    Err.Clear
    On Error GoTo 0
End Sub

Sub LogWrite(text)
    logFile.WriteLine text
End Sub
