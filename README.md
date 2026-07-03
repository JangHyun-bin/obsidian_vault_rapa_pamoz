# RAPA 스마트병원 동행 AI 앱 (파모즈) — Vault Home

> 1차년도 (2026.5 ~ 12). 컨소시엄 4개 기관, 본 vault는 **파모즈** 관점의 knowledge base.
> 작성: ㈜파모즈 / JangHyun-bin (narnia0900@gmail.com) / 2026-07-03 v0.1

## 빠른 링크

- 📊 [[Dashboards/Dashboard-Status|Dashboard — Status]] (Linear 임베드)
- 📋 [[WBS/index|WBS Index]] (전체 98 task)
- 🚨 [[WBS/WBS-july|7월 임박 산출물]] (D-day 정렬)
- 🔄 [[WBS/WBS-diff|WBS diff]] (v0.7 10am vs 5pm)
- 📦 [[Deliverables/1.3/README|1.3.x 산출물 v0.1]]
- 🔗 [[Linear-Issues|Linear 이슈 노트]] (manual snapshot)

## 사업 컨텍스트

- 사업: RAPA 2026 AI가상융합 사회기반혁신 — 스마트병원 동행 AI 앱 파일럿
- 컨소시엄: 레몬헬스케어(주관), 파모즈(참여1), 전남대산학(참여2), 전남대병원(수요)
- 마일스톤: 분석/설계 5월~7월 → 개발 7월~11월 → 테스트·홍보 11월~12월

## 컨소시엄 결정 (ADR)

- [[ADR/0001-rag-backbone-bm25-dense|0001 RAG 백본 (BM25 + Dense)]]
- [[ADR/0002-consortium-4-organizations|0002 컨소시엄 4개]]
- [[ADR/0003-positioning-fusion-algorithm|0003 측위 융합 알고리즘 (→ 0009 supersede)]]
- [[ADR/0004-backend-onpremise-hospital|0004 측위 백엔드 온프레미스]]
- [[ADR/0005-phi-routing-dual-llm|0005 PHI 라우팅]]
- [[ADR/0006-qab-gateway-only|0006 EMR 직접연동 X / QAB 경유]]
- [[ADR/0007-sdk-integration-native-internal|0007 SDK 통합 = 내부 Native]]
- [[ADR/0008-lbs-notification-by-lemon|0008 LBS 신고 주체]]
- [[ADR/0009-positioning-ondevice-magnetic-neural-fusion|0009 측위 on-device 자기장+신경]]
- [[ADR/0010-compute-placement-ondevice-first-server-accelerator|0010 컴퓨트 배치]]

## 핵심 스펙

- [[Specs/system-architecture|시스템 아키텍처 v4]]
- [[Specs/indoor-positioning|실내 측위]]
- [[Specs/domain-rag-architecture|Domain RAG v1_minimal]]
- [[Specs/r-and-r|R&R]]
- [[Specs/push-service|Push Service]]
- [[Specs/v0-acceptance-gate|v0 Acceptance Gate]]
- [[Specs/device-support-matrix|디바이스 지원 매트릭스]]
- [[Specs/cold-start-global-localization|콜드스타트]]

## 파모즈 영역 산출물 (1.3.x)

| WBS | 산출물 | 마감 | D-day | 산출 위치 |
|---|---|---|---|---|
| 1.3.1 | 시스템 아키텍처 설계서 | 7/16 | D-13 | [[Deliverables/1.3/01_시스템_구성_설계서_초안]] |
| 1.3.2 | 측위엔진 아키텍처 문서 | 7/15 | D-12 | [[Deliverables/1.3/03_측위엔진_아키텍처_문서_초안]] |
| 1.3.3 | SDK 구성 설계서 | 7/16 | D-13 | [[Deliverables/1.3/04_SDK_구성_설계서_초안]] |
| 1.3.4 | 데이터 흐름·인터페이스 계약서 | 7/21 | D-18 | [[Deliverables/1.3/05_데이터흐름_인터페이스_계약서_초안]] |
| 1.3.5 | 스캔·기준맵 파이프라인 | 7/27 | D-24 | [[Deliverables/1.3/06_스캔_기준맵_파이프라인_초안]] |
| 1.3.6 | 빌드·배포 CI 환경 | 7/24 | D-21 | [[Deliverables/1.3/07_빌드배포_CI_환경_초안]] |

## 의존성 그래프

```
1.3.1 시스템 구성 설계 (컨소 합의, D-13)
    ├─ 1.3.2 측위엔진 아키텍처 (D-12, 파모즈)
    │     └─ 1.3.5 스캔 파이프라인 (D-24)
    ├─ 1.3.3 SDK 구성 설계 (D-13, 파모즈)
    ├─ 1.3.4 데이터 흐름·인터페이스 (D-18, 파모즈)
    └─ 1.3.6 CI 환경 (D-21, 파모즈)
```

## 🔥 즉시 액션 (7/8까지)

1. 1.3.1 v0.1 + Q&A 체크리스트를 컨소시엄에 발송
2. 컨소 코멘트 수합 (7/14까지)
3. v0.2 반영 후 7/16 meeting 합의
4. 1.3.2/1.3.3 v0.1 정합성 확인
