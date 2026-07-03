---
id: 0005
type: decision
status: proposed
date: 2026-05-14
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: null
related_specs: ["[[domain-rag-architecture]]"]
related_meetings: ["[[2026-05-14-개발협의-아젠다-v2]]"]
tags: [phi, llm, guardrail, routing]
---

# 0005 — PHI 라우팅 = 클라우드 LLM (Non-PHI) + 병원 sLLM (PHI)

## 컨텍스트

환자 질의의 성격에 따라 LLM 추론 위치 및 가드레일 통과 경로가 분기되어야 함. PHI 포함 쿼리의 추론이 병원 내부에서 일어나는지, 클라우드로 송신되는지에 따라 의료법 준수 여부 결정 (아젠다 v2 A-2 "AI 시스템 박스의 실체 정의" 미해결).

## 옵션

- A. **단일 클라우드 LLM** — 모든 쿼리 클라우드 → PHI 외부 송신 발생, 의료법 위험
- B. **단일 병원 sLLM** — 모든 쿼리 병원 내 → 부담 ↑, 비용 ↑
- C. **이중 LLM + 라우팅** — Non-PHI는 클라우드, PHI는 병원 sLLM

## 결정 (proposed)

**C. 이중 LLM 라우팅**:

- **Non-PHI 일반 안내** (의료 상식, 일반 안내) → 클라우드 중앙 LLM 처리
- **PHI-touching 질의** (환자별 처방, EMR 조회 등) → 병원 내부 sLLM 처리
- 라우팅 결정: AI 기능 서버(클라우드)에서 분기

**가드레일 2단 구조**:

- **1단 — 클라우드 입력 가드레일** — PII 1차 필터, 악성 프롬프트 차단
- **2단 — 병원 입력 가드레일** — PHI 검증, 의료 안전성 추가 검증
- **출력 가드레일** — 병원 내부 위치 (Domain RAG 현행 4단 + 출력 1~2단과 동일)

## 근거

- PHI를 클라우드 LLM에 보내면 의료법·개인정보보호법 위반 위험 ([[0008-lbs-notification-by-lemon]] 와 일관된 분석)
- 모든 쿼리를 병원 sLLM 처리시 GPU 부담 ↑, sLLM 의료 답변 품질이 클라우드 GPT/Claude 대비 떨어질 수 있음
- 가드레일 2단으로 라우팅 실패 케이스(잘못 분류된 PHI)에도 안전망

## 결과

- 긍정: PHI 안전 + 일반 질의 품질 ↑
- 부정/리스크:
  - PHI 분기 기준 정의 (Non-PHI vs PHI-touching 경계가 모호한 케이스 처리)
  - sLLM 모델 선정 (Gemma-4-E4B-it 또는 다른 8B~13B급)
  - 라우팅 오분류 시 가드레일 의존 → 가드레일 정합성 정기 평가 필수
- 영향받는 스펙: [[domain-rag-architecture]]

## 변경 이력

- 2026-05-14: 아젠다 v2 B-4 라우팅 정책 + 가드레일 배치 제안
- 2026-05-14: 본 ADR — 이중 LLM + 가드레일 2단 (proposed)
- 미해결: PHI 분기 기준 정의, sLLM 도입 여부 및 모델 선정, 가드레일 단계 합의
