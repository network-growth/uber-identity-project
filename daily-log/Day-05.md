# 5일차 — 실제로 공격해보기 (`attack-simulation/`)

## 오늘 한 것
2일차 `mfa_policy.py`, 3일차 `app.py`를 다시 짠 게 아니라, `import`로 그대로 가져와서
진짜 공격자처럼 두들겨보는 스크립트 2개를 만들었다. 방어 코드를 재구현하지 않고
실제 코드를 그대로 공격했다는 점에서, 이 방어가 진짜로 작동한다는 걸 증명하는 방식이다.

## 코드

### 01_mfa_fatigue_attack.py — MFA Fatigue 공격
```python
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "auth-server"))

import mfa_policy


TARGET_USER = "victim_employee"
ATTACK_ATTEMPTS = 10


def run_attack():
    print(f"Attacker is spamming login requests for '{TARGET_USER}'...")
    print(f"Sending {ATTACK_ATTEMPTS} requests as fast as possible.\n")

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
    print(f"Push notifications actually sent: {allowed_count}")

    if allowed_count <= 1:
        print("\nDEFENSE WORKED: The attacker could not spam the victim with pushes.")
    else:
        print("\nDEFENSE FAILED: The attacker got through multiple times.")


if __name__ == "__main__":
    run_attack()
```

### 02_stolen_token_access.py — 세션 토큰 탈취
```python
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
```

## 실행 결과

<img width="954" height="385" alt="스크린샷 2026-08-05 120501" src="https://github.com/user-attachments/assets/d629e262-9105-4b70-a6d3-c2b9e6743024" />

<img width="966" height="326" alt="스크린샷 2026-08-05 120553" src="https://github.com/user-attachments/assets/7cf37e4f-4960-4be0-b96f-e9e172190710" />

## 트러블슈팅
`TARGET_USER` 변수명을 `TARGER_USER`로 오타 내서 `NameError` 발생.
파이썬이 제안해준 대로 바로 고쳐서 해결했다.

## 다음에 할 것
6일차 — 지금까지 만든 4개 컴포넌트(mfa_policy, app, envoy, attack-simulation)를
하나의 시나리오로 이어서 통합 테스트하고, 로그를 `test_results.log`에 정리
