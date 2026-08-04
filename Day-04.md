# 4일차 — Envoy Proxy로 Device Posture 검증하기

## 오늘 한 것
지금까지는 "로그인할 때"만 검증했다면, 오늘은 **로그인 이후 요청이 들어올 때마다**
"신뢰할 수 있는 기기에서 온 요청인지"를 검사하는 프록시를 만들었다.
Uber 사고에서는 인증만 통과하면 그 뒤로는 아무 검증 없이 내부망 접근이 허용됐는데,
그 부분을 Envoy Proxy로 막아본 것이다.

요청 헤더에 `x-device-trust: verified`가 없으면 무조건 403으로 차단하고,
있어야만 내부 서비스로 통과시키도록 설정했다.

## 설정 파일 핵심 부분
```yaml
static_resources:
  listeners:
  - name: main_listener
    address:
      socket_address: { address: 0.0.0.0, port_value: 10000 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: local_service
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                  headers:
                  - name: x-device-trust
                    string_match:
                      exact: "verified"
                route:
                  cluster: internal_service
              - match:
                  prefix: "/"
                direct_response:
                  status: 403
                  body:
                    inline_string: "Access denied: device not verified.\n"
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
  - name: internal_service
    connect_timeout: 5s
    type: STATIC
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: internal_service
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address: { address: 127.0.0.1, port_value: 8000 }

admin:
  address:
    socket_address: { address: 0.0.0.0, port_value: 9901 }
```

## 실행 결과

<img width="562" height="98" alt="스크린샷 2026-08-04 115114" src="https://github.com/user-attachments/assets/3205b871-5d72-4de0-a78b-537e5b0b393c" />

<img width="800" height="112" alt="스크린샷 2026-08-04 115148" src="https://github.com/user-attachments/assets/adc2e8ea-5afd-4f7c-a158-a37e0410c941" />

신뢰 헤더 없이 접근하면 차단되고, 헤더가 있어야만 내부 서비스에 접근되는 것을 확인했다.

## 트러블슈팅
YAML 문법 오류를 총 세 번 만났다.
1. `"@type"` 뒤에 콜론(`:`)이 빠져서 파싱 에러
2. `http_connection_manager`를 `http_connection_mananger`로 오타
3. `endpoint`(단수)를 `endpoints`(복수)로 잘못 써서 "unknown fields" 에러

Envoy는 설정 파일에 오타가 있으면 아예 실행이 안 되고 로그에 정확한 줄 번호와
이유를 알려줘서, 로그를 하나씩 읽으면서 디버깅하는 연습이 됐다.

## 다음에 할 것
5일차 — 실제로 MFA Fatigue 공격과 토큰 탈취 공격을 시뮬레이션하는 스크립트 작성
