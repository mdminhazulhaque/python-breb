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
breb-cli customer-info 1010018581900

# Look up the latest bill
breb-cli bill 1010018581900
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
$ breb-cli customer-info 1010018581900
```

**Sample Output:**
```
📋 Customer Information:
Account Number   1010018581900
Name             MD. MINHAZUL HAQUE
Father's Name    ...
Address          Jashore
PBS              Jashore PBS-1
PBS Office       ...
Tariff Category  LT-A
Phase            1
Load (kW)        2
Meter Number     14705612
```

### 🧾 Bill

```bash
$ breb-cli bill 1010018581900
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

```python
from breb import BREBConsumerAPI

client = BREBConsumerAPI()
client.login(phone_number="01XXXXXXXXX")   # token is stored and reused

customer = client.customer_info("1010018581900")
bill = client.bill("1010018581900")

print(customer["name"], customer["meter_number"])
print(bill["billed_amount"], bill["payment_status"])
```

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

This is an unofficial tool. Use at your own discretion. The authors are not responsible for any issues that may arise from using this tool.
