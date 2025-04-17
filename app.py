from flask import Flask, render_template, request, redirect, url_for, session
import csv
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

    # Altersbestätigung prüfen
    if not request.form.get('altersbestaetigung'):
        return redirect(url_for('buchen', art=art, fehler="Bitte bestätigen Sie, dass Sie mindestens 16 Jahre alt sind."))

    tischnummer = request.form.get('tischnummer')
    anzahl = request.form.get('anzahl')

    tische_belegt, freie_einzeltickets = lade_buchungen()

    # Verfügbarkeitsprüfung
    if art == 'tisch':
        if not tischnummer:
            return redirect(url_for('buchen', art=art, fehler="Bitte wählen Sie einen Tisch aus."))
        if int(tischnummer) in tische_belegt:
            return redirect(url_for('buchen', art=art, fehler="Dieser Tisch ist bereits gebucht."))
    elif art == 'einzelticket':
        if not anzahl or int(anzahl) < 1:
            return redirect(url_for('buchen', art=art, fehler="Bitte geben Sie eine gültige Anzahl an Tickets ein."))
        if int(anzahl) > freie_einzeltickets:
            return redirect(url_for('buchen', art=art, fehler=f"Nur noch {freie_einzeltickets} Tickets verfügbar."))

    # CSV-Daten speichern
    with open('data/buchungen.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([art, vorname, nachname, plz, ort, strasse, hausnummer, telefon, email, tischnummer, anzahl, 'offen'])

    return render_template('buchung/bestaetigung.html', art=art, vorname=vorname, nachname=nachname, tischnummer=tischnummer, anzahl=anzahl)



if __name__ == '__main__':
    app.run(debug=True)
