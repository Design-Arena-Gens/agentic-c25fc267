import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from python.forex_scanner import ForexScannerError, fetch_exchange_rates  # noqa: E402


DEFAULT_PAIRS = [
    "EUR/USD",
    "USD/JPY",
    "GBP/USD",
    "USD/CHF",
    "AUD/USD",
]


class handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            self._send_json({"error": "Missing ALPHA_VANTAGE_API_KEY environment variable."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query, keep_blank_values=False)

        raw_pairs = params.get("pairs", [])
        requested_pairs = []
        for entry in raw_pairs:
            requested_pairs.extend(item.strip() for item in entry.split(",") if item.strip())

        if not requested_pairs:
            requested_pairs = DEFAULT_PAIRS

        try:
            quotes, errors = fetch_exchange_rates(requested_pairs, api_key)
        except ForexScannerError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        payload = {
            "data": [
                {
                    "pair": quote.pair,
                    "exchange_rate": quote.exchange_rate,
                    "bid_price": quote.bid_price,
                    "ask_price": quote.ask_price,
                    "last_refreshed": quote.last_refreshed,
                    "timezone": quote.timezone,
                    "from_currency": quote.from_currency,
                    "to_currency": quote.to_currency,
                }
                for quote in quotes
            ],
            "errors": errors,
        }

        self._send_json(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

