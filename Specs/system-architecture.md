---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[레몬헬스케어]]"
implements: ["[[0004-backend-onpremise-hospital]]", "[[0005-phi-routing-dual-llm]]", "[[0006-qab-gateway-only]]"]
version: v4
tags: [architecture, system, integration]
---

# 스마트병원 AI 시스템 구성도 (v4)

본 사업 전체의 시스템 구성도. 레몬헬스케어 작성, 컨소시엄 협의 진행 중. 측위 백엔드 배치([[0004-backend-onpremise-hospital]]) 및 PHI 라우팅([[0005-phi-routing-dual-llm]]) ADR 들은 본 구성도와 관련된 결정사항.

*원본 아카이브:*
- *[[_raw/스마트병원AI_시스템구성도_v4]] (.pptx 슬라이드)*
- *[[_raw/스마트병원AI_시스템구성도_병원보고용_설명문서_0525]] (병원 보고용 설명문서 0525)*

---

## 1. 구성 개요 (v4 슬라이드 정리)

### Slide 1 — AS-IS

기존 환자용 앱 시스템 구성 (레몬케어 앱 + 병원 EMR/HIS 통신, AI 컴포넌트 부재).

### Slide 2 — AI 기능 호출 시 (안 1)

```
환자 앱 (AI 기능 호출)
    ↓
레몬케어 클라우드 서버
    ↓
Proxy 서버 (Web 서버)
    ↓
레몬케어 API 서버 (QAB)
    ↓
병원 EMR / HIS
```

위치: 네이버 클라우드 — 병원 DMZ — 내부망 계층 구조.

### Slide 3 — AI 기능 호출 시 (안 2)

동일 구조에서 AI 서비스 배치 위치 변화 (안 1 대비). 파모즈 검토안은 [[0005-phi-routing-dual-llm]] 의 이중 LLM + 라우팅을 권장.

### Slide 4 — 위치(측위) 기능 호출 시 (안 1)

환자 앱이 센서 신호를 송신 → 센서·매칭 흐름. 안 1은 레몬 안 (측위 서버 클라우드 배치). 파모즈 검토안 [[0004-backend-onpremise-hospital]] 는 측위 백엔드의 병원 온프레미스/DMZ 배치 권장 (1–5Hz 실시간 + PHI 보호).

### (이후 슬라이드)

데이터 처리 위치 및 보안 관련 흐름. 변환된 원본은 _raw 참조.

## 2. 핵심 합의 사항

| 영역 | 결정 / 제안 | ADR |
|---|---|---|
| 컨소시엄 4개 기관 구성 | accepted | [[0002-consortium-4-organizations]] |
| Domain RAG 백본 | accepted | [[0001-rag-backbone-bm25-dense]] |
| 측위 알고리즘 융합 | accepted | [[0003-positioning-fusion-algorithm]] |
| 측위 백엔드 + GPU 위치 | proposed | [[0004-backend-onpremise-hospital]] |
| PHI 라우팅 (이중 LLM) | proposed | [[0005-phi-routing-dual-llm]] |
| EMR 직접 연동 X / QAB 경유 | proposed | [[0006-qab-gateway-only]] |
| SDK 통합 모델 | proposed | [[0007-sdk-integration-native-internal]] |
| LBS 신고 주체 | accepted | [[0008-lbs-notification-by-lemon]] |

## 3. 통합 포인트

| 포인트 | 인터페이스 |
|---|---|
| 파모즈 SDK ↔ 레몬케어 인증서버 | OAuth2 SSO |
| AI Proactive 안내 ↔ 레몬케어 푸시서버 | [[push-service]] API |
| RAG → EMR 조회 ↔ QAB API 서버 | QAB 경유 |
| 측위 좌표 흐름 ↔ 병원 측위 백엔드 | MQTT/WebSocket (실시간 이벤트) |
| 운영 로그 ↔ 레몬케어 로그/모니터링 | 로그 수집 endpoint 통합 |

## 4. 데이터 처리 위치 (요약)

| 데이터 종류 | 처리 위치 | 보존 정책 |
|---|---|---|
| 환자 식별자 | 레몬 백엔드 (SDK에는 토큰만) | 일회용 토큰 + 비식별 세션 ID 권장 |
| 의료기관 정보 | 레몬 백엔드 → SDK 요청 | 캐시 ≤ 1시간 |
| 측위 좌표 (raw) | **온디바이스만, 휘발** | 미전송 |
| AR 이벤트 | SDK 자체 또는 레몬 분석 | 비식별·집계 |
| 만족도 평가 | RAPA KPI ③ 측정용 | 집계 |
| RAG 질의응답 | 내용에 따라 분기 | [[0005-phi-routing-dual-llm]] 라우팅 |

## 5. 미해결 / 다음 결정 후보

- 'AI 시스템' 박스의 실체 정의 (아젠다 v2 A-2 ★★★) — sLLM 모델 선정 미확정
- QAB API 명세 공유 (A-3 ★★★)
- 측위 시스템 개발 주체 식별 (A-4 ★★★) — 본 ADR/스펙에서는 파모즈로 명시되나 컨소시엄 차원 확정 필요
- 클라우드 GPU 전략 1안/2안 (B-1) — 외부 API 사용 가능 여부 법무 자문
- AI 챗봇 / 측위 채널 분리 (B-2) — 흐름도 별도 작성 합의

## 6. 변경 이력

- 2026-05-14: v4 슬라이드 작성 (FAMOZ 시점 시스템 구성도)
- 2026-05-15: 병원 보고용 설명문서 0515 (`_raw/260518_메일_첨부`의 03번 파일, 본 vault에 미흡수)
- 2026-05-25: 병원 보고용 설명문서 0525 (현 _raw 흡수본)
- 2026-05-29: 본 spec 첫 cut — 8개 ADR 와 link
