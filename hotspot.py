"""
hotspot.py — Control nativo de la Zona de cobertura móvil de Windows.
Usa la API oficial de Windows SDK (winsdk) directamente en Python:
1. Activa la zona de cobertura móvil si está apagada.
2. Lee el SSID y la contraseña reales configurados en Windows.
Sin procesos externos, sin PowerShell y sin comandos que activen alertas de antivirus.
"""

import asyncio

async def _activate_hotspot_async():
    try:
        import winsdk.windows.networking.connectivity as conn
        import winsdk.windows.networking.networkoperators as tether

        profile = conn.NetworkInformation.get_internet_connection_profile()
        if not profile:
            return "", "", False

        mgr = tether.NetworkOperatorTetheringManager.create_from_connection_profile(profile)
        if mgr.tethering_operational_state != tether.TetheringOperationalState.ON:
            await mgr.start_tethering_async()

        config = mgr.get_current_access_point_configuration()
        is_on = (mgr.tethering_operational_state == tether.TetheringOperationalState.ON)
        return config.ssid or "", config.passphrase or "", is_on
    except Exception:
        return "", "", False

def get_hotspot_status_and_activate():
    """
    Enciende la zona de cobertura móvil y devuelve (ssid, passphrase, is_on).
    """
    try:
        return asyncio.run(_activate_hotspot_async())
    except Exception:
        return "", "", False
