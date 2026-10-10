#!/usr/bin/env python3
"""
BREB Consumer CLI

Command-line interface for the Bangladesh REB / Palli Bidyut consumer API.

The CLI (not the core engine) owns token persistence: `login` saves the bearer
token to ~/.python-breb-api-config, and the other commands read it back. The
core `BREBConsumerAPI` class stays stateless so it can be reused in web apps.
"""

import os
import sys
import functools
import configparser

import click
import requests
from tabulate import tabulate

from .breb import BREBConsumerAPI
from . import __version__

CONFIG_FILE = os.path.expanduser("~/.python-breb-api-config")


def save_token(token):
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"token": token}
    with open(CONFIG_FILE, "w") as fh:
        config.write(fh)


def load_token():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config["DEFAULT"].get("token")
    return None


def client():
    """Build a core client using the saved token (if any)."""
    token = load_token()
    if not token:
        raise click.ClickException("Not logged in. Run `breb-cli login <phone_number>` first.")
    return BREBConsumerAPI(token=token)


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
        except click.ClickException:
            raise
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
    save_token(token)
    click.echo(f"✅ Logged in. Token saved to {CONFIG_FILE}")


@app.command(name="customer-info")
@click.argument("account_number")
@handle_api_error
def customer_info(account_number):
    """Get customer and meter details for an SMS account number."""
    click.echo("👤 Fetching customer information...")
    info = client().customer_info(account_number)
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
    b = client().bill(account_number)
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
        arrears = [[a["bill_month"], a["receivable"]] for a in b["arrears"]]
        click.echo("\n📌 Arrears:")
        click.echo(tabulate(arrears, headers=["Bill Month", "Receivable"], tablefmt="simple"))


if __name__ == "__main__":
    app()
