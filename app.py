from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from datetime import datetime
from utils import lade_buchungen
from admin import admin_bp
from mailer import sende_bestaetigungsmail
from ticketgenerator import ticket_bp





app = Flask(__name__)
app.secret_key = 'dein_geheimes_passwort'

# Admin-Blueprint registrieren
app.register_blueprint(admin_bp)
app.register_blueprint(ticket_bp)

@app.route('/')
def index():
    tische_belegt, _ = lade_buchungen()
    freie_tische = [tisch for tisch in range(1, 37) if tisch not in tische_belegt]
    return render_template('buchung/index.html', freie_tische=freie_tische)

@app.route('/buchen', methods=['GET'])
def buchen():
    buchungsart = request.args.get('art')
    tische_belegt, _ = lade_buchungen()
    return render_template('buchung/buchen.html', buchungsart=buchungsart, belegte_tische=tische_belegt)

@app.route('/absenden', methods=['POST'])
def absenden():
    art = request.form['art']
    vorname = request.form['vorname']
    nachname = request.form['nachname']
    plz = request.form['plz']
    ort = request.form['ort']
    strasse = request.form['strasse']
    hausnummer = request.form['hausnummer']
    telefon = request.form.get('telefon')
    email = request.form['email']
    kommentar = request.form.get('kommentar', '')

    if not request.form.get('altersbestaetigung') or not request.form.get('datenschutz'):
        return redirect(url_for('buchen', art=art, fehler="Bitte bestätigen Sie das Mindestalter und die Datenschutzerklärung."))

    # Neue Platzberechnung
    MAX_PLAETZE = 360
    tische_belegt, belegte_plaetze = lade_buchungen()
    freie_plaetze = MAX_PLAETZE - belegte_plaetze

    # Wenn nichts mehr frei ist → Abbruch
    if freie_plaetze <= 0:
        return render_template('buchung/ausgebucht.html')

    tischnummer_raw = request.form.get('tischnummer', '')
    tischnummern = [int(n.strip()) for n in tischnummer_raw.split(',') if n.strip().isdigit()]
    anzahl = request.form.get('anzahl')

    if art == 'tisch':
        if not tischnummern:
            return redirect(url_for('buchen', art=art, fehler="Bitte wählen Sie mindestens einen Tisch aus."))

        benoetigte_plaetze = len(tischnummern) * 10

        for t in tischnummern:
            if t in tische_belegt:
                return redirect(url_for('buchen', art=art, fehler=f"Tisch {t} ist bereits gebucht."))

        if benoetigte_plaetze > freie_plaetze:
            return render_template('buchung/ausgebucht.html')

        anzahl = str(benoetigte_plaetze)

    elif art == 'einzelticket':
        if not anzahl or not anzahl.isdigit() or int(anzahl) < 1:
            return redirect(url_for('buchen', art=art, fehler="Bitte geben Sie eine gültige Anzahl an Tickets ein."))

        if int(anzahl) > freie_plaetze:
            return render_template('buchung/ausgebucht.html')

    else:
        return redirect(url_for('index'))

    # Betrag & Zeitstempel berechnen
    betrag = 0
    tisch_anzahl = len(tischnummern) if art == 'tisch' else 0
    if art == 'einzelticket':
        betrag = int(anzahl) * 15
    elif art == 'tisch':
        betrag = tisch_anzahl * 150
    zeitstempel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # E-Mail senden
    tischnummer_str = ",".join(map(str, tischnummern)) if art == 'tisch' else ''
    mail_ok = sende_bestaetigungsmail(
        empfaenger=email,
        name=f"{vorname} {nachname}",
        buchungsart=art,
        anzahl=anzahl,
        tischnummern=tischnummer_str,
        betrag=betrag,
        tischanzahl=tisch_anzahl
    )

    # Status-Spalten korrekt setzen
    mail_status = "ja" if mail_ok else "nein"
    ticket_status = "nein"  # wird später manuell auf "ja" gesetzt

    # CSV speichern
    with open('data/buchungen.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            art, vorname, nachname, plz, ort, strasse, hausnummer, telefon,
            email, tischnummer_str, anzahl, kommentar, 'offen', betrag,
            zeitstempel, mail_status, ticket_status
        ])



    return render_template(
        'buchung/bestaetigung.html',
        art=art,
        vorname=vorname,
        nachname=nachname,
        tischnummer=",".join(map(str, tischnummern)) if art == 'tisch' else '',
        anzahl=anzahl
    )





if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
