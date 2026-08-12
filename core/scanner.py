import subprocess
import os
import time

def scan_networks(interface='wlan0mon', duration=60):
    try:
        temp_file = "/tmp/awb_scan"
        
        # Purani files delete karo
        for ext in ["-01.csv", "-01.cap"]:
            if os.path.exists(temp_file + ext):
                os.remove(temp_file + ext)

        # airodump-ng start karo
        proc = subprocess.Popen(['airodump-ng', '-w', temp_file, '--output-format', 'csv', interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(duration) # Scan time
        proc.terminate()
        proc.wait()
        time.sleep(2) # File save hone do
        
        csv_file = temp_file + "-01.csv"
        if not os.path.exists(csv_file):
            return {"status": "error", "networks": [], "message": "Scan failed. airodump-ng did not create file."}
            
        networks = []
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(',')
                # Agar line valid hai aur station section nahi hai
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    # Header aur Stations ko skip karo
                    if bssid == 'BSSID' or bssid == 'Station MAC':
                        continue
                    
                    channel = parts[3].strip()
                    essid = parts[13].strip()
                    
                    # Sirf valid BSSID wale networks add karo
                    if bssid and len(bssid) == 17 and bssid != "00:00:00:00:00:00":
                        if not essid:
                            essid = "Hidden Network"
                        networks.append({"bssid": bssid, "channel": channel, "essid": essid})
        
        # Clean up
        try:
            os.remove(csv_file)
        except:
            pass
            
        return {"status": "success", "networks": networks}
        
    except Exception as e:
        return {"status": "error", "networks": [], "message": str(e)}