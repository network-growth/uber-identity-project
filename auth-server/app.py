import random
import string

sessions = {}

def make_token():
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(8))

def create_session(user_id, ip, device_key):
    token = make_token()
    sessions[token] = {
        "user_id": user_id,
        "ip": ip,
        "device_key": device_key,
    }
    return token

def verify_session(token, ip, device_key):
    if token not in sessions:
        return "Invalid token. Access denied."

    session = sessions[token]

    if session["ip"] != ip:
        return "IP mismatch. This token was issued on a different network. Access denied."

    if session["device_key"] != device_key:
        return "Device mismatch. This token was issued on a different device. Access denied."

    return f"Access granted for {session['user_id']}."

if __name__ == "__main__":
    print("--- Scenario 1: Normal login and normal access ---")
    token = create_session("student1", "192.168.0.10", "laptop-key")
    print("Token issued:", token)
    print(verify_session(token, "192.168.0.10", "laptop-key"))

    print("\n--- Scenario 2: Attacker steals the token, uses it from a different IP---")
    print(verify_session(token, "203.0.113.99", "laptop-key"))

    print("\n--- Scenario 3: Attacker steals the token AND the IP, but not the device ---")
    print(verify_session(token, "192.168.0.10", "attacker-key"))

    print("\n--- Scenario 4: Legit user, correct IP and device ---")
    print(verify_session(token, "192.168.0.10", "laptop-key"))
