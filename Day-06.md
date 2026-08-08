# 6일차 — 통합 테스트 (`run_integration_test.py`)

## 오늘 한 것
2일차·3일차에 만든 방어 코드를 다시 짜지 않고 그대로 가져와서,
하나의 스크립트로 이어붙여 순서대로 테스트하고 결과를 `test_results.log`에 자동 저장했다.

## 코드
```python
# run_integration_test.py
# This script runs ALL the defenses built on Day 2-5 together, one after
# another, and writes everything into test_results.log so we have proof
# that the whole attack chain gets blocked.

import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "auth-server"))

import mfa_policy
import app


LOG_FILE = "test_results.log"


def log(message):
    # Print to screen AND save to the log file at the same time.
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
    # Start the log file fresh every time we run this.
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
    log("curl and confirmed working. See Day-04.md for that evidence.")
```

## 실행 결과

<img width="1287" height="459" alt="스크린샷 2026-08-08 200509" src="https://github.com/user-attachments/assets/f748cd52-ca2e-4c30-bb15-55997ce84c87" />


## 트러블슈팅
- `os.path.dirname`을 `dirame`으로 오타 내서 `AttributeError` 발생 → 파이썬이 제안해준 대로 수정
- `test_mfa_fatigue()` 함수에서 요약 출력과 `return passed` 부분을 통째로 빠뜨려서,
  테스트는 실제로 통과했는데도 최종 요약에 `FAIL`로 잘못 표시됨.
  에러 메시지 없이 조용히 틀린 결과가 나온 경우라 원인 찾는 데 시간이 좀 걸렸다.

## 다음에 할 것
7일차 — README.md 작성 및 GitHub 최종 커밋
