# Uber Identity Zero-Trust Hardening

> 2022년 Uber 침해 사고를 분석하고, 그 공격을 실제로 막는 방어 로직을 직접 구현한 프로젝트

학교 보안 수업 발표 과제로 실제 침해 사고 사례를 조사하다가, 2022년 Uber 사고를 접하게 됐다.
공격자가 제로데이가 아니라 **MFA 알림을 스팸처럼 보내는 단순한 방법**만으로 내부망 깊숙이
침투한 걸 보고, 발표로 끝내지 않고 직접 이 공격을 막는 시스템을 만들어보고 싶어서 시작한 프로젝트다.

---

## 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 주제 | Zero-Trust 원칙 기반 Identity & Session Hardening |
| 참고 사고 | 2022년 9월 Uber 침해 사고 (Lapsus$ 계열 위협 행위자) |
| 사용 언어/도구 | Python 3.12, Envoy Proxy, Docker, Bash |
| 실습 환경 | VirtualBox VM · Ubuntu 24.04 LTS · 2 vCPU / 6GB RAM |
| 기간 | 7일 |

## 공격 체인 5단계와 방어 매핑

Uber 사고를 5단계로 분석하고, 그중 3단계에 실제 방어 로직을 구현했다.

| 단계 | 공격 내용 | 방어 컴포넌트 | 결과 |
|---|---|---|---|
| 1. 자격증명 탈취 | 협력업체 계정 유출 | (프로젝트 범위 밖) | - |
| 2. MFA Fatigue | 짧은 간격으로 Push 알림 폭탄 | `auth-server/mfa_policy.py` | ✅ 차단 확인 |
| 3. 계정 접근 성공 | 인증 후 컨텍스트 검증 없음 | `envoy-proxy/envoy.yaml` | ✅ 차단 확인 |
| 4. 세션 토큰 탈취 | 토큰이 발급 환경에 안 묶임 | `auth-server/app.py` | ✅ 차단 확인 |
| 5. 내부 확산 | 암묵적 전면 신뢰 | 통합 테스트로 증명 | ✅ 확인 완료 |

자세한 공격 체인 분석은 [`daily-log/Day-01.md`](./daily-log/Day-01.md) 참고.

## 폴더 구조

```
uber-identity-zero-trust-hardening/
├── daily-log/
│   └── Day-01.md ~ Day-07.md   # 일자별 작업 기록
├── docs/
│   └── 01-uber-attack-analysis.md
├── auth-server/
│   ├── mfa_policy.py           # MFA Fatigue 방어 (쿨다운 + 계정 잠금)
│   └── app.py                  # 세션 토큰 IP/기기 바인딩
├── envoy-proxy/
│   └── envoy.yaml               # Device Posture(신뢰 헤더) 검증
├── attack-simulation/
│   ├── 01_mfa_fatigue_attack.py
│   └── 02_stolen_token_access.py
├── run_integration_test.py      # 전체 방어 로직 통합 테스트
└── test_results.log             # 통합 테스트 실행 로그
```

## 핵심 방어 로직 요약

### 1. MFA Fatigue 방어 (`mfa_policy.py`)
같은 계정에 짧은 간격으로 재요청이 오면 쿨다운으로 차단하고, 연속 실패 시 계정을 잠근다.
실제 테스트에서 공격자가 10번 연속 요청했을 때 9번이 막히고 Push는 1번만 나갔다.

### 2. 세션 토큰 바인딩 (`app.py`)
로그인 성공 시 토큰을 발급 당시의 IP·기기 정보와 함께 저장하고, 이후 요청마다 이 정보가
일치하는지 검증한다. 토큰이 털려도 다른 환경에서는 재사용할 수 없다.

### 3. Device Posture 검증 (`envoy.yaml`)
Envoy Proxy가 모든 요청에 대해 `x-device-trust` 헤더를 확인하고, 신뢰된 기기가 아니면
내부 서비스에 아예 도달하지 못하게 L7 계층에서 차단한다.

## 실행 결과 (통합 테스트)

```
=== FINAL SUMMARY ===
MFA Fatigue Defense (Day 2): PASS
Stolen Token Defense (Day 3): PASS
```

전체 로그는 [`test_results.log`](./test_results.log)에서 확인할 수 있다.

## 일자별 작업 기록

- [Day 1 — 프로젝트 설명 및 공격 체인 분석](./daily-log/Day-01.md)
- [Day 2 — MFA Fatigue 방어 로직](./daily-log/Day-02.md)
- [Day 3 — 세션 토큰 바인딩](./daily-log/Day-03.md)
- [Day 4 — Envoy Device Posture 검증](./daily-log/Day-04.md)
- [Day 5 — 공격 시뮬레이션](./daily-log/Day-05.md)
- [Day 6 — 통합 테스트](./daily-log/Day-06.md)
- [Day 7 — 마무리](./daily-log/Day-07.md)

## 배운 점

- 실제 침해 사고는 대부분 화려한 해킹 기술이 아니라, **"인증 이후를 아무도 검증하지 않는다"**는
  기본적인 설계 허점에서 시작된다는 걸 알게 됐다.
- 방어 로직을 코드로 직접 구현해보니, 개념으로만 알던 Zero-Trust 원칙(명시적 검증, 침해 가정,
  최소 권한)이 실제로 어떤 형태의 코드가 되는지 체감할 수 있었다.
- YAML 설정 파일의 사소한 오타(콜론 누락, 필드명 오타) 하나가 전체 시스템을 멈추게 한다는 걸
  Envoy 실습에서 직접 겪으며, 로그를 읽고 원인을 좁혀가는 디버깅 과정을 연습했다.

## 참고

이 문서는 공개된 사고 분석 자료를 바탕으로 재구성했으며, 특정 개인/조직을 비방할 목적이 없다.
목적은 순수하게 방어 아키텍처를 설계하고 학습하는 것이다.

## 참고

이 문서는 공개된 사고 분석 자료를 바탕으로 재구성했으며, 특정 개인/조직을 비방할 목적이 없다.
목적은 순수하게 방어 아키텍처를 설계하고 학습하는 것이다.
