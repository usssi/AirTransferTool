"""
launcher.py — Punto de entrada de AirTransferTool.
1. Fuerza la activación de la Zona de cobertura móvil mediante la API WinRT.
2. Lanza el servidor Flask en un hilo separado.
3. Abre la interfaz en una ventana nativa pywebview (sin consola ni barras de navegador).
"""

import sys
import threading
import time
import socket
from pathlib import Path
import webview
from app import refresh_hotspot_info

def start_flask():
    """Lanza el servidor Flask en un hilo daemon."""
    from app import app
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

def wait_for_server(timeout=10):
    """Espera a que Flask esté escuchando antes de abrir la ventana."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", 8080), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False

def main():
    # 1. Fuerza la activación de la zona WiFi y obtiene credenciales en background
    threading.Thread(target=refresh_hotspot_info, daemon=True).start()

    # 2. Lanza Flask en background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # 3. Espera a que el servidor Flask esté listo
    wait_for_server()

    # 4. Abre la ventana nativa con pywebview y el icono personalizado
    base_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    icon_candidate = base_dir / "static" / "icon.ico"
    if not icon_candidate.exists():
        icon_candidate = Path(__file__).parent / "icon.ico"
    icon_arg = str(icon_candidate.resolve()) if icon_candidate.exists() else None

    webview.create_window(
        title="AirTransfer",
        url="http://localhost:8080",
        width=960,
        height=680,
        min_size=(640, 480),
        resizable=True,
        text_select=False,
    )
    webview.start(debug=False, icon=icon_arg)

if __name__ == "__main__":
    main()
