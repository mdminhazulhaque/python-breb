# 🔌 BREB Consumer CLI

[![PyPI version](https://badge.fury.io/py/breb.svg)](https://badge.fury.io/py/breb)
[![Python Versions](https://img.shields.io/pypi/pyversions/breb.svg)](https://pypi.org/project/breb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/breb)](https://pepy.tech/project/breb)

A Python client and CLI for the **Bangladesh Rural Electrification Board (REB) / Palli Bidyut** consumer API. Log in with your phone number, then look up customer details and your latest bill directly from your terminal.

## ✨ Features

- 🔐 **Login**: Passwordless login with a phone number — returns and stores a bearer token
- 👤 **Customer Details**: Name, address, PBS office, meter number, tariff, sanctioned load
- 🧾 **Bill**: Latest bill amount, late-payment amount, due dates, payment status, and arrears
- 🚀 **Fast & Lightweight**: Pure `requests` REST client, no browser needed

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install breb
```

### From Source
```bash
git clone https://github.com/mdminhazulhaque/python-breb.git
cd python-breb
pip install -e .
```

## 🚀 Quick Start

After installation, use the `breb-cli` command:

```bash
# Get help
breb-cli --help

# Log in (token is saved to ~/.python-breb-api-config)
breb-cli login 01XXXXXXXXX

# Look up customer details
breb-cli customer-info 10XXXXXXXXXXX

# Look up the latest bill
breb-cli bill 10XXXXXXXXXXX
```

## 📖 Usage

```
Usage: breb-cli [OPTIONS] COMMAND [ARGS]...

  A CLI tool for Bangladesh REB / Palli Bidyut consumer accounts.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  login          Log in with a phone number and save the bearer token
  customer-info  Get customer and meter details for an SMS account number
  bill           Get the latest bill for an SMS account number
```

## 💡 Examples

### 🔐 Login

Login is passwordless — any registered phone number returns a token immediately.
The token is saved locally and reused by subsequent commands.

```bash
$ breb-cli login 01XXXXXXXXX
🔐 Logging in with phone number 01XXXXXXXXX...
✅ Logged in. Token saved: 2098137|KyD...
```

### 👤 Customer Details

```bash
$ breb-cli customer-info 10XXXXXXXXXXX
```

**Sample Output:**
```
📋 Customer Information:
Account Number   10XXXXXXXXXXX
Name             RAHIM UDDIN
Father's Name    KORIM UDDIN
Address          Sadar
PBS              Example PBS-1
PBS Office       Head Office
Tariff Category  Commercial and Office
Phase            Single Phase
Load (kW)        0.65
Meter Number     XXXXXXXX
```

### 🧾 Bill

```bash
$ breb-cli bill 10XXXXXXXXXXX
```

**Sample Output:**
```
🧾 Latest Bill:
Bill Number              ...
Bill Month               2025-01
Used (kWh)               120
Billed Amount            845.00
Billed Amount + LPC      863.00
Bill Date                2025-01-05
Last Payment Date        2025-01-15
Payment Status           Unpaid
Payment Channel          ...

📌 Arrears:
Bill Month      Receivable
------------  ------------
2024-12             845.00
```

## 🐍 Programmatic Use

The core `BREBConsumerAPI` is a **stateless engine** — it never touches the
filesystem, so it drops straight into FastAPI, Django, or any service. You own
the token: get one from `login()`, store it wherever you like, and pass it back
in via the constructor.

```python
from breb import BREBConsumerAPI

# 1. Log in once, persist the token in your own store (DB, Redis, session)
token = BREBConsumerAPI().login(phone_number="01XXXXXXXXX")

# 2. Later / elsewhere, construct a client per request with that token
client = BREBConsumerAPI(token=token)
customer = client.customer_info("10XXXXXXXXXXX")   # -> dict
bill = client.bill("10XXXXXXXXXXX")                 # -> dict

print(customer["name"], customer["meter_number"])
print(bill["billed_amount"], bill["payment_status"])
```

The `breb-cli` command is the one place that persists the token to disk
(`~/.python-breb-api-config`); the engine itself stays stateless, so you can
store the token however you like (DB, Redis, session) and pass it back via
`BREBConsumerAPI(token=...)`.

## 🛠️ Development

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setting up for Development

```bash
git clone https://github.com/mdminhazulhaque/python-breb.git
cd python-breb
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Dependencies

- `requests` - HTTP library for API calls
- `click` - Command line interface framework
- `tabulate` - Pretty-print tabular data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an independent, unofficial tool and is not affiliated with, endorsed by, or connected to the Bangladesh Rural Electrification Board (REB) / Palli Bidyut.

Every piece of information this tool retrieves is **already publicly available** to any consumer through the official customer portal and mobile app. This project does **not** reverse engineer, bypass, or circumvent anything — it simply accesses the same publicly accessible consumer information programmatically and presents it in a convenient format.

Please only look up accounts you are authorized to access. Use at your own discretion; the authors are not responsible for any issues that may arise from using this tool.
