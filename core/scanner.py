import subprocess
import os
import time

def scan_networks(interface='wlan0mon', duration=15):
    """
    Ye function airodump-ng chalata hai aur aas paas ke Wi-Fi networks ki
    list (BSSID, Channel, ESSID) nikal kar deta hai.
    """
    try:
        # Temp file ka setup
        temp_file = "/tmp/awb_scan"
        
        # Pehle se koi purani file ho toh delete karo
        if os.path.exists(temp_file + "-01.csv"):
            os.remove(temp_file + "-01.csv")

        # airodump-ng ko background mein 'duration' seconds ke liye chalayen
        # -w se file mein output save hoga, --output-format csv se CSV format mein
        proc = subprocess.Popen(['airodump-ng', '-w', temp_file, '--output-format', 'csv', interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(duration) # Scan ko 15 seconds tak chalne do
        proc.terminate()     # Scan stop karo
        
        # CSV file read karna
        csv_file = temp_file + "-01.csv"
        if not os.path.exists(csv_file):
            return {"status": "error", "networks": [], "message": "Scan failed. No file generated."}
            
        networks = []
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() == '':
                    break # Station section shuru ho gaya, networks khatam
                parts = line.split(',')
                if len(parts) > 14 and parts[0].strip() != 'BSSID':
                    bssid = parts[0].strip()
                    channel = parts[3].strip()
                    essid = parts[13].strip()
                    if bssid and essid:
                        networks.append({"bssid": bssid, "channel": channel, "essid": essid})
        
        # Temp file clean karo
        os.remove(csv_file)
        return {"status": "success", "networks": networks}
        
    except Exception as e:
        return {"status": "error", "networks": [], "message": str(e)}