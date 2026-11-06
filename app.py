"""
AirTransferTool - Servidor Flask
"""

import os
import sys
import shutil
import socket
import subprocess
from pathlib import Path
from flask import (
    Flask, render_template, request, send_file,
    redirect, url_for, jsonify
)

if getattr(sys, 'frozen', False):
    bundle_dir = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
    template_folder = os.path.join(bundle_dir, 'templates')
    static_folder = os.path.join(bundle_dir, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

# ---------------------------------------------------------------------------
# Directorios
# ---------------------------------------------------------------------------

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def get_uploads_dir():
    d = get_base_dir() / "uploads"
    d.mkdir(exist_ok=True)
    return d

def get_downloads_dir():
    return Path.home() / "Downloads"

# ---------------------------------------------------------------------------
# IP del hotspot
# ---------------------------------------------------------------------------

def get_hotspot_ip():
    """
    La Zona de cobertura móvil de Windows siempre usa 192.168.137.1.
    Verificamos que esté asignada; si no, fallback a IP local.
    """
    HOTSPOT_IP = "192.168.137.1"
    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if HOTSPOT_IP in result.stdout:
            return HOTSPOT_IP
    except Exception:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

from hotspot import get_hotspot_status_and_activate

HOTSPOT_INFO = {"ssid": "", "password": "", "is_on": False}

def refresh_hotspot_info():
    ssid, pwd, is_on = get_hotspot_status_and_activate()
    HOTSPOT_INFO["ssid"] = ssid
    HOTSPOT_INFO["password"] = pwd
    HOTSPOT_INFO["is_on"] = is_on

# ---------------------------------------------------------------------------
# Detección de dispositivo
# ---------------------------------------------------------------------------

def is_mobile(req):
    ua = req.headers.get("User-Agent", "").lower()
    return any(k in ua for k in ["iphone", "android", "mobile", "ipad"])

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

def get_files_data():
    uploads = get_uploads_dir()
    files = []
    for f in sorted(uploads.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file():
            size = f.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/1024/1024:.1f} MB"
            files.append({
                "name": f.name,
                "size": size,
                "size_str": size_str,
                "ext": f.suffix.lower().lstrip(".")
            })
    return files

@app.route("/")
def index():
    files = get_files_data()
    hotspot_ip = get_hotspot_ip()
    app_url = f"http://{hotspot_ip}:8080"
    ssid = HOTSPOT_INFO.get("ssid", "")
    password = HOTSPOT_INFO.get("password", "")
    wifi_qr = f"WIFI:T:WPA;S:{ssid};P:{password};;" if ssid else ""
    hotspot_on = HOTSPOT_INFO.get("is_on", False)
    mobile = is_mobile(request)

    return render_template(
        "index.html",
        files=files,
        app_url=app_url,
        wifi_qr=wifi_qr,
        ssid=ssid,
        hotspot_on=hotspot_on,
        mobile=mobile
    )

@app.route("/api/files")
def api_files():
    return jsonify({"files": get_files_data()})

@app.route("/upload", methods=["POST"])
def upload():
    uploaded = request.files.getlist("files")
    for f in uploaded:
        if f.filename:
            dest = get_uploads_dir() / f.filename
            f.save(dest)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
        return jsonify({"ok": True})
    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download(filename):
    uploads = get_uploads_dir()
    src = uploads / filename
    if not src.exists():
        return "File not found", 404
    if not str(src.resolve()).startswith(str(uploads.resolve())):
        return "Access denied", 403

    if not is_mobile(request):
        dest = get_downloads_dir() / filename
        shutil.move(str(src.resolve()), dest)
        return redirect(url_for("index"))
    else:
        return send_file(str(src.resolve()), as_attachment=True, download_name=filename)

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    uploads = get_uploads_dir()
    target = uploads / filename
    if target.exists() and str(target.resolve()).startswith(str(uploads.resolve())):
        target.unlink()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
        return jsonify({"ok": True})
    return redirect(url_for("index"))

@app.route("/delete-all", methods=["POST"])
def delete_all():
    uploads = get_uploads_dir()
    for f in uploads.iterdir():
        if f.is_file():
            try:
                f.unlink()
            except Exception:
                pass
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
        return jsonify({"ok": True})
    return redirect(url_for("index"))

@app.route("/open-folder", methods=["POST"])
def open_folder():
    uploads = get_uploads_dir()
    try:
        if sys.platform == "win32":
            os.startfile(str(uploads.resolve()))
        else:
            subprocess.run(["xdg-open", str(uploads.resolve())], check=False)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify({"ok": True})

@app.route("/preview/<filename>")
def preview(filename):
    uploads = get_uploads_dir()
    src = uploads / filename
    if not src.exists():
        return "File not found", 404
    if not str(src.resolve()).startswith(str(uploads.resolve())):
        return "Access denied", 403
    return send_file(str(src.resolve()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
