from flask import Flask, render_template, jsonify, request
# Core folder se functions import kar rahe hain
from core.hardware import get_hardware_status
from core.monitor import start_monitor_mode, stop_monitor_mode
from core.scanner import scan_networks
from core.attacker import launch_attack
from core.cracker import crack_handshake

# 'frontend' folder ko templates aur static dono ke liye use kar rahe hain
app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='')

@app.route('/')
def home():
    return render_template('index.html')

# --- API Routes ---

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
    # URL se interface le sakte hain, default wlan0mon hai
    interface = request.args.get('interface', 'wlan0mon')
    return jsonify(scan_networks(interface=interface))

@app.route('/api/launch_attack')
def launch_attack_api():
    # Attack karne ke liye BSSID aur Channel lazmi hai
    bssid = request.args.get('bssid')
    channel = request.args.get('channel')
    if not bssid or not channel:
        return jsonify({"status": "error", "message": "BSSID and Channel are required."})
    return jsonify(launch_attack(bssid=bssid, channel=channel))

@app.route('/api/crack_password')
def crack_password_api():
    cap_file = request.args.get('cap_file', '/tmp/awb_attack-01.cap')
    return jsonify(crack_handshake(cap_file=cap_file))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)