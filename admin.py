import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import lese_buchungen_komplett, speichere_buchungen
from generator_utils import generiere_ticketcodes

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/admin_login')
def admin_login():
    return render_template('admin/admin_login.html')

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'passwort123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return "Login fehlgeschlagen", 401

    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    buchungen = lese_buchungen_komplett()
    return render_template('admin/admin_dashboard.html', buchungen=buchungen)



@admin_bp.route('/status_update', methods=['POST'])
def status_update():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    buchung_id = int(request.form['buchung_id'])
    neuer_status = request.form['status']

    buchungen = lese_buchungen_komplett()

    if 0 <= buchung_id < len(buchungen):
        buchungen[buchung_id][12] = neuer_status  # Status

        # Status → bezahlt → Eintrag erzeugen
        if neuer_status == 'bezahlt':
            buchung = buchungen[buchung_id]

            bestehende_codes = set()
            try:
                with open('data/ticketgenerator.csv', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)
                    for row in reader:
                        if len(row) >= 6 and row[5].strip():
                            bestehende_codes.update(row[5].split(';'))
            except FileNotFoundError:
                pass

            anzahl = int(buchung[10]) if buchung[10].isdigit() else 0
            codes = generiere_ticketcodes(anzahl, bestehende_codes)
            codes_str = ';'.join(codes)

            neue_zeile = [
                buchung[0], buchung[1], buchung[2], buchung[8],
                buchung[10], codes_str, 'nein', 'nein'
            ]

            with open('data/ticketgenerator.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(neue_zeile)

        # Status → offen → Eintrag entfernen
        elif neuer_status == 'offen':
            try:
                with open('data/ticketgenerator.csv', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    zeilen = [header]
                    for row in reader:
                        if len(row) < 6:
                            continue  # Zeile überspringen, wenn sie zu kurz ist

                        if not (
                            row[0] == buchungen[buchung_id][0] and
                            row[1] == buchungen[buchung_id][1] and
                            row[2] == buchungen[buchung_id][2] and
                            row[3] == buchungen[buchung_id][8]
                        ):
                            zeilen.append(row)

                with open('data/ticketgenerator.csv', mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(zeilen)
            except FileNotFoundError:
                pass

    speichere_buchungen(buchungen)
    return redirect(url_for('admin.admin_dashboard'))
    

@admin_bp.route('/delete_buchung', methods=['POST'])
def delete_buchung():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    buchung_id = int(request.form['buchung_id'])
    buchungen = lese_buchungen_komplett()

    if 0 <= buchung_id < len(buchungen):
        buchungen.pop(buchung_id)  # Eintrag löschen

    speichere_buchungen(buchungen)

    return redirect(url_for('admin.admin_dashboard'))

from flask import send_file
import io

@admin_bp.route('/export_buchungen')
def export_buchungen():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    buchungen = lese_buchungen_komplett()

    # CSV in Speicher schreiben (nicht auf Festplatte)
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Kopfzeile schreiben
    writer.writerow(['Buchungstyp', 'Vorname', 'Nachname', 'PLZ', 'Ort', 'Straße', 'Hausnummer', 'Telefon', 'E-Mail', 'Tischnummer', 'Anzahl Tickets', 'Status', 'Zeitstempel'])
    
    # Alle Buchungen schreiben
    writer.writerows(buchungen)

    output.seek(0)



    # Datei als Download zurückgeben
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='buchungen_export.csv'
    )
