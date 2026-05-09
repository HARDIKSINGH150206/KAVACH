from __future__ import annotations

import argparse
import time

import requests

DEMO_MESSAGES = [
    "Vehicle MH12AB1234 ka e-challan Rs.500 pending hai. Pay karein: https://bit.ly/challan99 -MoRTH",
    "SBI: Aapka KYC expire ho raha hai. Abhi update: https://tinyurl.com/sbikycnow ya account band!",
    "FASTag balance low Rs.12. Recharge now: https://cutt.ly/fastagpay avoid toll penalty",
    "ECHLNG: Payment received for challan 2024DL5678. Thank you. -Parivahan",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject demo SMS messages into KAVACH.")
    parser.add_argument("--api", default="http://localhost:8000", help="KAVACH API base URL")
    parser.add_argument("--interval", type=float, default=4.0, help="Seconds between messages")
    args = parser.parse_args()

    index = 0
    while True:
        message = DEMO_MESSAGES[index % len(DEMO_MESSAGES)]
        response = requests.post(f"{args.api}/sms/mock", json={"text": message}, timeout=5)
        response.raise_for_status()
        print(f"Injected: {message[:90]}")
        index += 1
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
