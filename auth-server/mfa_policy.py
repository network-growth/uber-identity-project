import time

COOLDOWN_SECONDS = 30
MAX_FAILS = 3

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {"last_time": 0, "fail_count": 0, "locked": False}
    return users[user_id]

def request_login(user_id):
    user = get_user(user_id)

    if user["locked"]:
        return "Account is locked. Try again later."

    now = time.time()
    time_passed = now - user["last_time"]

    if time_passed < COOLDOWN_SECONDS:
        wait = int(COOLDOWN_SECONDS - time_passed)
        return f"Too soon to retry. Wait {wait} more seconds."

    user["last_time"] = now
    return "Login request sent. Please approve on your phone."

def fail_login(user_id):
    user = get_user(user_id)
    user["fail_count"] += 1

    if user["fail_count"] >= MAX_FAILS:
        user["locked"] = True
        return f"Account locked after {MAX_FAILS} failed attempts."

    return f"Login failed ({user['fail_count']}/{MAX_FAILS})"

def success_login(user_id):
    user = get_user(user_id)
    user["fail_count"] = 0
    return "Login success!"

if __name__ == "__main__":
    print("--- Scenario 1: Normal login ---")
    print(request_login("student1"))
    print(success_login("student1"))

    print("\n--- Scenario 2: Attack simulation ---")
    for i in range(3):
        print(f"Request {i+1} ->", request_login("student1"))

    print("\n--- Scenario 3: Account lockout test ---")
    for i in range(3):
        print(f"Attempt {i+1} ->", fail_login("student2"))

    print("\n--- Scenario 4: Retry on locked account ---")
    print(request_login("student2"))


