import requests
import json
import time
import random

# Configuration
URL = "http://localhost:8080/api/log"
HEADERS = {"Content-Type": "application/json"}

# Data Pools
SERVICES = ["auth-service", "payment-service", "user-service", "database"]
NORMAL_MESSAGES = [
    "User login successful",
    "Health check passed",
    "Fetched user profile",
    "Transaction completed successfully",
    "Cache refreshed",
    "Index updated"
]
WARNING_MESSAGES = [
    "Query took longer than expected (205ms)",
    "Disk usage at 85%",
    "Rate limit approaching for user 123",
    "Connection pool busy"
]
ATTACK_MESSAGES = [
    "SQL Injection Attempt Detected: SELECT * FROM users WHERE password = OR 1=1; DROP TABLE users; --",
    "Cross-Site Scripting (XSS) attempt: <script>alert('xss')</script> in payload",
    "Unauthorized root access attempt from IP 192.168.1.55",
    "Buffer overflow detected in input handling module at offset 0x4432",
    "Multiple failed login attempts detected (Brute Force) for admin account"
]

def send_log(entry):
    try:
        response = requests.post(URL, headers=HEADERS, data=json.dumps(entry))
        if response.status_code == 200:
            print(f"[SENT] {entry['level']}: {entry['message'][:30]}...")
        else:
            print(f"[FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")

def generate_traffic(count=20, anomaly_ratio=0.1):
    print(f"--- Generating {count} log entries (Anomaly Ratio: {anomaly_ratio}) ---")
    
    for _ in range(count):
        is_anomaly = random.random() < anomaly_ratio
        
        if is_anomaly:
            # Generate Attack/Anomaly
            entry = {
                "service": random.choice(SERVICES),
                "level": random.choice(["ERROR", "CRITICAL"]),
                "message": random.choice(ATTACK_MESSAGES) + " " + "x" * random.randint(50, 200) # Make it long
            }
        else:
            # Generate Normal Traffic
            if random.random() < 0.8:
                # Info
                entry = {
                    "service": random.choice(SERVICES),
                    "level": "INFO",
                    "message": random.choice(NORMAL_MESSAGES)
                }
            else:
                # Warning
                entry = {
                    "service": random.choice(SERVICES),
                    "level": "WARN",
                    "message": random.choice(WARNING_MESSAGES)
                }
        
        send_log(entry)
        time.sleep(0.1) # fast generation

if __name__ == "__main__":
    # Generate a mix of data
    generate_traffic(count=50, anomaly_ratio=0.1)
