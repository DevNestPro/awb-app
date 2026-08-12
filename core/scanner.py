import subprocess
import os
import time

def scan_networks(interface='wlan0mon', duration=20):
    try:
        temp_file = "/tmp/awb_scan"
        
        # 1. Pehle koi chalta hua airodump kill karo
        subprocess.run(['pkill', 'airodump-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        
        # Purani files delete karo
        for f in os.listdir('/tmp'):
            if f.startswith('awb_scan'):
                try: os.remove(os.path.join('/tmp', f))
                except: pass

        # 2. airodump-ng start karo
        proc = subprocess.Popen(['airodump-ng', '-w', temp_file, '--output-format', 'csv', '--ignore-negative-one', interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(duration)
        proc.terminate()
        proc.wait()
        time.sleep(2)
        
        csv_file = temp_file + "-01.csv"
        if not os.path.exists(csv_file):
            return {"status": "error", "networks": [], "message": "Scan failed. CSV file not generated."}
            
        networks = {}
        
        # 3. CSV file read karna (Robust Parser)
        with open(csv_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split(',')
                
                # Station section (Devices) shuru ho jaye toh network wali line khatam
                if "Station MAC" in line:
                    break
                    
                # Network wali line check karna
                if len(parts) > 10:
                    bssid = parts[0].strip()
                    if bssid == 'BSSID' or len(bssid) != 17:
                        continue
                    
                    channel = parts[3].strip().split(',')[0]
                    enc = parts[5].strip()
                    pwr = parts[8].strip()
                    essid = parts[13].strip()
                    
                    if bssid and bssid != "00:00:00:00:00:00":
                        if not essid:
                            essid = "Hidden Network"
                        
                        signal_quality = "Weak"
                        if pwr.lstrip('-').isdigit():
                            pwr_val = int(pwr)
                            if pwr_val > -50: signal_quality = "Excellent"
                            elif pwr_val > -65: signal_quality = "Good"
                            elif pwr_val > -75: signal_quality = "Fair"
                        
                        networks[bssid] = {
                            "bssid": bssid, 
                            "channel": channel, 
                            "essid": essid,
                            "pwr": pwr,
                            "signal": signal_quality, 
                            "encryption": enc if enc else "Unknown", 
                            "clients": 0
                        }

        # 4. Devices (Clients) Count Karna - BUG FIXED
        parsing_stations = False
        for line in lines:
            parts = line.split(',') # Yahan split karna bhool gaya tha, ab fix kar diya
            if "Station MAC" in line:
                parsing_stations = True
                continue
            
            if parsing_stations and len(parts) >= 6:
                # Un devices ko count karo jo upar networks mein mojood hain
                station_bssid = parts[5].strip()
                if station_bssid in networks:
                    networks[station_bssid]["clients"] += 1

        # Clean up
        try: os.remove(csv_file)
        except: pass
            
        return {"status": "success", "networks": list(networks.values())}
        
    except Exception as e:
        return {"status": "error", "networks": [], "message": str(e)}