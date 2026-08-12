let scannedNetworks = [];
let attackInterval = null;
let crackInterval = null;

function logToTerminal(message) {
    const terminal = document.getElementById('terminal-output');
    terminal.innerHTML += `<span>root@kali</span>:~# ${message}<br>`;
    terminal.scrollTop = terminal.scrollHeight;
}

function checkHw() {
    logToTerminal("Fetching hardware status...");
    fetch('/api/check_hardware')
    .then(response => response.json())
    .then(data => {
        document.getElementById('hw-mode').innerText = data.mode;
        document.getElementById('hw-iface').innerText = data.interface;
        document.getElementById('hw-dot').className = 'dot ' + data.color;
        logToTerminal(`Hardware Status: ${data.mode} (${data.interface})`);
    });
}

function startMonitor() {
    logToTerminal("Enabling Monitor Mode...");
    fetch('/api/start_monitor').then(res => res.json()).then(data => { logToTerminal(data.message); checkHw(); });
}

function stopMonitor() {
    logToTerminal("Disabling Monitor Mode...");
    fetch('/api/stop_monitor').then(res => res.json()).then(data => { logToTerminal(data.message); checkHw(); });
}

function scanNetworks() {
    logToTerminal("Scanning networks for 20 seconds... Please wait.");
    fetch('/api/scan_networks')
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            scannedNetworks = data.networks;
            const list = document.getElementById('network-list');
            list.innerHTML = '';
            if (scannedNetworks.length === 0) {
                list.innerHTML = '<tr><td colspan="7">No networks found.</td></tr>';
                return;
            }
            scannedNetworks.forEach((net, index) => {
                list.innerHTML += `
                    <tr>
                        <td onclick="showDetails(${index})" style="cursor:pointer; color:#00ff41;">${net.essid}</td>
                        <td>${net.bssid}</td>
                        <td>${net.channel}</td>
                        <td>${net.signal}</td>
                        <td>${net.encryption}</td>
                        <td>${net.clients}</td>
                        <td><button class="action-btn danger" onclick="selectTarget('${net.bssid}', '${net.channel}', '${net.essid}')">SELECT</button></td>
                    </tr>
                `;
            });
            logToTerminal(`Scan complete. Found ${scannedNetworks.length} networks.`);
        } else {
            logToTerminal(`<span style='color:red'>Scan failed: ${data.message}</span>`);
        }
    });
}

function showDetails(index) {
    const net = scannedNetworks[index];
    const modal = document.getElementById('details-modal');
    const content = document.getElementById('modal-content');
    let clientText = net.clients > 0 ? `<span style="color:#00ff41;">${net.clients} device(s) connected.</span> Good target!` : `<span style="color:#ff0000;">No devices connected.</span> Hard to capture handshake.`;
    content.innerHTML = `
        <strong>Wi-Fi Name:</strong> ${net.essid}<br>
        <strong>MAC Address:</strong> ${net.bssid}<br>
        <strong>Channel:</strong> ${net.channel}<br>
        <strong>Signal Strength:</strong> ${net.signal}<br>
        <strong>Security:</strong> ${net.encryption}<br>
        <strong>Connected Devices:</strong> ${clientText}
    `;
    modal.style.display = 'block';
}

function closeModal() { document.getElementById('details-modal').style.display = 'none'; }

// Attack Logic
let targetBSSID = null;
let targetChannel = null;

function selectTarget(bssid, channel, essid) {
    targetBSSID = bssid;
    targetChannel = channel;
    logToTerminal(`Target selected: ${essid} (${bssid}). Now click [05] Start Attack.`);
}

function launchAttack() {
    if(!targetBSSID) { logToTerminal("Error: Please select a target network first."); return; }
    logToTerminal(`Launching Infinite Attack on ${targetBSSID}...`);
    fetch(`/api/launch_attack?bssid=${targetBSSID}&channel=${targetChannel}`)
    .then(res => res.json())
    .then(data => {
        logToTerminal(data.message);
        // Start polling status
        attackInterval = setInterval(checkAttackStatus, 3000);
    });
}

function stopAttack() {
    logToTerminal("Sending STOP signal to attack...");
    fetch('/api/stop_attack')
    .then(res => res.json())
    .then(data => {
        clearInterval(attackInterval);
        logToTerminal("Attack stopped.");
    });
}

function checkAttackStatus() {
    fetch('/api/attack_status')
    .then(res => res.json())
    .then(data => {
        if(!data.running) {
            clearInterval(attackInterval);
            if(data.message.includes("SUCCESS")) {
                logToTerminal(`<span style='color:green'>${data.message} Ready to crack!</span>`);
            } else {
                logToTerminal(`Attack status: ${data.message}`);
            }
        }
    });
}

// Crack Logic
function crackPassword(mode) {
    logToTerminal(`Starting cracking engine (Mode: ${mode})...`);
    fetch(`/api/crack_password?mode=${mode}`)
    .then(res => res.json())
    .then(data => {
        logToTerminal(data.message);
        crackInterval = setInterval(checkCrackStatus, 5000);
    });
}

function stopCrack() {
    logToTerminal("Sending STOP signal to cracking engine...");
    fetch('/api/stop_crack')
    .then(res => res.json())
    .then(data => {
        clearInterval(crackInterval);
        logToTerminal("Cracking paused/stopped.");
    });
}

function checkCrackStatus() {
    fetch('/api/crack_status')
    .then(res => res.json())
    .then(data => {
        if(!data.running) {
            clearInterval(crackInterval);
            if(data.password) {
                logToTerminal(`<span style='color:green; font-size: 16px; font-weight:bold;'>[+] KEY FOUND! Password is: ${data.password}</span>`);
            } else {
                logToTerminal(`Crack status: ${data.message}`);
            }
        } else {
            logToTerminal(`Cracking in progress: ${data.message}`);
        }
    });
}

window.onload = checkHw;