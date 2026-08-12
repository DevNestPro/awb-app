import subprocess
import os

def launch_attack(bssid, channel, interface='wlan0mon'):
    try:
        clean_channel = str(channel).split(',')[0]
        
        # Bash script ko chalane ki command
        script_path = os.path.join(os.path.dirname(__file__), 'attack.sh')
        command = ['bash', script_path, interface, bssid, clean_channel]
        
        # Script ko 70 seconds ke timeout ke sath chalao
        result = subprocess.run(command, capture_output=True, text=True, timeout=70)
        output = result.stdout.strip()
        
        if "SUCCESS" in output:
            return {"status": "success", "message": "VERIFIED! Handshake captured successfully! Ready to crack."}
        else:
            return {"status": "error", "message": "Attack finished but NO HANDSHAKE captured. Try again."}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Attack timed out."}
    except Exception as e:
        return {"status": "error", "message": str(e)}