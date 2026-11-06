"""
hotspot.py — Control nativo de la Zona de cobertura móvil de Windows.
Usa la API WinRT (Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager)
a través de PowerShell para:
1. Activar la zona de cobertura móvil automáticamente si está apagada.
2. Obtener el SSID y la contraseña reales configurados en Windows.
"""

import subprocess
import json

PS_HOTSPOT_SCRIPT = """
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}
try {
    $connectionProfile = [Windows.Networking.Connectivity.NetworkInformation, Windows.Networking.Connectivity, ContentType = WindowsRuntime]::GetInternetConnectionProfile()
    if (-not $connectionProfile) {
        throw "No active connection profile"
    }
    $tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager, Windows.Networking.NetworkOperators, ContentType = WindowsRuntime]::CreateFromConnectionProfile($connectionProfile)
    $config = $tetheringManager.GetCurrentAccessPointConfiguration()
    if ($tetheringManager.TetheringOperationalState -ne 'On') {
        Await ($tetheringManager.StartTetheringAsync()) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult]) | Out-Null
    }
    [PSCustomObject]@{
        Ssid = $config.Ssid
        Passphrase = $config.Passphrase
        State = $tetheringManager.TetheringOperationalState.ToString()
    } | ConvertTo-Json -Compress
} catch {
    [PSCustomObject]@{
        Ssid = ""
        Passphrase = ""
        State = "Off"
    } | ConvertTo-Json -Compress
}
"""

def get_hotspot_status_and_activate():
    """
    Enciende la zona de cobertura móvil y devuelve (ssid, passphrase, is_on).
    """
    try:
        proc = subprocess.run(
            [
                "powershell", "-NoProfile", "-NonInteractive",
                "-ExecutionPolicy", "Bypass", "-Command", PS_HOTSPOT_SCRIPT
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        data = json.loads(proc.stdout.strip())
        is_on = data.get("State") == "On"
        return data.get("Ssid", ""), data.get("Passphrase", ""), is_on
    except Exception:
        return "", "", False

