import subprocess
import re

def get_hardware_status():
    try:
        # iwconfig run karne ki koshish
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        output = result.stdout
        
        if "no wireless extensions found" in output.lower() or not output.strip():
            return {"status": "error", "mode": "NO ADAPTER DETECTED", "interface": "None", "color": "red"}
        
        # Interface naam extract karna (jaise wlan0 ya wlan0mon)
        interfaces = re.findall(r'^(\w+)', output, re.MULTILINE)
        if not interfaces:
            return {"status": "error", "mode": "NO ADAPTER DETECTED", "interface": "None", "color": "red"}
            
        interface = interfaces[0]
        
        if "Monitor" in output:
            return {"status": "success", "mode": "MONITOR MODE ACTIVE", "interface": interface, "color": "green"}
        else:
            return {"status": "success", "mode": "MANAGED MODE (ADAPTER FOUND)", "interface": interface, "color": "yellow"}
            
    except Exception as e:
        return {"status": "error", "mode": f"Error: {str(e)}", "interface": "None", "color": "red"}