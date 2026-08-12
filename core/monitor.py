import subprocess

def start_monitor_mode():
    try:
        subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)
        subprocess.run(['airmon-ng', 'start', 'wlan0'], capture_output=True)
        return {"status": "success", "message": "Monitor mode enabled successfully. Interface changed to wlan0mon."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to start monitor mode: {str(e)}"}

def stop_monitor_mode():
    try:
        subprocess.run(['airmon-ng', 'stop', 'wlan0mon'], capture_output=True)
        subprocess.run(['systemctl', 'start', 'NetworkManager'], capture_output=True)
        return {"status": "success", "message": "Monitor mode disabled. Managed mode restored."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to stop monitor mode: {str(e)}"}