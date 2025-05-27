from fpdf import FPDF
import os
import qrcode

def generiere_qr_pdf(vorname, nachname, buchungstyp, ticketcodes, ausgabeordner="tickets_qr"):
    if not os.path.exists(ausgabeordner):
        os.makedirs(ausgabeordner)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for code in ticketcodes:
        # QR-Code generieren und temporär speichern
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        pfad = os.path.join(ausgabeordner, f"{code}.png")
        img.save(pfad)

        # PDF-Seite
        pdf.add_page()

        # Veranstaltungsinfos oben
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 12, "Dirndlparty 2025", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "27.09.2025  HAP Grießhaber Halle Eningen", ln=True, align="C")
        pdf.cell(0, 10, "Live-Band: Dirndlstürmer", ln=True, align="C")
        pdf.cell(0, 10, "Kontakt: dirndlparty@mv-eningen.de", ln=True, align="C")
        pdf.ln(10)

        # Buchungsinfos
        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, f"Buchung: {vorname} {nachname}", ln=True, align="C")
        pdf.cell(0, 10, f"Tickettyp: {buchungstyp}", ln=True, align="C")
        pdf.ln(5)

        # QR-Code Bild
        pdf.image(pfad, x=80, y=pdf.get_y(), w=50, h=50)
        pdf.ln(60)

        # Code darunter als Text
        pdf.set_font("Courier", "B", 28)
        pdf.cell(0, 15, code, ln=True, align="C")
        pdf.ln(5)

        # Zusatzinfo
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Musikverein Eningen  gültig für 1 Person", ln=True, align="C")

        # Bild wieder löschen
        os.remove(pfad)

    dateiname = f"{ausgabeordner}/tickets_{vorname}_{nachname}_qr.pdf"
    pdf.output(dateiname)
    print(f"✅ PDF mit QR-Codes erstellt: {dateiname}")
    return dateiname
