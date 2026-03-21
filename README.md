# PlayArea Management App

A premium, fully responsive web application designed for PlayArea businesses to manage digital customer check-ins, top-ups, and point-of-sale functionality using QR code scanning capabilities. Built with Flask, SQLite, and vanilla Javascript.

## ✨ Premium Features

- 📱 **Fully Responsive Typography & Layout**: Entire application scales elegantly across desktops, tablets, and mobile phones. Complex data tables magically format themselves into stacked, isolated component cards on small viewports. Navigation menus switch gracefully to off-canvas overlays with dedicated exit mappings.
- 🎨 **State-of-the-Art Aesthetic**: Built using extensive Glassmorphism, dynamic DOM transitions, and mathematical CSS variables. Customer arrays dynamically generate styled programmatic avatars natively.
- 📸 **Advanced Hardware Scanner Pipeline**: Features a custom camera feed engine built dynamically over `html5-qrcode`. Implements explicit permission request delays, device enumeration (camera selection dropdowns), smart unified toggle controls, and gorgeous status overlays (Success rings, Loaders) styled uniformly across all pages. 
- 💳 **Wallet Top-up System**: Select customers via name autocomplete, or scan their QR code to instantly pull up their profile and recharge their balance with quick pre-filled amounts (₹100, ₹500, ₹1000).
- 🌙 **Flawless Dark Mode Persistence**: Engineered to entirely bypass the structural "Flash of Unstyled Content" (FOUC) bug by parsing and executing local viewport settings actively within the document `<head>` DOM allocation. 
- ⚡ **O(log N) Performance & Rendering Pipelines**: Upgraded internal database querying via native SQLite performance indexes mitigating bottleneck scans. Re-engineered dynamic DOM manipulation to strictly bypass `innerHTML` reflows, instead buffering array matrices actively inside detached `DocumentFragment` instances. Exclusively offloaded all DOM transition repaints to hardware-accelerated GPU layers.
- 🗑️ **Cascading Deletions**: Provides a persistent, native backend endpoint and UI hook targeting SQLite relations. Automatically unlinks and clears orphaned transactional logs before explicitly purging users.
- 🔒 **OWASP Network Patches**: Deployed comprehensive global input sanitization (`escapeHTML()`) securely wrapping all user profile mappings. Effectively mitigates arbitrary DOM-based XSS payload scripts traversing the network into client browser environments.

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask, Flask-SQLAlchemy (SQLite3), Waitress (Production WSGI Gateway)
- **Frontend**: HTML5, Vanilla CSS3 (CSS Variables, Flex/Grid matrices, GPU Transforms), Vanilla JavaScript (Fragment Buffers)
- **Libraries**:
  - `qrcode[pil]` (Server-side automatic bitmap QR generation)
  - `html5-qrcode` (Browser-Side Camera feed stream and matrix decoding)

## 🚀 Getting Started

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
   *Note: For deployment, uncomment the active `waitress` block bridging the WSGI interface inside `app.py`*

3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```
   *(The SQLite database `playarea.db` will be initialized automatically on the first request.)*

## 📱 Mobile Camera Testing (Local LAN)

If you are running the development server on your PC (`http://192.168.x.x:5000`) and testing the QR scanner on an Android device, modern mobile browsers will strictly **hardware-block** the `getUserMedia` camera API because it is served over unencrypted HTTP.

**To bypass this for local development testing:**
1. Open Google Chrome on your Android phone.
2. Navigate to `chrome://flags/#unsafely-treat-insecure-origin-as-secure`.
3. Enter your local server URL (e.g., `http://192.168.1.5:5000`) into the text box.
4. Enable the flag and relaunch the browser. Camera permissions will now successfully prompt!

## 📖 Usage Guide

1. Navigate to the **Customers** page to "Issue New QR" or "Assign Existing QR". Download or capture the QR generated.
2. Navigate to **Check-in**, allow your browser to use your camera, and wave the QR code in front of the lens. It will verify the customer and pull their entry fee from their balance.
3. If they run out of money, go to the **Recharge** tab. Type their name to use the autocomplete drop-down, or scan their QR code, enter the top-up amount, and confirm.
