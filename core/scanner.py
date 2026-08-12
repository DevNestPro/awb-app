import subprocess
import os
import time

def scan_networks(interface='wlan0mon', duration=60):
    try:
        temp_file = "/tmp/awb_scan"
        
        if os.path.exists(temp_file + "-01.csv"):
            os.remove(temp_file + "-01.csv")

        proc = subprocess.Popen(['airodump-ng', '-w', temp_file, '--output-format', 'csv', interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(duration)
        proc.terminate()
        proc.wait() # Process ke completely band hone ka wait karo
        time.sleep(2) # File save hone ke liye 2 seconds extra do
        
        csv_file = temp_file + "-01.csv"
        if not os.path.exists(csv_file):
            return {"status": "error", "networks": [], "message": "Scan failed. airodump-ng did not create file. Check if adapter supports scanning."}
            
        networks = []
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == '':
                    break
                parts = line.split(',')
                if len(parts) > 14 and parts[0].strip() != 'BSSID':
                    bssid = parts[0].strip()
                    channel = parts[3].strip()
                    essid = parts[13].strip()
                    if bssid and essid:
                        networks.append({"bssid": bssid, "channel": channel, "essid": essid})
        
        os.remove(csv_file)
        return {"status": "success", "networks": networks}
        
    except Exception as e:
        return {"status": "error", "networks": [], "message": str(e)}