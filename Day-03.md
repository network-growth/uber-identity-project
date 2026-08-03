# 3일차 — 훔친 세션 토큰이 못 쓰이게 막기 (`app.py`)

## 오늘 한 것
Uber 사고에서 공격자가 훔친 세션 토큰을 아무 곳에서나 재사용할 수 있었던 문제를 막아봤다.
토큰을 발급할 때 "어느 IP, 어떤 기기에서 로그인했는지"를 같이 저장해두고,
나중에 그 토큰으로 접근할 때 IP·기기 정보가 다르면 차단하는 방식이다.
(실제로는 DPoP이라는 암호학적 방식을 쓰지만, 오늘은 그 핵심 아이디어만 단순화해서 구현했다.)

## 코드
```python
import random
import string

# This dictionary stores all active sessions.
# Example: {"abc123": {"user_id": "student1", "ip": "1.1.1.1", "device_key": "laptop-key"}}
sessions = {}


def make_token():
    # Create a random 8-character token, like a real session ID.
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(8))


def create_session(user_id, ip, device_key):
    # Called when a user successfully logs in.
    # The token gets locked to the IP and device_key it was created with.
    token = make_token()
    sessions[token] = {
        "user_id": user_id,
        "ip": ip,
        "device_key": device_key,
    }
    return token


def verify_session(token, ip, device_key):
    # Called every time a request comes in with a token.
    # We check that the IP and device_key MATCH what was used at login time.
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

    print("\n--- Scenario 2: Attacker steals the token, uses it from a different IP ---")
    print(verify_session(token, "203.0.113.99", "laptop-key"))

    print("\n--- Scenario 3: Attacker steals the token AND the IP, but not the device ---")
    print(verify_session(token, "192.168.0.10", "attacker-key"))

    print("\n--- Scenario 4: Legit user, correct IP and device ---")
    print(verify_session(token, "192.168.0.10", "laptop-key"))
```

## 실행 결과

<img width="720" height="287" alt="스크린샷 2026-08-03 152005" src="https://github.com/user-attachments/assets/8766ab31-908a-454b-99cc-cfb7c89de3e5" />

## 트러블슈팅
- 딕셔너리 항목 사이에 쉼표(`,`)를 빼먹어서 `SyntaxError` 발생 → 추가해서 해결
- `string.digits`를 `strings.digits`로 오타 내서 `NameError` 발생 → 파이썬이 제안해준 대로 고쳐서 해결

## 다음에 할 것
4일차 — Envoy Proxy에서 Device Posture 검증 붙이기
