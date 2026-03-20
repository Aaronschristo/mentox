# PlayArea Management App

A modern, responsive web application designed for PlayArea businesses to manage digital customer check-ins, top-ups, and point-of-sale functionality using QR code scanning capabilities. Built with Flask, SQLite, and vanilla Javascript.

## Features

- 👤 **Customer Management**: Register new customers with initial balances. 
- 🖨️ **QR Code Issuance**: Generate unique QR codes for new customers, or scan and assign *existing physical QR cards* to new customer accounts on the fly.
- 📸 **Camera Check-ins**: Dedicated scanner kiosk interface powered by `html5-qrcode` to automatically decode customer cards via webcam, deducting the ₹100 flat entry fee.
- 💳 **Wallet Top-up System**: Select customers via name autocomplete, or scan their QR code to directly pull up their profile and recharge their balance with quick pre-filled amounts (₹100, ₹500, ₹1000).
- 📊 **Real-time Dashboard**: Displays total registered customers, total generated check-in revenue, and an audit table of recent transactions.
- 🌙 **Dark Mode**: Comes with a sleek Dark Mode toggle that saves your aesthetic preferences to your browser natively.

## Tech Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy (SQLite3)
- **Frontend**: HTML5, CSS3 Variables (Glassmorphism), Vanilla JavaScript
- **Libraries**:
  - `qrcode[pil]` (Server-side QR generation)
  - `html5-qrcode` (Browser-Side Camera decoder)

## Getting Started

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/)
- Built-in `venv` module

### Installation

1. **Clone the repository** (if applicable) and open a terminal in the project directory:
   ```bash
   cd playarea-app
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Ensure your virtual environment is activated.
2. Start the local Flask development server:
   ```bash
   python app.py
   ```
3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```
   *(The SQLite database `playarea.db` will be initialized automatically on the first request.)*

## Usage Guide

1. Navigate to the **Customers** page to "Issue New QR" or "Assign Existing QR". Download or capture the QR generated.
2. Navigate to **Check-in**, allow your browser to use your camera, and wave the QR code in front of the lens. It will verify the customer and pull their entry fee from their balance.
3. If they run out of money, go to the **Recharge** tab. Type their name to use the autocomplete drop-down, or scan their QR code, enter the top-up amount, and confirm.
