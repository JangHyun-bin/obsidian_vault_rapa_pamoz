---
id: 0001
type: decision
status: accepted
date: 2026-05-13
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: null
related_specs: ["[[domain-rag-architecture]]"]
related_meetings: []
tags: [rag, retrieval, llm]
---

# 0001 — Domain RAG 백본 = BM25 + Dense + Gemma

## 컨텍스트

한국어 의료 RAG 시스템의 백본 retrieval·생성 스택을 선택해야 했음.
요구사항:
- 한국어 의료 도메인 corpus (KCD, ATC, 의료 문서) 정확 검색
- 오프라인/온프레미스 운영 가능 (PHI 보호)
- 가드레일·citation·평가 지원

## 옵션

- A. **Sparse only (BM25)** — 빠르고 가볍지만 의미 검색 약함
- B. **Dense only (sentence-transformers + FAISS)** — 의미 검색 강하나 정확 키워드 매칭 약함
- C. **Hybrid (BM25 + Dense + RRF)** — 양쪽 강점 결합

생성 LLM:
- α. **GPT/Claude API** — 의료 PHI 외부 전송 → 불가
- β. **Gemma-4-E4B-it (4bit)** — 로컬 추론, 약 4B 파라미터, 한국어 OK
- γ. **자체 fine-tuned LLM** — 데이터·시간 부담 큼

## 결정

**Retrieval: C (Hybrid BM25 + Dense + RRF)**
**LLM: β (Gemma-4-E4B-it, bnb 4bit)**

추가 컴포넌트:
- **ExpandedRetriever** — 동의어/온톨로지 확장 (KCD, ATC 코드)
- **Input Guardrail 4단** — PII → emergency → scope → intent
- **Output Guardrail** — dose validator + faithfulness
- **Citation (clinician mode)** — [KCD: x] [ATC: y] 자동 부착

## 근거

- 한국어 의료 corpus는 정확 코드 매칭(BM25)과 의미 매칭(Dense) 둘 다 중요 → Hybrid가 단일 솔루션보다 우수
- Gemma-4-E4B-it는 의료 가이드라인을 비교적 잘 따르고, 4bit 양자화로 단일 GPU에서 운영 가능
- RAGAS 4 메트릭(answer relevancy, faithfulness, context precision, context recall)으로 자체 평가 가능

## 결과

- 긍정: 외부 API 의존성 0, PHI 안전, 평가 가능, 오프라인 운영
- 부정/리스크: 자체 운영 부담 (인덱스 관리·모델 업데이트), GPU 메모리 ≥ 8GB 필요
- 영향받는 스펙: [[domain-rag-architecture]]

## 변경 이력

- 2026-05-13: 본 ADR 작성 (accepted) — Domain RAG v1_minimal Architecture 문서로 명문화
