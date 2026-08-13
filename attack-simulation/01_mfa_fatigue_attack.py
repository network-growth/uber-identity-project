import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "auth-server"))

import mfa_policy

TARGET_USER = "victim_employee"
ATTACK_ATTEMPTS = 10

def run_attack():
    print(f"Attacker is spamming login requests for '{TARGET_USER}'...")
    print(f"Sending {ATTACK_ATTEMPTS} requsts as fast as possible.\n")

    blocked_count = 0
    allowed_count = 0

    for i in range(ATTACK_ATTEMPTS):
        result = mfa_policy.request_login(TARGET_USER)
        is_blocked = "Too soon" in result or "locked" in result

        if is_blocked:
            blocked_count += 1
        else:
            allowed_count += 1

        print(f"Attempt {i+1}: {result}")

    print("\n--- Attack Summary ---")
    print(f"Total requests sent: {ATTACK_ATTEMPTS}")
    print(f"Blocked by cooldown/lockout: {blocked_count}")
    print(f"Push notifictations actually sent: {allowed_count}")

    if allowed_count <= 1:
        print("\nDEFENSE WORKED: The attacker could not spam the victim with pushed.")
    else:
        print("\nDEFENSE FAILED: The attacker got through multiple times.")

if __name__  == "__main__":
    run_attack()
