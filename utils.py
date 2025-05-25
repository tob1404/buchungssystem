import csv

def lade_buchungen():
    tische_belegt = set()
    belegte_plaetze = 0

    try:
        with open('data/buchungen.csv', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                if len(row) < 15:
                    row += [''] * (15 - len(row))  # ⬅️ ANPASSUNG: 14 statt 13 Spalten
                art, _, _, _, _, _, _, _, _, tischnummer, anzahl, _, _, _,_ = row  # ⬅️ ANPASSUNG: 14 Variablen

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
                if len(row) < 15:  # ⬅️ ANPASSUNG
                    row += [''] * (15 - len(row))
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
            'Kommentar', 'Status', 'Betrag (€)', 'Zeitstempel'  # ⬅️ NEUE SPALTE
        ])
        writer.writerows(buchungen)
