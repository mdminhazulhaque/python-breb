#!/usr/bin/env python3
"""
BREB Consumer CLI

A command-line interface for the Bangladesh REB / Palli Bidyut consumer API.
Provides commands to log in (passwordless, phone number only), look up customer
details, and view the latest bill.
"""

import sys
import functools

import click
import requests
from tabulate import tabulate

from .breb import BREBConsumerAPI
from . import __version__


def handle_api_error(func):
    """Decorator to handle API errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            click.echo(
                f"❌ Could not reach the BREB API at {BREBConsumerAPI.BREB_BASE_URL}.\n"
                "   The service may be down or temporarily unreachable from your network. "
                "Please try again later.",
                err=True,
            )
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            sys.exit(1)
    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="breb-cli")
def app():
    """
    🔌 BREB Consumer CLI

    A command-line tool for Bangladesh REB / Palli Bidyut consumer accounts.
    Log in with your phone number, then look up customer details and bills.
    """
    pass


@app.command(name="login")
@click.argument("phone_number")
@handle_api_error
def login(phone_number):
    """Log in with a phone number and save the bearer token."""
    click.echo(f"🔐 Logging in with phone number {phone_number}...")
    token = BREBConsumerAPI().login(phone_number=phone_number)
    click.echo(f"✅ Logged in. Token saved: {token[:12]}...")


@app.command(name="customer-info")
@click.argument("account_number")
@handle_api_error
def customer_info(account_number):
    """Get customer and meter details for an SMS account number."""
    click.echo("👤 Fetching customer information...")
    info = BREBConsumerAPI().customer_info(account_number)
    table = [
        ["Account Number", info["account_number"]],
        ["Name", info["name"]],
        ["Father's Name", info["father_name"]],
        ["Address", info["address"]],
        ["Mobile", info["mobile"]],
        ["PBS", info["pbs"]],
        ["PBS Office", info["pbs_office"]],
        ["Tariff Category", info["tariff_category"]],
        ["Phase", info["phase"]],
        ["Load (kW)", info["load_kw"]],
        ["Meter Number", info["meter_number"]],
    ]
    click.echo("\n📋 Customer Information:")
    click.echo(tabulate(table, tablefmt="simple"))


@app.command(name="bill")
@click.argument("account_number")
@handle_api_error
def bill(account_number):
    """Get the latest bill for an SMS account number."""
    click.echo("💰 Fetching bill...")
    b = BREBConsumerAPI().bill(account_number)
    table = [
        ["Bill Number", b["bill_number"]],
        ["Bill Month", b["bill_month"]],
        ["Used (kWh)", b["used_kwh"]],
        ["Billed Amount", b["billed_amount"]],
        ["Billed Amount + LPC", b["billed_amount_with_lpc"]],
        ["Bill Date", b["bill_date"]],
        ["Last Payment Date", b["last_payment_date"]],
        ["Last Payment Date + LPC", b["last_payment_date_with_lpc"]],
        ["Payment Status", b["payment_status"]],
        ["Payment Channel", b["payment_channel"]],
    ]
    click.echo("\n🧾 Latest Bill:")
    click.echo(tabulate(table, tablefmt="simple"))

    if b["arrears"]:
        arrears = [
            [a.get("BillMonth"), a.get("ReceivableAmount")]
            for a in b["arrears"]
        ]
        click.echo("\n📌 Arrears:")
        click.echo(tabulate(arrears, headers=["Bill Month", "Receivable"], tablefmt="simple"))


if __name__ == "__main__":
    app()
