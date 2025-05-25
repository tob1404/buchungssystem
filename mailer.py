import smtplib
from email.mime.text import MIMEText  # ⬅️ Das war der fehlende Import

def sende_bestaetigungsmail(empfaenger, name, buchungsart, anzahl, tischnummern, betrag, tischanzahl=0):
    absender = "dirndlparty.mveningen@gmail.com"
    app_passwort = "xmel rfni idel jsfs"  # 16-stelliger App-Code

    buchungsart_anzeige = "Tischpaket" if buchungsart == "tisch" else "Einzelticket"

    if buchungsart == "tisch":
        tisch_info = f"- Anzahl Tische: {tischanzahl}\n- Tisch-Nr.: {tischnummern}"
    else:
        tisch_info = "- Tisch-Nr.: –"

    text = f"""
Hallo {name},

vielen Dank für Ihre Reservierung für die Dirndlparty 2025.

Buchungsdetails:
- Buchungsart: {buchungsart_anzeige}
- Tickets: {anzahl}
{tisch_info}
- Betrag: {betrag} €

Sie erhalten die Tickets nach Zahlungseingang.

Musikalische Grüße
Musikverein Eningen
"""

    msg = MIMEText(text)
    msg['Subject'] = "Reservierungsbestätigung – Dirndlparty"
    msg['From'] = absender
    msg['To'] = empfaenger

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(absender, app_passwort)
            server.send_message(msg)
        print("✅ Bestätigungsmail erfolgreich gesendet.")
        return True
    except Exception as e:
        print("❌ Fehler beim Mailversand:", e)
        return False
