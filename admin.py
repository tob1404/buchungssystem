import csv
import io

from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import lese_buchungen_komplett, speichere_buchungen

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
        buchungen[buchung_id][11] = neuer_status  # ACHTUNG: Index 11 (nicht mehr 7!)

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
    writer.writerow(['Buchungstyp', 'Vorname', 'Nachname', 'PLZ', 'Ort', 'Straße', 'Hausnummer', 'Telefon', 'E-Mail', 'Tischnummer', 'Anzahl Tickets', 'Status'])
    
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
