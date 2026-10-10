#!/usr/bin/env python3
"""
BREB (Bangladesh Rural Electrification Board / Palli Bidyut) API client.

Talks to the consumer-mobile-app API used by the official "com.myreb" app.
Authentication is a passwordless bearer token: POST a phone number to `login`
and the API returns a Laravel Sanctum token used on every subsequent call.
"""

import os
import configparser

import requests


class BREBConsumerAPI:
    BREB_BASE_URL = "https://service.rebpbs.com/api/v1/consumer-mobile-app"
    CONFIG_FILE = os.path.expanduser("~/.python-breb-api-config")
    TIMEOUT = 25

    def __init__(self):
        self.token = self.load_token()

    # --- auth ---------------------------------------------------------------

    def login(self, phone_number):
        """
        Log in with a phone number and return a bearer token.

        Login is passwordless: any phone number returns a token immediately.
        The token is saved to CONFIG_FILE and reused by later calls.
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
        self.save_token(token)
        return token

    def _get_info(self, account_number):
        """
        POST icbs/getInfo for an SMS account number.

        Returns the `data` object: {customer_info, billing_info}.
        Requires a token (call login() first).
        """
        if not self.token:
            raise RuntimeError("Not authenticated. Run login(phone_number) first.")

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

    # --- customer details ---------------------------------------------------

    def customer_info(self, account_number):
        """Return customer/meter details for an account number."""
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

    # --- bill ----------------------------------------------------------------

    def bill(self, account_number):
        """Return the latest bill (with arrears) for an account number."""
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
            "arrears": billing.get("ArrearDetails", []),
        }

    # --- token persistence ---------------------------------------------------

    def save_token(self, token):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"token": token}
        with open(self.CONFIG_FILE, "w") as configfile:
            config.write(configfile)

    def load_token(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_FILE):
            config.read(self.CONFIG_FILE)
            return config["DEFAULT"].get("token")
        return None
