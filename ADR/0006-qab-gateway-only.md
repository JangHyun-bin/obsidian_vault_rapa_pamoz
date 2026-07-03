---
id: 0006
type: decision
status: proposed
date: 2026-05-14
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: null
related_specs: ["[[r-and-r]]"]
related_meetings: ["[[2026-05-14-개발협의-아젠다-v2]]", "[[2026-05-18-스마트병원-AI-회의록]]"]
tags: [emr, integration, qab, security]
---

# 0006 — RAG → EMR/OCS/PACS 직접 연동 없이 QAB API만 경유

## 컨텍스트

QAB(레몬케어 API 서버)는 병원 내부망에서 EMR/OCS/PACS 및 편의시스템과 연결된 통합 API 게이트웨이로 추정됨. 정확한 역할 정의·노출 API 명세는 미공유 (아젠다 v2 A-3, ★★최우선). 파모즈 RAG가 EMR/PACS를 직접 조회하는 구조 vs QAB를 경유하는 구조 결정 필요.

5-18 회의에서 QAB가 측위 데이터베이스와 직접 연결 또는 쿼리 타입으로 연결되는 옵션도 논의됨.

## 옵션

- A. **EMR/OCS/PACS 직접 연동** — 파모즈 RAG가 병원 시스템과 직접 통신
- B. **QAB 경유** — 모든 EMR 데이터 호출은 QAB 통과

## 결정 (proposed)

**B. QAB 경유**:

| 통합 포인트 | 인터페이스 |
|---|---|
| 파모즈 SDK ↔ 레몬케어 인증서버 | OAuth2 SSO 토큰 |
| AI Proactive 안내 ↔ 레몬케어 푸시서버 | 푸시 채널 호출 API |
| **RAG → EMR 조회 ↔ QAB API 서버** | **QAB 경유 (EMR 직접 미연동)** |
| 운영 로그 ↔ 레몬케어 로그/모니터링 | 로그 수집 endpoint 통합 |

## 근거

- **보안 경계 명확** — 파모즈 시스템은 병원 망 직접 접근 안 함
- 파모즈 측 개발 부담 ↓ (EMR/OCS/PACS 각각 직접 연동시 인증·권한 모델 별도)
- QAB의 인증·권한 모델 + Rate Limit 한 곳에서 관리
- 측위 DB는 별개로 처리 (병원 온프레미스, [[0004-backend-onpremise-hospital]])

## 결과

- 긍정: 보안 경계 명확, 인증·권한 단일 지점
- 부정/리스크:
  - QAB API 스펙 미공유 → 본 결정의 전제(QAB가 필요한 API를 제공)가 확인 필요
  - QAB의 외부 시스템(파모즈 RAG/AI 서버) 호출 권한 정책 필요
  - QAB Rate Limit이 환자 150명 동시 측위 부담을 흡수할 수 있는지 사전 산정
- 영향받는 스펙: [[r-and-r]] (백엔드 통합 포인트)
- 미해결: QAB API 명세 공유, 인증 방식 합의, SLA 협의

## 변경 이력

- 2026-05-14: 아젠다 v2 A-3 (QAB 정의 미공유) + D-2 (백엔드 통합 포인트)
- 2026-05-14: 본 ADR — QAB 경유 권장 (proposed)
- 2026-05-18: 회의에서 측위 DB는 QAB와 별도 연결 가능성 논의
