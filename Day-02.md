# 2일차 — MFA Fatigue 공격 막는 코드 짜보기

## 오늘 한 것
1일차에서 분석한 Uber 공격 중 "MFA 알림 여러 번 보내서 지치게 만드는 공격"을
막는 파이썬 코드를 짰다. 핵심 아이디어는 두 가지다.

- **쿨다운**: 한 번 요청하면 30초 안에는 다시 요청 못 하게 막기
- **계정 잠금**: 3번 연속 틀리면 계정을 잠가버리기

## 코드
(auth-server/mfa_policy.py 참고 — 함수 4개로 구성: get_user, request_login, fail_login, success_login)
```python
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
```

## 실행 결과
<img width="778" height="314" alt="스크린샷 2026-07-30 120704" src="https://github.com/user-attachments/assets/9cd7e578-583a-4ac7-80b6-40682ac95af5" />

짧은 간격으로 여러 번 요청해도 쿨다운에 막히고, 3번 틀리면 잠기는 걸 확인했다.

## 트러블슈팅
`request_login` 함수 이름을 `requset_login`으로 오타 내서 `NameError`가 발생했다.
에러 메시지에 파이썬이 "혹시 이거 아니야?(Did you mean...)"라고 제안해준 덕분에 바로 찾아서 고쳤다.

## 다음에 할 것
Number Matching(화면에 뜬 숫자 맞추기) 기능 추가 예정.
