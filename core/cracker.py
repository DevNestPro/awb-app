import subprocess
import os

def crack_handshake(cap_file, wordlist='/usr/share/wordlists/rockyou.txt'):
    """
    Ye function aircrack-ng chalata hai aur .cap file ko rockyou.txt se match karta hai.
    Agar password mil jaye toh wapas de deta hai.
    """
    if not os.path.exists(cap_file):
        return {"status": "error", "message": "Capture file not found."}
    if not os.path.exists(wordlist):
        return {"status": "error", "message": "Wordlist (rockyou.txt) not found. Please download it."}
        
    try:
        # aircrack-ng -w wordlist cap_file
        result = subprocess.run(['aircrack-ng', '-w', wordlist, cap_file], 
                                capture_output=True, text=True, timeout=300) # 5 minutes timeout
        
        output = result.stdout
        
        # Check if password found
        if "KEY FOUND!" in output:
            # Password extract karna (output string se)
            start = output.find("[") + 1
            end = output.find("]", start)
            password = output[start:end].strip()
            return {"status": "success", "message": "Password Cracked Successfully!", "password": password}
        else:
            return {"status": "error", "message": "Password not found in the dictionary."}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Cracking timed out."}
    except Exception as e:
        return {"status": "error", "message": str(e)}