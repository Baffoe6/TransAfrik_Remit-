"""Generate payment voucher PDF with branding, barcode, and QR code."""

import base64
from io import BytesIO

import qrcode
from fpdf import FPDF

from app.config import get_settings

settings = get_settings()


def _make_qr_base64(data: str, size: int = 120) -> str:
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


class VoucherPDF(FPDF):
    def header(self):
        self.set_fill_color(27, 94, 59)
        self.rect(0, 0, 210, 25, "F")
        self.set_text_color(201, 162, 39)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 20, "TransAfrik Remit", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(45, 45, 45)
        self.ln(5)


def generate_voucher_pdf(
    *,
    transfer_reference: str,
    payment_reference: str,
    voucher_number: str | None,
    amount: str,
    expiry_date: str,
    barcode_data: str | None,
    qr_data: str | None,
    payment_method: str,
) -> bytes:
    pdf = VoucherPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Operated by IPAYGO (Pty) Ltd", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Payment Voucher", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(4)

    rows = [
        ("Transfer Number", transfer_reference),
        ("Payment Reference", payment_reference),
        ("Voucher Number", voucher_number or "N/A"),
        ("Payment Method", payment_method),
        ("Amount Due", f"R {amount}"),
        ("Expiry Date", expiry_date),
    ]
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 8, label + ":")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "Barcode", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 10, barcode_data or payment_reference, new_x="LMARGIN", new_y="NEXT")

    qr_payload = qr_data or payment_reference
    try:
        qr_b64 = _make_qr_base64(qr_payload)
        qr_path = BytesIO(base64.b64decode(qr_b64))
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "Scan to Pay", new_x="LMARGIN", new_y="NEXT")
        pdf.image(qr_path, x=80, w=40, h=40)
        pdf.ln(44)
    except Exception:
        pdf.set_font("Courier", "", 9)
        pdf.cell(0, 8, f"QR: {qr_payload}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        5,
        "TransAfrik Remit is a customer-facing remittance facilitation platform operated by "
        "IPAYGO (Pty) Ltd. Transfers are processed through approved third-party payment and "
        "remittance partners.",
    )

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
