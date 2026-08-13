import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "auth-server"))

import app

VICTIM_IP = "192.168.0.10"
VICTIM_DEVICE = "laptop-key"

ATTACKER_IP = "203.0.113.99"
ATTACKER_DEVICE = "unknown-attacker-device"

def run_attack():
    print("Step 1: The victim logs in normally from their own laptop.")
    token = app.create_session("victim_employee", VICTIM_IP, VICTIM_DEVICE)
    print(f"A session token was issued: {token}\n")

    print("Step 2: The attacker somehow steals this exact token")
    print("(e.g. found in a log file, or leaked in a shared script).\n")

    print("Step 3: The attacker tries to use the stolen token")
    print(f"from their own IP ({ATTACKER_IP}) and device.\n")

    result = app.verify_session(token, ATTACKER_IP, ATTACKER_DEVICE)
    print("Result:", result)

    print("\n--- Attack Summary ---")
    if "denied" in result:
        print("DEFENSE WORKED: The stolen token was rejected because")
        print("the IP and device did not match the original login.")
    else:
        print("DEFENSE FAILED: The stolen token was accepted.")

    print("\nFor comparison, here is the real victim using their own token normally:")
    legit_result = app.verify_session(token, VICTIM_IP, VICTIM_DEVICE)
    print("Result:", legit_result)

if __name__ == "__main__":
    run_attack()
