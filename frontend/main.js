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
    })
    .catch(error => logToTerminal("<span style='color:red'>Error connecting to backend.</span>"));
}

function startMonitor() {
    logToTerminal("Enabling Monitor Mode... (This takes a few seconds)");
    fetch('/api/start_monitor')
    .then(response => response.json())
    .then(data => {
        logToTerminal(data.message);
        checkHw(); // Auto-refresh status
    });
}

function stopMonitor() {
    logToTerminal("Disabling Monitor Mode...");
    fetch('/api/stop_monitor')
    .then(response => response.json())
    .then(data => {
        logToTerminal(data.message);
        checkHw(); // Auto-refresh status
    });
}

function scanNetworks() {
    logToTerminal("Scanning networks for 60 seconds... Please wait.");
    fetch('/api/scan_networks')
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            const list = document.getElementById('network-list');
            list.innerHTML = ''; // Clear old list
            
            if (data.networks.length === 0) {
                list.innerHTML = '<tr><td colspan="4" style="text-align: center;">No networks found.</td></tr>';
                logToTerminal("Scan complete. No networks found.");
                return;
            }

            // Add networks to table
            data.networks.forEach(net => {
                list.innerHTML += `
                    <tr>
                        <td>${net.essid}</td>
                        <td>${net.bssid}</td>
                        <td>${net.channel}</td>
                        <td><button class="action-btn danger" onclick="launchAttack('${net.bssid}', '${net.channel}', '${net.essid}')">ATTACK</button></td>
                    </tr>
                `;
            });
            logToTerminal(`Scan complete. Found ${data.networks.length} networks.`);
        } else {
            logToTerminal(`<span style='color:red'>Scan failed: ${data.message}</span>`);
        }
    });
}

function launchAttack(bssid, channel, essid) {
    logToTerminal(`Targeting ${essid} (${bssid}) on Channel ${channel}...`);
    logToTerminal("Launching Deauth Attack & Capturing Handshake (60s)...");
    
    // URL encode the parameters
    const url = `/api/launch_attack?bssid=${encodeURIComponent(bssid)}&channel=${encodeURIComponent(channel)}`;
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            logToTerminal(`<span style='color:green'>SUCCESS: ${data.message}</span>`);
            logToTerminal("Handshake file saved. You can now click [05] Crack Captured Handshake.");
        } else {
            logToTerminal(`<span style='color:red'>ERROR: ${data.message}</span>`);
        }
    });
}

function crackPassword() {
    logToTerminal("Starting cracking engine using rockyou.txt...");
    logToTerminal("This may take a few minutes depending on password complexity.");
    
    fetch('/api/crack_password')
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            logToTerminal(`<span style='color:green; font-size: 16px; font-weight:bold;'>[+] KEY FOUND! Password is: ${data.password}</span>`);
        } else {
            logToTerminal(`<span style='color:red'>[-] ${data.message}</span>`);
        }
    });
}

// Auto check hardware on page load
window.onload = checkHw;