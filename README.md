# Mentox - PlayArea Manager 

A premium, cross-platform application designed for PlayArea businesses to manage digital customer check-ins, wallet top-ups, and point-of-sale functionality securely using QR code scanning capabilities. Built with **Tauri 2 (Desktop Client)**, **Flask (Python Backend API)**, and **Vanilla Javascript/CSS**.

🌍 **Live Web Demo:** [https://aaronschristo.pythonanywhere.com/](https://aaronschristo.pythonanywhere.com/)

---

## 🛠️ System Architecture

Mentox is designed with a decoupled architecture, allowing the frontend to run independently either as a **Desktop Application** or as a **Web Application**, communicating with a centralized **Flask Backend Server**.

1. **`app.py` & `/instance`:** The Python Flask backend API and SQLite Database.
2. **`frontend/`:** Vanilla HTML/CSS/JS containing all pages, styles, and logic.
3. **`src-tauri/`:** The Rust-based environment that wraps the `frontend/` into a native Desktop executable.

---

## 🚀 Setting Up the Backend Server

The backend powers the entire database operations and API for Mentox. You must run this server for the app to work locally.

### 1. Prerequisites
- [Python 3.8+](https://www.python.org/downloads/) installed on your machine.

### 2. Installation Steps
Open your terminal in the `mentox` project directory:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# 3. Install required Python packages
pip install -r requirements.txt
```

### 3. Run the Server
Once dependencies are installed, start the backend API:

```bash
python app.py
```
> The server will start running at **`http://127.0.0.1:5000`**. Wait until it logs that it is active. The backend is now ready!

---

## ⚙️ Configuring the Frontend

The frontend needs to know where to send database requests. By default, it might be pointing to the production cloud server. **You need to point it to your local server.**

1. Open `frontend/js/config.js` in your code editor.
2. Change the `API_BASE` value to point to your local Flask backend:

```javascript
// frontend/js/config.js
window.APP_CONFIG = {
    // For Local Development:
    API_BASE: 'http://127.0.0.1:5000'

    // For Production (Change it back before deployment):
    // API_BASE: 'https://aaronschristo.pythonanywhere.com'
};
```

---

## 💻 Running the Application

You can launch Mentox in either Web Mode or Desktop Mode.

### Option A: Web App Mode (Browser)
Simply open your web browser and navigate to:
**`http://127.0.0.1:5000`**

*Since `app.py` is configured to serve the `frontend/` directory, the website will load seamlessly from your local server.*

### Option B: Tauri Desktop Mode (Native App)
To run Mentox as an actual desktop window using Tauri:

**Requirements:** [Node.js](https://nodejs.org/) and [Rust](https://www.rust-lang.org/tools/install) must be installed.

1. Open a **new** terminal in the `mentox` directory.
2. Keep your Flask server running in the background.
3. Launch the Tauri developer app:
   ```bash
   npx @tauri-apps/cli@2 dev
   ```

*To build a final `.exe` or `.msi` Windows installer for distribution, run:*
```bash
npx @tauri-apps/cli@2 build
```

---

## 📱 Local Network Mobile Testing (QR Scanner)

If you are trying to test the exact QR Code scanner on your phone by connecting to your computer's IP (e.g., `http://192.168.1.5:5000`), mobile browsers will strictly block the camera because the site doesn't have an `https://` SSL certificate.

**How to bypass this for local development on Android:**
1. Open Google Chrome on your Android phone.
2. Navigate to `chrome://flags/#unsafely-treat-insecure-origin-as-secure` in the URL bar.
3. Type your local IP into the text box (e.g., `http://192.168.1.5:5000`).
4. Enable the setting and relaunch the browser. Camera permissions will now pop up correctly!

---

## 📖 Usage Flow
1. **Initialize Settings:** Start by going to **Settings**. Set your Business Name and Check-in Fee.
2. **Issue Customers:** Head to **Customers** to generate QR codes for new profiles.
3. **Recharge Wallets:** Head to **Recharge** to add money to customer accounts.
4. **Scan Passes:** Open **Check-in**, point the camera at a QR code, and watch the system automatically debit their wallet.
5. **Insights:** Track all your revenue through the **Analytics** page. 
