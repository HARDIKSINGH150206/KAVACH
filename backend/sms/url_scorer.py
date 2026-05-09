from __future__ import annotations

import math
import re
from urllib.parse import urlparse

try:
    import tldextract
except ImportError:  # pragma: no cover
    tldextract = None

SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "cutt.ly",
    "rb.gy",
    "short.gy",
    "shorturl.at",
}
SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".click", ".link"}
LOOKALIKE_KEYWORDS = {"paytm", "sbi", "hdfc", "icici", "npc", "uidai", "morth", "fastag"}


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)>\]]+", text)


def _domain_parts(url: str) -> tuple[str, str, str]:
    if tldextract:
        ext = tldextract.extract(url)
        domain = ext.domain
        suffix = f".{ext.suffix}" if ext.suffix else ""
        full = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        return domain, suffix, full

    host = urlparse(url).netloc.lower()
    parts = host.split(".")
    domain = parts[-2] if len(parts) >= 2 else host
    suffix = f".{parts[-1]}" if len(parts) >= 2 else ""
    return domain, suffix, host


def score_url(url: str) -> dict:
    risk = 0.0
    flags: list[str] = []
    parsed = urlparse(url)
    domain, suffix, full = _domain_parts(url)

    if full in SHORTENERS:
        risk += 0.4
        flags.append("url_shortener")
    if suffix in SUSPICIOUS_TLDS:
        risk += 0.3
        flags.append("suspicious_tld")

    entropy = shannon_entropy(domain)
    if entropy > 3.5:
        risk += 0.2
        flags.append(f"high_entropy_{entropy:.1f}")

    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", parsed.netloc):
        risk += 0.4
        flags.append("ip_address_url")

    for keyword in LOOKALIKE_KEYWORDS:
        if keyword in domain and full not in {f"{keyword}.com", f"{keyword}.in"}:
            risk += 0.25
            flags.append(f"lookalike_{keyword}")

    return {"url_risk": round(min(risk, 1.0), 3), "entropy": round(entropy, 3), "tld": suffix, "flags": flags}
