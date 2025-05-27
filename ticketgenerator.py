from flask import Blueprint, render_template, request, send_file, redirect, url_for
from generator_utils import erstelle_ticketgenerator_csv
from generator_qr import generiere_qr_pdf
import csv
import os
import io


ticket_bp = Blueprint('ticket_bp', __name__, template_folder='templates')

@ticket_bp.route('/ticketgenerator')
def ticketgenerator():
    # 👇 CSV wird erzeugt, wenn sie noch nicht existiert
    if not os.path.exists('data/ticketgenerator.csv'):
        erstelle_ticketgenerator_csv()

    buchungen = []
    with open('data/ticketgenerator.csv', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) >= 6:
                buchungen.append(row)

    return render_template('admin/ticketgenerator.html', buchungen=buchungen)

@ticket_bp.route('/erzeuge_ticket/<int:buchung_id>', methods=['POST'])
def erzeuge_ticket(buchung_id):
    pfad = 'data/ticketgenerator.csv'
    zeilen = []

    with open(pfad, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        zeilen.append(header)
        for row in reader:
            zeilen.append(row)

    if 1 <= buchung_id < len(zeilen):  # 0 ist Header
        buchung = zeilen[buchung_id]
        
        

        buchungstyp = buchung[0]
        vorname = buchung[1]
        nachname = buchung[2]
        email = buchung[3]
        anzahl = buchung[4]
        ticketcodes = buchung[5].split(';') if buchung[5].strip() else []

        if not ticketcodes:
            print("⚠️ Keine Ticketcodes vorhanden.")
            return redirect(url_for('ticket_bp.ticketgenerator'))

        dateiname = generiere_qr_pdf(vorname, nachname, buchungstyp, ticketcodes)

        if dateiname:
            while len(buchung) < 8:
                buchung.append('')
            buchung[6] = "ja"  # PDF erstellt

            with open(pfad, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(zeilen)

            return send_file(dateiname, as_attachment=True)

    return redirect(url_for('ticket_bp.ticketgenerator'))

@ticket_bp.route('/ticketgedruckt/<int:buchung_id>', methods=['POST'])
def ticket_gedruckt(buchung_id):
    pfad = 'data/ticketgenerator.csv'
    zeilen = []

    with open(pfad, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        zeilen = list(reader)

    if 1 <= buchung_id < len(zeilen):
        zeilen[buchung_id][6] = 'ja'  # Spalte "PDF erstellt" auf „ja“

    with open(pfad, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(zeilen)

    return redirect(url_for('ticket_bp.ticketgenerator'))

@ticket_bp.route('/toggle_gedruckt/<int:buchung_id>', methods=['POST'])
def toggle_gedruckt(buchung_id):
    pfad = 'data/ticketgenerator.csv'
    zeilen = []

    with open(pfad, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        zeilen.append(header)
        for row in reader:
            # Immer auf 10 Spalten auffüllen
            while len(row) < 10:
                row.append('')
            zeilen.append(row)

    if 1 <= buchung_id < len(zeilen):
        status = zeilen[buchung_id][9].strip().lower() if len(zeilen[buchung_id]) > 9 else ""

        zeilen[buchung_id][9] = "gedruckt" if status != "gedruckt" else "noch nicht gedruckt"


    with open(pfad, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(zeilen)

    return redirect(url_for('ticket_bp.ticketgenerator'))

@ticket_bp.route('/ticketgenerator_export')
def ticketgenerator_export():
    pfad = 'data/ticketgenerator.csv'

    if not os.path.exists(pfad):
        return "Keine Ticketdaten vorhanden", 404

    with open(pfad, newline='', encoding='utf-8') as file:
        csv_content = file.read()

    return send_file(
        io.BytesIO(csv_content.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='ticketgenerator_export.csv'
    )
