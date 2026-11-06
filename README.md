# AirTransfer

A lightweight, cable-free file transfer tool between your Windows PC and iPhone over a local Wi-Fi hotspot. No iTunes, cables, third-party clouds, or internet connection required.

[![Download Portable Executable](https://img.shields.io/badge/Download-v1.0.0_Portable_(.zip)-blue?style=for-the-badge&logo=windows)](https://github.com/usssi/AirTransferTool/releases/tag/v1.0.0)

👉 **[Download the latest release (v1.0.0)](https://github.com/usssi/AirTransferTool/releases/tag/v1.0.0)**

---

## What Problem It Solves

- **Zero cables:** No Lightning/USB-C cables or iTunes sync hassles.
- **100% Offline:** Transfers stay strictly on your local Wi-Fi network without touching external servers or cloud accounts.
- **Zero setup:** Automatically turns on Windows Mobile Hotspot in the background using native Windows APIs.
- **Scan & Go:** Connect your iPhone and open the web portal instantly via QR codes.

---

## How to Use (Portable .exe)

1. **Download & Extract:**
   Download the [v1.0.0 release zip](https://github.com/usssi/AirTransferTool/releases/tag/v1.0.0) and extract it anywhere on your PC.

2. **Run:**
   Double-click `AirTransfer.exe` (it silently turns on the Wi-Fi hotspot and opens the app window).

3. **Connect iPhone:**
   - Scan the **first QR code** with your iPhone camera to join the Wi-Fi.
   - Scan the **second QR code** to open the transfer portal in Safari.

4. **Transfer:**
   - **From iPhone:** Tap to select and upload photos, videos, or documents.
   - **On PC:** Click `Move to Downloads` on any file to send it straight to your Windows Downloads folder.

---

## Development & Building from Source

```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Run in dev mode
py launcher.py

# 3. Compile portable .exe
py build.py
```

---

## Conceptual Architecture

The app is built around 4 simple, transparent components:

1. **`launcher.py`**: Activates hotspot in background, starts the local Flask server on port 8080, and opens the native desktop window (`pywebview`).
2. **`hotspot.py`**: Uses the official Microsoft Windows SDK (`winsdk`) directly in Python to turn on the mobile hotspot and read the Wi-Fi SSID and password natively without spawning PowerShell or external processes.
3. **`app.py`**: Minimal Flask backend handling file uploads, downloads, and moving files directly into your Windows `Downloads` folder.
4. **`templates/index.html`**: Clean, dark-mode web interface with bundled offline QR generation for camera pairing.
