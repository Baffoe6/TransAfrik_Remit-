"""Default notification templates for transfer lifecycle events."""

DEFAULT_TEMPLATES = [
    {
        "code": "transfer_created",
        "name": "Transfer Created",
        "channel": "email",
        "subject": "TransAfrik: Transfer {reference} created",
        "body_template": "Hi {customer_name},\n\nYour transfer {reference} for R{amount_zar} has been created.\n\nStatus: {status}\n\nTransAfrik Remit — IPAYGO (Pty) Ltd",
    },
    {
        "code": "transfer_created",
        "name": "Transfer Created SMS",
        "channel": "sms",
        "subject": None,
        "body_template": "TransAfrik: Transfer {reference} created. Pay R{total_zar} to complete. Ref: {payment_reference}",
    },
    {
        "code": "payment_received",
        "name": "Payment Received",
        "channel": "email",
        "subject": "TransAfrik: Payment received for {reference}",
        "body_template": "Hi {customer_name},\n\nWe received your payment for transfer {reference}. Your transfer is being processed.\n\nTransAfrik Remit",
    },
    {
        "code": "payment_verified",
        "name": "Payment Verified",
        "channel": "sms",
        "subject": None,
        "body_template": "TransAfrik: Payment verified for {reference}. Recipient will receive GHS {receive_ghs}.",
    },
    {
        "code": "transfer_completed",
        "name": "Transfer Completed",
        "channel": "email",
        "subject": "TransAfrik: Transfer {reference} completed",
        "body_template": "Hi {customer_name},\n\nGreat news! Transfer {reference} of GHS {receive_ghs} to {beneficiary_name} has been completed.\n\nTransAfrik Remit",
    },
    {
        "code": "transfer_failed",
        "name": "Transfer Failed",
        "channel": "email",
        "subject": "TransAfrik: Transfer {reference} update",
        "body_template": "Hi {customer_name},\n\nTransfer {reference} could not be completed. Reason: {reason}\n\nContact support@transafrik.co.za for assistance.\n\nTransAfrik Remit",
    },
    {
        "code": "compliance_review",
        "name": "Compliance Review Required",
        "channel": "email",
        "subject": "TransAfrik: Additional review for {reference}",
        "body_template": "Hi {customer_name},\n\nTransfer {reference} requires additional compliance review. We will update you within 24 hours.\n\nTransAfrik Remit",
    },
    {
        "code": "transfer_created",
        "name": "Transfer Created WhatsApp",
        "channel": "whatsapp",
        "subject": None,
        "body_template": "Hi {customer_name}! Your TransAfrik transfer {reference} for R{amount_zar} is ready. Pay R{total_zar} using ref {payment_reference}.",
    },
    {
        "code": "payment_verified",
        "name": "Payment Verified WhatsApp",
        "channel": "whatsapp",
        "subject": None,
        "body_template": "TransAfrik: Payment confirmed for {reference}. GHS {receive_ghs} will be sent to {beneficiary_name}.",
    },
    {
        "code": "transfer_completed",
        "name": "Transfer Completed WhatsApp",
        "channel": "whatsapp",
        "subject": None,
        "body_template": "Great news {customer_name}! Transfer {reference} of GHS {receive_ghs} to {beneficiary_name} is complete.",
    },
]
