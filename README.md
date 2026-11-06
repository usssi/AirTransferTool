# AirTransferTool

A lightweight, portable tool to transfer files between your Windows PC and your iPhone over a local Wi-Fi connection powered by Windows Mobile Hotspot.

---

## What Problem It Solves

Removes the friction of transferring photos, videos, and documents between PC and iPhone:
- No USB cables or iTunes required.
- No uploading to third-party clouds or needing an active Internet connection.
- Automatically enables the Windows Mobile Hotspot silently in the background via native WinRT APIs without manual configuration prompts.
- Scan and connect: connects the iPhone via QR and opens the minimalist web interface directly in Safari or any mobile browser.

---

## How to Use (.exe Portable)

1. Open the folder:
   ```
   dist\AirTransferTool\
   ```
2. Double-click `AirTransferTool.exe`:
   - Silently enables the Windows Mobile Hotspot in the background.
   - Launches the native desktop app window (no console window or browser address bars).
3. In the **QR · Connect** tab:
   - Scan the **first QR code** with your iPhone camera to connect to the Wi-Fi network.
   - Scan the **second QR code** to open the web app on your phone.
4. **Upload / Download**:
   - From iPhone: tap to upload files to the server.
   - From PC: click `Move to Downloads` to transfer files directly to your PC's `Downloads` folder.
   - Tap the trash icon to delete files (processed asynchronously via Fetch without insecure form warnings).

*Note:* You can move the entire `dist\AirTransferTool\` folder anywhere (USB drive, Desktop, etc.). The `uploads/` directory is created automatically next to the executable.

---

## Development & Building

```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Run in development mode
py launcher.py

# 3. Build executable
py build.py
```

---

## Architecture

- **`hotspot.py`:** Manages Windows Mobile Hotspot via the native Windows Runtime API (`Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager`) in PowerShell silently without popups. Forces activation and reads configured SSID and password for QR generation.
- **`launcher.py`:** Main entry point. Starts hotspot activation, launches Flask server, and opens the native `pywebview` window.
- **`app.py`:** Flask backend server handling file uploads (`/upload`), downloads (`/download/<filename>`), deletions (`/delete/<filename>`), and previews (`/preview/<filename>`).
- **`templates/index.html`:** Clean, responsive, monochrome UI in English with asynchronous Fetch actions.
- **`static/qrcode.min.js`:** Local QR code generator bundled for offline usage.
