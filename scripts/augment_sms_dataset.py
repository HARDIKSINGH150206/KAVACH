#!/usr/bin/env python3
"""
Augment SMS dataset with regex-based variations for better model training.
Generates synthetic samples by replacing placeholders in existing SMS templates.
"""

import random
import re
import string
from pathlib import Path

import pandas as pd

# Vehicle number pattern: MH12AB1234
VEHICLE_PATTERN = re.compile(r"MH\d{2}[A-Z]{2}\d{4}")
AMOUNT_PATTERN = re.compile(r"Rs\.(\d+)")
ACCOUNT_PATTERN = re.compile(r"XX\d{4}|\d{4}")
OTP_PATTERN = re.compile(r"\d{6}")
PNR_PATTERN = re.compile(r"\d{10}")
URL_PATTERN = re.compile(r"https?://[^\s]+")


def random_vehicle():
    """Generate random Indian vehicle number."""
    state = "MH"
    num = random.randint(10, 99)
    letter1 = random.choice(string.ascii_uppercase)
    letter2 = random.choice(string.ascii_uppercase)
    digits = random.randint(1000, 9999)
    return f"{state}{num}{letter1}{letter2}{digits}"


def random_amount():
    """Generate random amount between 100-5000."""
    return str(random.randint(100, 5000))


def random_account():
    """Generate random account ending."""
    return f"{random.randint(1000,9999)}"


def random_otp():
    """Generate random 6-digit OTP."""
    return f"{random.randint(100000,999999)}"


def random_pnr():
    """Generate random 10-digit PNR."""
    return f"{random.randint(1000000000,9999999999)}"


def random_url():
    """Generate random suspicious URL."""
    domains = ["bit.ly", "tinyurl.com", "cutt.ly", "short.link", "linktree.com", "xyz", "click", "secure"]
    paths = [f"{random.randint(100,999)}", f"{random.choice(string.ascii_lowercase)}{random.randint(10,99)}"]
    return f"https://{random.choice(domains)}/{random.choice(paths)}"


def augment_text(text: str, is_phishing: bool = True) -> str:
    """Augment a single SMS text with random variations."""
    text = VEHICLE_PATTERN.sub(lambda m: random_vehicle(), text)
    text = AMOUNT_PATTERN.sub(lambda m: f"Rs.{random_amount()}", text)
    text = ACCOUNT_PATTERN.sub(lambda m: random_account(), text)
    text = OTP_PATTERN.sub(lambda m: random_otp(), text)
    text = PNR_PATTERN.sub(lambda m: random_pnr(), text)
    if is_phishing:
        text = URL_PATTERN.sub(lambda m: random_url(), text)
    return text


def augment_dataset(input_csv: Path, output_csv: Path, target_samples: int = 1000):
    """Augment dataset to target number of samples."""
    df = pd.read_csv(input_csv)
    original_count = len(df)
    augmented_texts = []

    # Keep originals
    augmented_texts.extend(df["text"].tolist())

    # Generate variations
    while len(augmented_texts) < target_samples:
        for text in df["text"]:
            if len(augmented_texts) >= target_samples:
                break
            augmented_texts.append(augment_text(text, "phishing" in str(input_csv).lower()))

    # Create new dataframe
    new_df = pd.DataFrame({"text": augmented_texts[:target_samples]})
    new_df.to_csv(output_csv, index=False)
    print(f"Augmented {input_csv.name}: {original_count} -> {len(new_df)} samples")


def main():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "backend" / "data"

    # Augment phishing dataset
    augment_dataset(data_dir / "phishing_sms.csv", data_dir / "phishing_sms_augmented.csv", target_samples=5000)

    # Augment legit dataset
    augment_dataset(data_dir / "legit_sms.csv", data_dir / "legit_sms_augmented.csv", target_samples=2500)


if __name__ == "__main__":
    main()
