# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client and CLI for the Bangladesh Rural Electrification Board (REB) / Palli Bidyut consumer API. Like the sibling `python-bpdb` project (and unlike `python-nesco`, which scrapes HTML), it talks to a **REST API** and authenticates with a **bearer token**.

Scope is intentionally small: login, customer details, and bill lookup.

## Architecture

### Core Components

**breb/breb.py** — stateless API engine
- `BREBConsumerAPI(token=None)` — pure `requests` REST client, **no file/env I/O**
- Safe to instantiate per-request in FastAPI/Django; the caller owns the token
- **Passwordless bearer-token auth**: `login(phone_number)` returns a Laravel Sanctum token (no OTP, no password) and stores it on `self.token`, but does NOT persist it
- Form fields are sent as multipart (`files={"field": (None, value)}`) to match the mobile app
- The account identifier is the **SMS account number** (10–14 digit string)
- Methods return plain JSON-serializable dicts

**breb/main.py** — CLI layer (owns persistence)
- Click-based CLI using the `@app.command(name="...")` decorator pattern
- **Token persistence lives here, not in the engine**: `login` saves to `~/.python-breb-api-config` (configparser); other commands read it back and pass `token=` into the engine
- `@handle_api_error` decorator catches connection/timeout and generic errors, exits 1
- Entry point: `app()` mapped to `breb-cli` in pyproject.toml
- `tabulate` for formatted output

**breb/__init__.py** — package entry point
- Exports `BREBConsumerAPI`
- Version controlled by GitHub Actions during release (format: `1.{run_number}.0`)

### Auth / Request Flow

1. `login(phone_number)` → bearer token, saved to config file
2. Every data call sends `Authorization: Bearer <token>`
3. `_get_info(account_number)` returns the `data` object with `customer_info` and `billing_info`
4. `customer_info()` and `bill()` project that into clean, snake_case dicts

## Public Methods

- `login(phone_number)` → token (also stored)
- `customer_info(account_number)` → dict: account_number, name, father_name, address, mobile, pbs, pbs_office, tariff_category, phase, load_kw, meter_number
- `bill(account_number)` → dict: bill_number, bill_month, used_kwh, billed_amount, billed_amount_with_lpc, bill_date, last_payment_date, last_payment_date_with_lpc, payment_status, payment_channel, arrears[]

Both `customer_info` and `bill` come from the same upstream call; they just project different parts of the response.

## CLI Commands

```bash
breb-cli login <phone_number>
breb-cli customer-info <account_number>
breb-cli bill <account_number>
```

## Development Commands

```bash
# Install in development mode
pip install -e .

# Build distribution packages
python -m pip install build
python -m build   # -> dist/*.whl and dist/*.tar.gz
```

## Version Management

- Version is defined in `breb/__init__.py` as `__version__ = "1.0.0"`
- GitHub Actions workflow (`.github/workflows/pypi.yml`) auto-updates version on push to main
- Version format: `1.{github.run_number}.0`
- Workflow uses sed: `sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" breb/__init__.py`

## Publishing

Automated via GitHub Actions on push to main:
1. Version number updated automatically
2. Build artifacts created with `python -m build`
3. Published to PyPI using trusted publisher with OIDC token

Manual workflow dispatch also available via GitHub Actions UI.

## Important Notes

- Part of a multi-repository project with sibling repositories: `python-bpdb` and `python-nesco` (similar utility tools for other Bangladesh power companies)
- Login is passwordless by design — a token comes back for any registered phone
- Dependencies: `requests`, `click`, `tabulate` (no `beautifulsoup4`, unlike nesco)
- Keep the README free of raw endpoint/base-URL details — they live in the code only
