import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "auth-server"))

import mfa_policy
import app

LOG_FILE = "test_results.log"

def log(message):
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def test_mfa_fatigue():
    log("=== TEST 1: MFA Fatigue Attack (Day 2 defense) ===")
    target = "victim_employee"
    blocked = 0
    allowed = 0

    for i in range(10):
        result = mfa_policy.request_login(target)
        if "Too soon" in result or "locked" in result:
            blocked += 1
        else:
            allowed += 1
        log(f"Attempt {i+1}: {result}")
    log(f"Summary: {blocked}/10 blocked, {allowed}/10 push notifications actually sent")
    passed = allowed <= 1
    log(f"TEST 1 RESULT: {'PASSED' if passed else 'FAILED'}\n")
    return passed

def test_token_theft():
    log("=== TEST 2: Stolen Session Token (Day 3 defense) ===")
    token = app.create_session("victim_employee", "192.168.0.10", "laptop-key")
    log(f"Legit session token issued: {token}")

    result = app.verify_session(token, "203.0.113.99", "attacker-device")
    log(f"Attacker tries the stolen token from a different IP/device: {result}")

    passed = "denied" in result
    log(f"TEST 2 RESULT: {'PASSED' if passed else 'FAILED'}\n")
    return passed

if __name__ == "__main__":
    with open(LOG_FILE, "w") as f:
        f.write(f"Integration Test Run - {time.ctime()}\n")
        f.write("=" * 50 + "\n\n")

    results = []
    results.append(("MFA Fatigue Defense (Day 2)", test_mfa_fatigue()))
    results.append(("Stolen Token Defense (Day 3)", test_token_theft()))

    log("=== FINAL SUMMARY ===")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        log(f"{name}: {status}")

    log("\nNote: Envoy Device Posture check (Day 4) was tested manually with")
    log("curl and confirmed working. sedd Day-04.md for that evidence.")
