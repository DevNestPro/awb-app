import subprocess
import os
import time

def scan_networks(interface='wlan0mon', duration=20):
    try:
        temp_file = "/tmp/awb_scan"
        
        # Purani files delete karo
        for ext in ["-01.csv", "-01.cap", "-01.kismet.csv", "-01.netxml"]:
            if os.path.exists(temp_file + ext):
                os.remove(temp_file + ext)

        # airodump-ng start karo (20 seconds ke liye)
        proc = subprocess.Popen(['airodump-ng', '-w', temp_file, '--output-format', 'csv', interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(duration)
        proc.terminate()
        proc.wait()
        time.sleep(2)
        
        csv_file = temp_file + "-01.csv"
        if not os.path.exists(csv_file):
            return {"status": "error", "networks": [], "message": "Scan failed."}
            
        networks = {}
        # CSV file read karna
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            parsing_stations = False
            for line in lines:
                parts = line.split(',')
                
                # Agar empty line mile toh stations (devices) section shuru ho gaya
                if len(parts) < 2:
                    parsing_stations = True
                    continue
                    
                if not parsing_stations and len(parts) >= 14:
                    bssid = parts[0].strip()
                    if bssid == 'BSSID' or len(bssid) != 17: continue
                    
                    channel = parts[3].strip().split(',')[0]
                    enc = parts[5].strip()
                    pwr = parts[8].strip()
                    essid = parts[13].strip()
                    
                    if bssid and bssid != "00:00:00:00:00:00":
                        if not essid: essid = "Hidden Network"
                        # PWR ko asaan bana rahe hain (-100 se 0 tak)
                        signal_quality = "Weak"
                        if pwr.isdigit():
                            pwr_val = int(pwr)
                            if pwr_val > -50: signal_quality = "Excellent"
                            elif pwr_val > -65: signal_quality = "Good"
                            elif pwr_val > -75: signal_quality = "Fair"
                        
                        networks[bssid] = {
                            "bssid": bssid, "channel": channel, "essid": essid,
                            "signal": signal_quality, "encryption": enc, "clients": 0
                        }
                        
                elif parsing_stations and len(parts) >= 6:
                    # Devices (Stations) count karna
                    station_bssid = parts[5].strip()
                    if station_bssid in networks:
                        networks[station_bssid]["clients"] += 1

        os.remove(csv_file)
        return {"status": "success", "networks": list(networks.values())}
        
    except Exception as e:
        return {"status": "error", "networks": [], "message": str(e)}