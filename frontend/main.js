let scannedNetworks = []; // Scan kiye gaye networks ko save karne ke liye

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
    .then(data => { logToTerminal(data.message); checkHw(); });
}

function stopMonitor() {
    logToTerminal("Disabling Monitor Mode...");
    fetch('/api/stop_monitor')
    .then(response => response.json())
    .then(data => { logToTerminal(data.message); checkHw(); });
}

function scanNetworks() {
    logToTerminal("Scanning networks for 20 seconds... Please wait.");
    fetch('/api/scan_networks')
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            scannedNetworks = data.networks; // Networks ko save kar liya
            const list = document.getElementById('network-list');
            list.innerHTML = '';
            
            if (scannedNetworks.length === 0) {
                list.innerHTML = '<tr><td colspan="7" style="text-align: center;">No networks found.</td></tr>';
                logToTerminal("Scan complete. No networks found.");
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
                        <td><button class="action-btn danger" onclick="launchAttack('${net.bssid}', '${net.channel}', '${net.essid}')">ATTACK</button></td>
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
    
    // Asaan alfazon mein details
    let clientText = net.clients > 0 ? `<span style="color:#00ff41;">${net.clients} device(s) are connected.</span> Good target for attack!` : `<span style="color:#ff0000;">No devices connected.</span> Handshake will be hard to capture.`;
    
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

function closeModal() {
    document.getElementById('details-modal').style.display = 'none';
}

function launchAttack(bssid, channel, essid) {
    logToTerminal(`Targeting ${essid} (${bssid}) on Channel ${channel}...`);
    logToTerminal("Launching Burst Deauth Attack. Capturing Handshake (Max 70s)...");
    
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

window.onload = checkHw;