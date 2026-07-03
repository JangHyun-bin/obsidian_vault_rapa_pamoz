---
type: doc
status: living
last_reviewed: 2026-05-29
---

# Phase A+C Implementation — Deferred Items

본 문서는 2026-05-28 기준 Phase A (인프라) + Phase C (RAG·발행) 구현 완료 후 발견된 spec 대비 deferred 항목을 추적한다. Phase B 콘텐츠 마이그레이션 및 NAS MCP 셋업 완료 (2026-05-29) 후 일부 항목 처리 상태 갱신.

설계 spec: `docs/superpowers/specs/2026-05-28-corpus-design.md`
구현 plan: `docs/superpowers/plans/2026-05-28-corpus-migration.md`
NAS 배포: `docs/superpowers/nas-mcp-deployment.md`

## 우선순위 — 콘텐츠 작업 중 부딪힐 수 있는 것

### 1. ETL 정리 — `_converted/.ledger.json` 추적 정책 ✅ 완료
**처리:** `.gitignore` 에 `_converted/` 전체 추가 (commit `1c20927`). 분류 후 폴더 자체가 삭제되는 워크플로우로 운영.

### 2. ADR 사후수정 감지 (spec §5-6) — 미구현
**spec 약속:** "본문 수정된 status: accepted ADR (pre-commit hook)"
**현재:** check_corpus의 4개 check 중 본문수정 감지 빠짐. ADR accepted 후 본문 수정 금지는 컨벤션만, 자동 강제 없음.
**구현 방법:** git log에서 해당 파일의 첫 status=accepted 커밋을 찾고, 그 이후 본문 변경이 있는지 검사. pre-commit hook에서 staged 파일 중 accepted ADR이 있으면 거부.
**필요 시점:** ADR 8건 확정됐고 supersede 패턴이 자리 잡았으니, 향후 누군가 실수로 옛 ADR을 고치려 할 때 도입.

## 중간 우선순위

### 3. 청크 사이즈 타깃팅 (spec §8-2) — 미구현
**spec 약속:** "한 chunk 800~1200 토큰... 200토큰 overlap"
**현재:** `chunker.chunk_markdown` 이 `target_tokens=1000`, `overlap=200` 파라미터를 받지만 무시. 헤딩 섹션 1개 = chunk 1개.
**영향:** 현 24노트 corpus 에서는 BM25 + Claude 보완으로 검색 품질 OK. 200+ chunks 늘어나면 영향.
**구현 방법:**
- 인접 작은 섹션(< 600 토큰) 묶기
- 큰 섹션(> 1500 토큰) 문단 단위 분할 (코드블록 보존)
- 양 옆 200토큰 overlap

### 4. Citation에 `web_url` 추가 (spec §8-3) — 미구현
**spec 약속:** chunk 메타에 `obsidian_uri` AND `web_url` 둘 다.
**현재:** `obsidian_uri`만. `web_url` 누락. Claude가 답할 때 Quartz 사이트로 가는 링크 없음.
**필요 시점:** 컨소시엄 외부 사용자가 Claude 답변 받기 시작할 때.
**구현 방법:** `build_index.py` 의 chunk 생성부에 `c["web_url"] = f"https://rapa-corpus.pages.dev/{rel.removesuffix('.md')}"`. baseUrl은 env 변수로 빼면 깔끔.

## 낮은 우선순위

### 5. chardet 사용 (spec §6-4) — 미사용
requirements.txt에 핀돼 있지만 어디서도 import 안 함. markitdown이 내부 처리. 한국어 인코딩 사고 나면 wiring.

### 6. `dense_search` O(n²) lookup — 미수정
`serve.py:77` 의 `chunks.index(c)` 는 dense top-k 마다 chunk 리스트를 O(n) 검색.
**현재 영향:** NAS MCP는 BM25-only 모드라 dense_search 사용 안 함. dense 모드 PC에서만 영향.
**고침:** `dense_search` 가 chunks 대신 인덱스 리스트를 반환하도록.

### 7. README 다중 OS 안내 — 부분 완료
README의 setup 가이드가 Windows 위주. `nas-mcp-deployment.md` 가 Linux 환경 자세히 다룸.

### 8. `repository_dispatch` webhook (vault → Corpus-Site 자동) — 미구현
현재는 vault push → Corpus-Site는 수동 트리거. 또 NAS의 RAG 인덱스도 PC가 git push해도 NAS는 git pull + restart 수동.
**고침 2단계:**
- a. vault repo의 GH Action에서 Corpus-Site로 `repository_dispatch` 발송 → Quartz 사이트 자동 빌드
- b. NAS의 git pull + 인덱스 rebuild 자동화 (cron 또는 webhook receiver)

### 9. post-commit 백그라운드 rebuild 로그 — 미수정
빌드 실패시 stderr 가 어디로 가는지 불명확. `scripts/rag/index/.last_build.log` 같은 곳에 리다이렉트.

## NAS 운영 follow-up (2026-05-29 추가)

### 10. Token rotation 자동화 — 운영 절차만 명시 (수동)
`nas-mcp-deployment.md` 의 "Token rotate" 섹션에 안내. 90일 권장. 자동화는 미구현.

### 11. NAS의 vault git pull 자동화 — 수동
NAS에 vault 변경이 자동 반영 안 됨. 옵션:
- a. cron으로 5분마다 `git pull && docker-compose restart rapa-rag-mcp`
- b. GitHub Webhook → NAS의 webhook receiver
**현재 운영:** 사용자가 push 후 NAS SSH로 수동 갱신.

### 12. Tailscale Funnel 보안 강화
Bearer token으로 1차 인증은 적용. 추가 고려:
- HSTS / TLS 인증서 자체는 Tailscale이 관리 (자동 갱신).
- Rate limit 없음. 악성 공격 시 NAS 부담.
- 본격 운영 시 IP 화이트리스트(`tailscale serve` 의 access control) 검토.

### 13. RAG 인덱스 incremental rebuild — 미구현
현재는 컨테이너 재시작 시 인덱스 전체 재빌드. 24노트는 즉시 끝나지만 200+ 늘어나면 비효율.
**고침:** 변경된 .md 파일만 chunking + BM25 partial update.

## 미정 결정 (spec §11 미결 항목)

- **GitHub 레포 위치**: ✅ 결정됨 — `JangHyun-bin/RAPA_Smart_Hospital_AI_Corpus` (vault) + `..._Site` (Quartz)
- **Cloudflare Access 정책**: ✅ 결정 — Quartz 사이트는 Access OFF (현재 public). MCP는 Bearer token으로 보호.
- **Obsidian Sync 사용 여부**: 미정. 모바일 사용 빈도 확인 후.
- **임베딩 모델**: NAS는 BM25 only (Dense 불필요 결정). PC dev에서는 ko-sroberta 그대로.

## 후처리 권장 순서 (2026-05-29 기준)

1. **6번 dense_search O(n²)** — PC dev 작업 시 가끔 영향. 한 번에 고치기 쉬움.
2. **4번 web_url** — Quartz 사이트 활용도 ↑ 시점에 추가.
3. **8b번 NAS git pull 자동화** — vault 자주 수정하기 시작하면 필수. cron 한 줄 추가.
4. **3번 chunker 사이즈** — chunk 개수 100+ 도달 시 손봄.
5. **2번 ADR 사후수정 감지** — 누군가 옛 ADR을 잘못 수정한 사고 발생 시 즉시.
