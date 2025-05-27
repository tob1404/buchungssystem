from fpdf import FPDF
import os
import csv
import random
import string


def lade_bezahlte_buchungen(pfad='data/buchungen.csv'):
    buchungen = []
    with open(pfad, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) >= 18 and row[12] == 'bezahlt' and row[17].strip():
                buchungen.append(row)
    return buchungen


def generiere_tickets_pdf(buchung, ausgabeordner="tickets"):
    if not os.path.exists(ausgabeordner):
        os.makedirs(ausgabeordner)

    vorname = buchung[1]
    nachname = buchung[2]
    buchungstyp = buchung[0]
    ticketcodes = buchung[17].split(';') if buchung[17].strip() else []
    

    if not ticketcodes:
        print("⚠️ Keine Ticketcodes vorhanden.")
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for code in ticketcodes:
        pdf.add_page()
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 15, "Dirndlparty 2025", ln=True, align="C")

        pdf.set_font("Arial", "", 14)
        pdf.ln(10)
        pdf.cell(0, 10, f"Buchung: {vorname} {nachname}", ln=True, align="C")
        pdf.cell(0, 10, f"Tickettyp: {buchungstyp}", ln=True, align="C")

        pdf.set_font("Courier", "B", 36)
        pdf.ln(20)
        pdf.cell(0, 20, code, ln=True, align="C")

        pdf.set_font("Arial", "", 10)
        pdf.ln(10)
        pdf.cell(0, 10, "Musikverein Eningen – gültig für 1 Person", ln=True, align="C")

    dateiname = f"{ausgabeordner}/tickets_{vorname}_{nachname}.pdf"
    pdf.output(dateiname)
    print(f"✅ PDF erstellt: {dateiname}")
    return dateiname



def generiere_ticketcodes(anzahl, bestehende_codes):
    codes = []
    while len(codes) < anzahl:
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in bestehende_codes:
            bestehende_codes.add(code)
            codes.append(code)
    return codes

def erstelle_ticketgenerator_csv(quellpfad='data/buchungen.csv', zielpfad='data/ticketgenerator.csv'):
    bestehende_codes = set()
    bestehende_eintraege = {}

    # 1. Bestehende Einträge aus ticketgenerator.csv laden
    if os.path.exists(zielpfad):
        with open(zielpfad, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if len(row) < 10:
                    row += [''] * (10 - len(row))
                key = (row[1], row[2], row[3], row[8])  # (Vorname, Nachname, E-Mail, Zeitstempel)
                bestehende_eintraege[key] = row
                bestehende_codes.update(row[5].split(';'))

    neue_zeilen = []

    # 2. Neue Daten aus buchungen.csv prüfen
    with open(quellpfad, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) < 18:
                row += [''] * (18 - len(row))

            status = row[12].strip().lower()
            if status != 'bezahlt':
                continue

            buchungstyp = row[0]
            vorname = row[1]
            nachname = row[2]
            email = row[8]
            try:
                anzahl = int(row[10])
            except ValueError:
                continue

            zeitstempel = row[14]
            key = (vorname, nachname, email, zeitstempel)

            if key in bestehende_eintraege:
                # Bereits vorhanden → übernehmen
                neue_zeilen.append(bestehende_eintraege[key])
            else:
                # Neu → Codes generieren
                codes = generiere_ticketcodes(anzahl, bestehende_codes)
                codes_str = ';'.join(codes)
                neue_zeilen.append([
                    buchungstyp, vorname, nachname, email,
                    anzahl, codes_str, 'nein', 'nein', zeitstempel, 'noch nicht gedruckt'
                ])

    # 3. Schreiben
    with open(zielpfad, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Buchungstyp', 'Vorname', 'Nachname', 'E-Mail',
            'Anzahl', 'Ticketcodes', 'PDF erstellt', 'Mail versendet',
            'Zeitstempel', 'Druckstatus'
        ])
        writer.writerows(neue_zeilen)

    print(f"✅ {len(neue_zeilen)} Buchung(en) in {zielpfad} übernommen.")


