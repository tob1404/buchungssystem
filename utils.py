import csv

def lade_buchungen():
    tische_belegt = set()
    freie_einzeltickets = 360  # Anfangs 360 Plätze

    try:
        with open('data/buchungen.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # Kopfzeile überspringen
            for row in reader:
                if len(row) < 13:
                    row += [''] * (13 - len(row))  # Falls Felder fehlen, auffüllen
                art, vorname, nachname, plz, ort, strasse, hausnummer, telefon, email, tischnummer, anzahl, kommentar, status = row

                if art == 'tisch' and tischnummer:
                    tische_belegt.add(int(tischnummer))
                elif art == 'einzelticket' and anzahl:
                    freie_einzeltickets -= int(anzahl)
    except FileNotFoundError:
        pass

    return tische_belegt, freie_einzeltickets


def lese_buchungen_komplett():
    buchungen = []

    try:
        with open('data/buchungen.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if len(row) < 12:
                    row += [''] * (12 - len(row))  # Fehlende Spalten ergänzen
                buchungen.append(row)
    except FileNotFoundError:
        pass

    return buchungen


def speichere_buchungen(buchungen):
    with open('data/buchungen.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Buchungstyp', 'Name', 'Alter', 'Adresse', 'E-Mail', 'Tischnummer', 'Anzahl Tickets', 'Status'])
        writer.writerows(buchungen)
