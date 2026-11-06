"""
build.py — Genera el .exe con PyInstaller.
Corré: py build.py
El .exe queda en dist/AirTransferTool/AirTransferTool.exe
"""

import subprocess
import sys

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onedir",               # carpeta única (portable)
    "--windowed",             # sin consola visible
    "--icon", "icon.ico",
    "--name", "AirTransfer",
    "--add-data", "templates;templates",
    "--add-data", "static;static",
    "--collect-all", "webview",
    "--hidden-import", "hotspot",
    "--hidden-import", "flask",
    "--hidden-import", "jinja2",
    "--hidden-import", "werkzeug",
    "launcher.py"
]

print("Construyendo .exe con PyInstaller y pywebview...")
subprocess.run(cmd, check=True)
print("\nListo. El ejecutable está en: dist/AirTransferTool/AirTransferTool.exe")
