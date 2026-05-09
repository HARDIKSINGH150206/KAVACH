from __future__ import annotations

import asyncio

_queue: asyncio.Queue[str] = asyncio.Queue()

DEMO_MESSAGES = [
    "Vehicle MH12AB1234 ka e-challan Rs.500 pending hai. Pay karein: https://bit.ly/challan99 -MoRTH",
    "SBI: Aapka KYC expire ho raha hai. Abhi update: https://tinyurl.com/sbikycnow ya account band!",
    "FASTag balance low Rs.12. Recharge now: https://cutt.ly/fastagpay avoid toll penalty",
    "ECHLNG: Payment received for challan 2024DL5678. Thank you. -Parivahan",
    "HDFCBK: Your A/c XX4321 credited Rs.15000 on 07-May. Avl Bal Rs.87650.",
]


def inject_mock_sms(text: str) -> None:
    _queue.put_nowait(text)


async def get_next_sms(timeout: float = 0.1) -> str | None:
    try:
        return await asyncio.wait_for(_queue.get(), timeout=timeout)
    except asyncio.TimeoutError:
        return None


async def demo_sms_pump(interval: float = 5.0) -> None:
    index = 0
    while True:
        inject_mock_sms(DEMO_MESSAGES[index % len(DEMO_MESSAGES)])
        index += 1
        await asyncio.sleep(interval)
