import csv

def lade_buchungen():
    tische_belegt = set()
    belegte_plaetze = 0

    try:
        with open('data/buchungen.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if len(row) < 13:
                    row += [''] * (13 - len(row))
                art, _, _, _, _, _, _, _, _, tischnummer, anzahl, _, _ = row

                if art == 'tisch' and tischnummer:
                    plaetze = 0
                    for nummer in tischnummer.split(','):
                        if nummer.strip().isdigit():
                            tische_belegt.add(int(nummer.strip()))
                            plaetze += 10
                    belegte_plaetze += plaetze
                elif art == 'einzelticket' and anzahl:
                    belegte_plaetze += int(anzahl)
    except FileNotFoundError:
        pass

    return tische_belegt, belegte_plaetze



def lese_buchungen_komplett():
    buchungen = []

    try:
        with open('data/buchungen.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if len(row) < 13:
                    row += [''] * (13 - len(row))  # Fehlende Spalten ergänzen
                buchungen.append(row)
    except FileNotFoundError:
        pass

    return buchungen


def speichere_buchungen(buchungen):
    with open('data/buchungen.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Buchungstyp', 'Vorname', 'Nachname', 'PLZ', 'Ort', 'Straße',
            'Hausnummer', 'Telefon', 'E-Mail', 'Tischnummer', 'Anzahl Tickets',
            'Kommentar', 'Status'
        ])
        writer.writerows(buchungen)
