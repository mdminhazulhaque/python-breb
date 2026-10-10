#!/usr/bin/env python3
"""
BREB (Bangladesh Rural Electrification Board / Palli Bidyut) API client.

Stateless core engine: construct with an optional bearer token, call methods,
get back plain dicts. No file or environment I/O happens here, so the class is
safe to instantiate per-request inside FastAPI, Django, or any web framework.
Token persistence (file, DB, Redis) is the caller's responsibility -- see the
`examples/` directory.
"""

import requests


class BREBConsumerAPI:
    BREB_BASE_URL = "https://service.rebpbs.com/api/v1/consumer-mobile-app"
    TIMEOUT = 25

    def __init__(self, token=None):
        """
        Args:
            token: a bearer token obtained from `login()`. Required for every
                   call except `login()` itself.
        """
        self.token = token

    # --- auth ---------------------------------------------------------------

    def login(self, phone_number):
        """
        Log in with a phone number and return a bearer token.

        Login is passwordless: any registered phone number returns a token
        immediately. The token is also stored on `self.token` for convenience,
        but it is NOT persisted anywhere -- persist the returned value yourself.
        """
        url = f"{self.BREB_BASE_URL}/login"
        response = requests.post(
            url,
            headers={"Accept": "application/json"},
            files={"phone_number": (None, str(phone_number))},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

        token = response.json().get("data", {}).get("token")
        if not token:
            raise RuntimeError(f"Login failed: {response.text}")

        self.token = token
        return token

    def _get_info(self, account_number):
        """POST icbs/getInfo and return the `data` object {customer_info, billing_info}."""
        if not self.token:
            raise RuntimeError("Not authenticated. Pass token= or call login() first.")

        url = f"{self.BREB_BASE_URL}/icbs/getInfo"
        response = requests.post(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            files={"sms_account_number": (None, str(account_number))},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(payload.get("message", "Request failed"))
        return payload["data"]

    # --- data ----------------------------------------------------------------

    def customer_info(self, account_number):
        """Return customer/meter details as a dict."""
        info = self._get_info(account_number)["customer_info"]
        return {
            "account_number": info.get("AccountNumber"),
            "name": info.get("ConsumerName"),
            "father_name": info.get("FatherName"),
            "address": info.get("ConsumerAddress"),
            "mobile": info.get("MobileNumber"),
            "pbs": info.get("PBSName"),
            "pbs_office": info.get("PBSOfficeName"),
            "tariff_category": info.get("TariffCategory"),
            "phase": info.get("Phase"),
            "load_kw": info.get("LoadKW"),
            "meter_number": info.get("MeterNumber"),
        }

    def bill(self, account_number):
        """Return the latest bill (with arrears) as a dict."""
        billing = self._get_info(account_number)["billing_info"]
        return {
            "bill_number": billing.get("BillNumber"),
            "bill_month": billing.get("BillMonth"),
            "used_kwh": billing.get("TotalUsedKwh"),
            "billed_amount": billing.get("BilledAmount"),
            "billed_amount_with_lpc": billing.get("BilledAmountWithLPC"),
            "bill_date": billing.get("BillDate"),
            "last_payment_date": billing.get("LastPaymentDate"),
            "last_payment_date_with_lpc": billing.get("LastPaymentDateWithLpc"),
            "payment_status": billing.get("PaymentStatus"),
            "payment_channel": billing.get("PaymentChannel"),
            "arrears": [
                {
                    "bill_month": a.get("BillMonth"),
                    "receivable": a.get("ReceivableAmount"),
                }
                for a in billing.get("ArrearDetails", [])
            ],
        }
