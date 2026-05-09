from __future__ import annotations

import re

VEHICLE_REGEX = r"\b[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{3,4}\b"

ECHALLAN_KEYWORDS = ("echallan", "e-challan", "traffic challan", "challan", "parivahan", "morth")
KYC_KEYWORDS = ("kyc", "aadhaar link", "pan link", "account suspend", "account band", "verify identity")
FASTAG_KEYWORDS = ("fastag", "fas tag", "toll balance", "recharge")
OTP_SCAM_KEYWORDS = ("share otp", "otp share", "otp batao", "verify otp", "otp do", "send otp")
URGENCY_KEYWORDS = ("turant", "abhi", "immediately", "last warning", "legal action", "blocked", "suspended")
UPI_KEYWORDS = ("upi", "collect request", "refund", "cashback", "payment failed", "reverse payment")
BILL_KEYWORDS = ("electricity bill", "bijli bill", "power bill", "disconnection", "meter")
DELIVERY_KEYWORDS = ("parcel", "delivery", "courier", "address verify", "customs fee")
LOAN_JOB_KEYWORDS = ("loan approved", "instant loan", "job offer", "registration fee", "processing fee")


def classify_scam_type(text: str) -> dict:
    text_lower = text.lower()
    score = 0.0
    matched_rules: list[str] = []
    scam_type = None

    echallan_hits = sum(1 for keyword in ECHALLAN_KEYWORDS if keyword in text_lower)
    if echallan_hits:
        score += 0.35 + (0.08 * echallan_hits)
        matched_rules.append(f"echallan_keywords:{echallan_hits}")
        scam_type = "e-Challan"

    if re.search(VEHICLE_REGEX, text.upper()):
        score += 0.18
        matched_rules.append("vehicle_number_present")

    kyc_hits = sum(1 for keyword in KYC_KEYWORDS if keyword in text_lower)
    if kyc_hits:
        score += 0.25 * kyc_hits
        matched_rules.append(f"kyc_keywords:{kyc_hits}")
        scam_type = scam_type or "KYC Scam"

    fastag_hits = sum(1 for keyword in FASTAG_KEYWORDS if keyword in text_lower)
    if fastag_hits:
        score += 0.22 * fastag_hits
        matched_rules.append(f"fastag_keywords:{fastag_hits}")
        scam_type = scam_type or "FASTag Scam"

    upi_hits = sum(1 for keyword in UPI_KEYWORDS if keyword in text_lower)
    if upi_hits:
        score += 0.20 * upi_hits
        matched_rules.append(f"upi_keywords:{upi_hits}")
        scam_type = scam_type or "UPI Scam"

    bill_hits = sum(1 for keyword in BILL_KEYWORDS if keyword in text_lower)
    if bill_hits:
        score += 0.18 * bill_hits
        matched_rules.append(f"bill_keywords:{bill_hits}")
        scam_type = scam_type or "Utility Bill Scam"

    delivery_hits = sum(1 for keyword in DELIVERY_KEYWORDS if keyword in text_lower)
    if delivery_hits:
        score += 0.16 * delivery_hits
        matched_rules.append(f"delivery_keywords:{delivery_hits}")
        scam_type = scam_type or "Delivery Scam"

    loan_job_hits = sum(1 for keyword in LOAN_JOB_KEYWORDS if keyword in text_lower)
    if loan_job_hits:
        score += 0.16 * loan_job_hits
        matched_rules.append(f"loan_job_keywords:{loan_job_hits}")
        scam_type = scam_type or "Loan/Job Scam"

    otp_hits = sum(1 for keyword in OTP_SCAM_KEYWORDS if keyword in text_lower)
    if otp_hits:
        score += 0.45
        matched_rules.append(f"otp_scam_keywords:{otp_hits}")
        scam_type = scam_type or "OTP Scam"

    urgency_hits = sum(1 for keyword in URGENCY_KEYWORDS if keyword in text_lower)
    if urgency_hits:
        score += min(0.2, urgency_hits * 0.08)
        matched_rules.append(f"urgency_keywords:{urgency_hits}")

    rule_score = round(min(score, 1.0), 3)
    return {
        "is_scam_pattern": rule_score > 0.3,
        "scam_type": scam_type,
        "rule_score": rule_score,
        "matched_rules": matched_rules,
    }
