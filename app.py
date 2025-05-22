from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from utils import lade_buchungen
from admin import admin_bp

app = Flask(__name__)
app.secret_key = 'dein_geheimes_passwort'

# Admin-Blueprint registrieren
app.register_blueprint(admin_bp)

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
    telefon = request.form.get('telefon')  # optional
    email = request.form['email']
    kommentar = request.form.get('kommentar', '')

    # Alters- und Datenschutzbestätigung prüfen
    if not request.form.get('altersbestaetigung') or not request.form.get('datenschutz'):
        return redirect(url_for('buchen', art=art, fehler="Bitte bestätigen Sie das Mindestalter und die Datenschutzerklärung."))

    tische_belegt, freie_einzeltickets = lade_buchungen()

    tischnummer_raw = request.form.get('tischnummer', '')
    tischnummern = [int(n.strip()) for n in tischnummer_raw.split(',') if n.strip().isdigit()]

    if art == 'tisch':
        if not tischnummern:
            return redirect(url_for('buchen', art=art, fehler="Bitte wählen Sie mindestens einen Tisch aus."))
        for tisch in tischnummern:
            if tisch in tische_belegt:
                return redirect(url_for('buchen', art=art, fehler=f"Tisch {tisch} ist bereits gebucht."))
        anzahl = len(tischnummern) * 10  # 10 Plätze pro Tisch
    else:
        anzahl_raw = request.form.get('anzahl')
        if not anzahl_raw or int(anzahl_raw) < 1:
            return redirect(url_for('buchen', art=art, fehler="Bitte geben Sie eine gültige Anzahl an Tickets ein."))
        anzahl = int(anzahl_raw)
        if anzahl > freie_einzeltickets:
            return redirect(url_for('buchen', art=art, fehler=f"Nur noch {freie_einzeltickets} Tickets verfügbar."))

    # CSV-Daten speichern
    with open('data/buchungen.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            art,
            vorname,
            nachname,
            plz,
            ort,
            strasse,
            hausnummer,
            telefon,
            email,
            ",".join(map(str, tischnummern)) if art == 'tisch' else '',
            anzahl,
            kommentar,
            'offen'
        ])

    return render_template('buchung/bestaetigung.html',
                           art=art,
                           vorname=vorname,
                           nachname=nachname,
                           tischnummer=", ".join(map(str, tischnummern)) if art == 'tisch' else '',
                           anzahl=anzahl)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
