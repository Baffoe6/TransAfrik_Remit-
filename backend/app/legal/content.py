OPERATOR = "iPayGo (Pty) Ltd"
PLATFORM = "TransAfrik Remit"

DISCLAIMER = (
    "TransAfrik Remit is operated by iPayGo (Pty) Ltd as a customer-facing remittance "
    "facilitation platform. Transfers are processed through approved third-party payment "
    "and remittance partners."
)

LEGAL_PAGES = {
    "terms": {
        "title": "Terms of Use",
        "sections": [
            {"heading": "Agreement", "body": f"By using {PLATFORM}, you agree to these terms. {DISCLAIMER}"},
            {"heading": "Service Description", "body": "We facilitate remittance requests between South Africa and supported destination countries through licensed partners."},
            {"heading": "User Responsibilities", "body": "You must provide accurate information, complete KYC verification, and comply with applicable laws."},
            {"heading": "Fees", "body": "Transfer fees and exchange rates are disclosed before you confirm a transaction."},
        ],
    },
    "privacy": {
        "title": "Privacy Policy",
        "sections": [
            {"heading": "Data Controller", "body": f"{OPERATOR} is the responsible party for personal information collected through {PLATFORM}."},
            {"heading": "Information Collected", "body": "Identity documents, contact details, transaction history, and device/session data."},
            {"heading": "Purpose", "body": "KYC/AML compliance, transaction processing, customer support, and service improvement."},
            {"heading": "Retention", "body": "Data is retained as required by FIC regulations and POPIA."},
        ],
    },
    "popia": {
        "title": "POPIA Notice",
        "sections": [
            {"heading": "Your Rights", "body": "Under POPIA you may request access, correction, or deletion of your personal information subject to legal retention requirements."},
            {"heading": "Information Officer", "body": "Contact: privacy@ipaygo.co.za"},
            {"heading": "Cross-Border Transfer", "body": "Remittance data may be shared with partner institutions in destination countries for transaction fulfilment."},
        ],
    },
    "aml-fica": {
        "title": "AML / FICA Notice",
        "sections": [
            {"heading": "Regulatory Compliance", "body": f"{PLATFORM} complies with FIC Act requirements including customer identification and record-keeping."},
            {"heading": "Monitoring", "body": "Transactions are screened for suspicious activity. We may request additional documentation."},
            {"heading": "Reporting", "body": "Suspicious transactions may be reported to the Financial Intelligence Centre."},
        ],
    },
    "refund": {
        "title": "Refund Policy",
        "sections": [
            {"heading": "Eligibility", "body": "Refunds may be issued for failed or cancelled transfers where funds were collected but not disbursed."},
            {"heading": "Processing Time", "body": "Approved refunds are processed within 5-10 business days to the original payment method where possible."},
            {"heading": "Fees", "body": "Service fees may be non-refundable once a transfer has been submitted to a partner."},
        ],
    },
    "complaints": {
        "title": "Complaints Policy",
        "sections": [
            {"heading": "How to Complain", "body": "Email complaints@transafrik.co.za or raise a support ticket in your dashboard."},
            {"heading": "Response Time", "body": "We acknowledge complaints within 2 business days and aim to resolve within 15 business days."},
            {"heading": "Escalation", "body": "Unresolved complaints may be escalated to our compliance team."},
        ],
    },
    "partner-disclaimer": {
        "title": "Partner Processing Disclaimer",
        "sections": [
            {"heading": "Third-Party Processing", "body": DISCLAIMER},
            {"heading": "Partners", "body": "Payment collection and disbursement are performed by approved partners including Mukuru, Flutterwave, Pay@, EasyPay, and others."},
            {"heading": "No Banking Licence", "body": f"{OPERATOR} is not a bank or licensed remittance operator. We act as a facilitation platform."},
        ],
    },
}
