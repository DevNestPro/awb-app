from flask import Flask, render_template, jsonify, request
from core.hardware import get_hardware_status
from core.monitor import start_monitor_mode, stop_monitor_mode
from core.scanner import scan_networks
import subprocess
import os
import threading

app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='')

# Global variables for background tasks
attack_process = None
crack_process = None
attack_status = {"running": False, "message": "Idle"}
crack_status = {"running": False, "message": "Idle", "password": None}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/check_hardware')
def check_hardware():
    return jsonify(get_hardware_status())

@app.route('/api/start_monitor')
def start_monitor():
    return jsonify(start_monitor_mode())

@app.route('/api/stop_monitor')
def stop_monitor():
    return jsonify(stop_monitor_mode())

@app.route('/api/scan_networks')
def scan_networks_api():
    interface = request.args.get('interface', 'wlan0mon')
    return jsonify(scan_networks(interface=interface))

# --- Attack APIs ---
@app.route('/api/launch_attack')
def launch_attack_api():
    global attack_process, attack_status
    bssid = request.args.get('bssid')
    channel = request.args.get('channel')
    if not bssid or not channel:
        return jsonify({"status": "error", "message": "Missing parameters"})
    
    # Stop existing attack
    if attack_process and attack_process.poll() is None:
        attack_process.terminate()
        
    clean_channel = str(channel).split(',')[0]
    script_path = os.path.join(os.path.dirname(__file__), 'core', 'attack.sh')
    
    attack_status = {"running": True, "message": "Attack running... Waiting for handshake."}
    
    def run_attack():
        global attack_process, attack_status
        attack_process = subprocess.Popen(['bash', script_path, 'wlan0mon', bssid, clean_channel], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = attack_process.communicate()
        out_str = out.decode()
        if "SUCCESS" in out_str:
            attack_status = {"running": False, "message": "SUCCESS! Handshake captured."}
        else:
            attack_status = {"running": False, "message": "Attack Stopped."}

    threading.Thread(target=run_attack).start()
    return jsonify({"status": "started", "message": "Attack started in background."})

@app.route('/api/stop_attack')
def stop_attack():
    global attack_status
    subprocess.run(['pkill', '-f', 'attack.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['pkill', 'airodump-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['pkill', 'aireplay-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    attack_status = {"running": False, "message": "Attack stopped by user."}
    return jsonify({"status": "success"})

@app.route('/api/attack_status')
def get_attack_status():
    return jsonify(attack_status)

# --- Cracking APIs ---
@app.route('/api/crack_password')
def crack_password_api():
    global crack_process, crack_status
    mode = request.args.get('mode', 'start')
    
    if crack_process and crack_process.poll() is None:
        return jsonify({"status": "error", "message": "Cracking already running."})
        
    script_path = os.path.join(os.path.dirname(__file__), 'core', 'crack.sh')
    crack_status = {"running": True, "message": "Cracking started... (rockyou.txt)", "password": None}
    
    def run_crack():
        global crack_process, crack_status
        crack_process = subprocess.Popen(['bash', script_path, mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = crack_process.communicate()
        out_str = out.decode()
        if "KEY FOUND" in out_str:
            # Extract password
            start = out_str.find("[") + 1
            end = out_str.find("]", start)
            pwd = out_str[start:end].strip()
            crack_status = {"running": False, "message": "Password Found!", "password": pwd}
        elif "NO_PASSWORD_FOUND" in out_str:
            crack_status = {"running": False, "message": "Password not in dictionary.", "password": None}
        else:
            crack_status = {"running": False, "message": "Cracking stopped.", "password": None}

    threading.Thread(target=run_crack).start()
    return jsonify({"status": "started", "message": "Cracking started in background."})

@app.route('/api/stop_crack')
def stop_crack():
    global crack_status
    subprocess.run(['pkill', 'aircrack-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['pkill', 'crunch'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    crack_status = {"running": False, "message": "Cracking paused/stopped.", "password": None}
    return jsonify({"status": "success"})

@app.route('/api/crack_status')
def get_crack_status():
    return jsonify(crack_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)