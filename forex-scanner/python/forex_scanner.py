"""
Utility functions for fetching live Forex exchange rates from Alpha Vantage.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable, List, Tuple


API_URL_TEMPLATE = (
    "https://www.alphavantage.co/query"
    "?function=CURRENCY_EXCHANGE_RATE&from_currency={from_code}&to_currency={to_code}&apikey={api_key}"
)


class ForexScannerError(Exception):
    """Raised when fetching exchange rates fails."""


@dataclass(slots=True)
class ForexQuote:
    pair: str
    exchange_rate: float
    bid_price: float | None
    ask_price: float | None
    last_refreshed: str
    timezone: str
    from_currency: str
    to_currency: str


def _normalize_pair(raw_pair: str) -> Tuple[str, str]:
    sanitized = raw_pair.replace("-", "/").replace("_", "/").strip()
    if "/" not in sanitized:
        if len(sanitized) == 6:
            sanitized = f"{sanitized[:3]}/{sanitized[3:]}"
        else:
            raise ForexScannerError(f"Invalid currency pair format: '{raw_pair}'")

    base, quote = [part.strip().upper() for part in sanitized.split("/", maxsplit=1)]

    if not (base.isalpha() and quote.isalpha() and len(base) == 3 and len(quote) == 3):
        raise ForexScannerError(f"Invalid currency codes in pair '{raw_pair}'")

    return base, quote


def _fetch_pair(from_code: str, to_code: str, api_key: str, timeout: float = 10.0) -> ForexQuote:
    url = API_URL_TEMPLATE.format(from_code=from_code, to_code=to_code, api_key=api_key)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise ForexScannerError(f"Network error while fetching {from_code}/{to_code}: {exc}") from exc

    if "Error Message" in payload:
        raise ForexScannerError(payload["Error Message"])

    if "Note" in payload:
        raise ForexScannerError(payload["Note"])

    quote_block = payload.get("Realtime Currency Exchange Rate")
    if not quote_block:
        raise ForexScannerError(f"Unexpected response for {from_code}/{to_code}")

    def _get_float(key: str) -> float | None:
        raw_value = quote_block.get(key)
        if raw_value is None:
            return None
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return None

    pair = f"{from_code}/{to_code}"

    return ForexQuote(
        pair=pair,
        exchange_rate=_get_float("5. Exchange Rate") or 0.0,
        bid_price=_get_float("8. Bid Price"),
        ask_price=_get_float("9. Ask Price"),
        last_refreshed=quote_block.get("6. Last Refreshed", "Unknown"),
        timezone=quote_block.get("7. Time Zone", "UTC"),
        from_currency=quote_block.get("2. From_Currency Name", from_code),
        to_currency=quote_block.get("4. To_Currency Name", to_code),
    )


def fetch_exchange_rates(pairs: Iterable[str], api_key: str) -> Tuple[List[ForexQuote], List[str]]:
    """
    Fetch exchange rates for the provided currency pairs.

    Returns a tuple containing the successful quotes and any error messages.
    """
    if not api_key:
        raise ForexScannerError("Alpha Vantage API key is missing.")

    results: List[ForexQuote] = []
    errors: List[str] = []

    for raw_pair in pairs:
        if not raw_pair:
            continue

        try:
            base, quote = _normalize_pair(raw_pair)
            quote_data = _fetch_pair(base, quote, api_key)
            results.append(quote_data)
            time.sleep(0.2)  # Courtesy delay to stay within free tier rate limits
        except ForexScannerError as exc:
            errors.append(str(exc))

    return results, errors


def main(argv: List[str] | None = None) -> int:
    """
    Command-line entry point.

    Usage:
        python -m python.forex_scanner EUR/USD GBPJPY
    """
    argv = list(argv or sys.argv[1:])

    if not argv:
        print("Usage: python -m python.forex_scanner EUR/USD GBPJPY ...", file=sys.stderr)
        return 1

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Error: ALPHA_VANTAGE_API_KEY environment variable is not set.", file=sys.stderr)
        return 1

    quotes, errors = fetch_exchange_rates(argv, api_key)

    for quote in quotes:
        bid = f"{quote.bid_price:.6f}" if quote.bid_price is not None else "N/A"
        ask = f"{quote.ask_price:.6f}" if quote.ask_price is not None else "N/A"
        print(
            f"{quote.pair} | Rate: {quote.exchange_rate:.6f} | Bid: {bid} | "
            f"Ask: {ask} | Updated: {quote.last_refreshed} ({quote.timezone})"
        )

    if errors:
        print("\nErrors:", file=sys.stderr)
        for message in errors:
            print(f"- {message}", file=sys.stderr)
        return 2 if not quotes else 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

