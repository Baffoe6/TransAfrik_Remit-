"""Generate downloadable compliance PDF packs."""

from datetime import UTC, datetime

from fpdf import FPDF
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.compliance import CustomerRiskProfile
from app.models.customer_profile import CustomerProfile
from app.models.enums import CompliancePackType
from app.models.kyc_document import KycDocument
from app.models.mukuru_operations import MukuruBatch
from app.models.payment_proof import PaymentProof
from app.models.transfer import Transfer
from app.models.transfer_status_history import TransferStatusHistory
from app.models.user import User


class _CompliancePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "TransAfrik Remit - Compliance Pack", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.cell(0, 6, "Operated by iPayGo (Pty) Ltd", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def section(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)


def _save_pdf(pdf: FPDF, filename: str) -> str:
    from app.utils.file_storage import save_bytes

    content = pdf.output()
    if isinstance(content, str):
        content = content.encode("latin-1")
    return save_bytes(content, "compliance_packs", filename)


def generate_kyc_summary_pack(db: Session, user_id: int) -> str:
    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
    docs = db.query(KycDocument).filter(KycDocument.user_id == user_id).all()
    risk = db.query(CustomerRiskProfile).filter(CustomerRiskProfile.user_id == user_id).first()

    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("Customer KYC Summary")
    pdf.cell(0, 6, f"Customer: {profile.first_name} {profile.last_name}" if profile else f"User #{user_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Email: {user.email if user else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"KYC Status: {profile.kyc_status.value if profile else 'unknown'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Risk Level: {risk.risk_level if risk else 'not_assessed'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.section("Documents")
    for d in docs:
        pdf.cell(0, 6, f"- {d.document_type.value}: {d.status.value} ({d.original_filename})", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"kyc_summary_{user_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_transfer_audit_pack(db: Session, transfer_id: int) -> str:
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    history = (
        db.query(TransferStatusHistory)
        .filter(TransferStatusHistory.transfer_id == transfer_id)
        .order_by(TransferStatusHistory.created_at)
        .all()
    )
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == transfer.beneficiary_id).first() if transfer else None

    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("Transfer Audit Trail")
    if transfer:
        pdf.cell(0, 6, f"Reference: {transfer.reference}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Amount: R{transfer.send_amount_zar} -> GHS {transfer.receive_amount_ghs}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Status: {transfer.status}", new_x="LMARGIN", new_y="NEXT")
        if beneficiary:
            pdf.cell(0, 6, f"Beneficiary: {beneficiary.full_name} ({beneficiary.country})", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.section("Status History")
    for h in history:
        pdf.cell(0, 6, f"{h.created_at}: {h.from_status} -> {h.to_status}", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"transfer_audit_{transfer_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_payment_proof_pack(db: Session, transfer_id: int) -> str:
    proofs = db.query(PaymentProof).filter(PaymentProof.transfer_id == transfer_id).all()
    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("Payment Proof Summary")
    pdf.cell(0, 6, f"Transfer ID: {transfer_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Proofs on file: {len(proofs)}", new_x="LMARGIN", new_y="NEXT")
    for p in proofs:
        pdf.cell(0, 6, f"- {p.original_filename} uploaded {p.created_at}", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"payment_proof_{transfer_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_aml_review_pack(db: Session, user_id: int) -> str:
    risk = db.query(CustomerRiskProfile).filter(CustomerRiskProfile.user_id == user_id).first()
    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("AML Risk Review")
    if risk:
        pdf.cell(0, 6, f"Risk Level: {risk.risk_level}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Risk Score: {risk.risk_score}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"AML Flags: {risk.aml_flag_count}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Notes: {risk.notes or 'None'}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "No risk profile on file", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"aml_review_{user_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_mukuru_batch_pack(db: Session, batch_id: int) -> str:
    batch = db.query(MukuruBatch).filter(MukuruBatch.id == batch_id).first()
    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("Mukuru Batch Summary")
    if batch:
        pdf.cell(0, 6, f"Batch ID: {batch.batch_reference}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Status: {batch.status}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Transfers: {batch.transfer_count}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Total ZAR: {batch.total_amount_zar}", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"mukuru_batch_{batch_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_partner_onboarding_pack(db: Session) -> str:
    from app.models.webhook import ProviderConfig

    configs = db.query(ProviderConfig).filter(ProviderConfig.is_enabled.is_(True)).all()
    pdf = _CompliancePDF()
    pdf.add_page()
    pdf.section("Partner Onboarding Document Pack")
    pdf.multi_cell(0, 6, "TransAfrik Remit is operated by iPayGo (Pty) Ltd as a customer-facing remittance facilitation platform. Transfers are processed through approved third-party payment and remittance partners.")
    pdf.ln(4)
    pdf.section("Active Partners")
    for c in configs:
        mode = "Sandbox" if c.is_sandbox else "Production"
        pdf.cell(0, 6, f"- {c.display_name} ({c.provider_code}) - {mode}", new_x="LMARGIN", new_y="NEXT")
    return _save_pdf(pdf, f"partner_onboarding_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.pdf")


def generate_compliance_pack(db: Session, pack_type: CompliancePackType, **kwargs) -> str:
    generators = {
        CompliancePackType.KYC_SUMMARY: lambda: generate_kyc_summary_pack(db, kwargs["user_id"]),
        CompliancePackType.TRANSFER_AUDIT: lambda: generate_transfer_audit_pack(db, kwargs["transfer_id"]),
        CompliancePackType.PAYMENT_PROOF: lambda: generate_payment_proof_pack(db, kwargs["transfer_id"]),
        CompliancePackType.AML_REVIEW: lambda: generate_aml_review_pack(db, kwargs["user_id"]),
        CompliancePackType.MUKURU_BATCH: lambda: generate_mukuru_batch_pack(db, kwargs["batch_id"]),
        CompliancePackType.PARTNER_ONBOARDING: lambda: generate_partner_onboarding_pack(db),
    }
    return generators[pack_type]()
