---
type: doc
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
---

# P.RAPA Corpus

스마트병원 AI 사업의 **단일 진실 공급원(SSoT)**.
시간에 따라 진화하는 결정사항·스펙·회의록·도메인 지식을 한 곳에 모아 정합성을 유지하고,
**사람 / 정적 사이트 / LLM** 셋 다 같은 source를 본다.

---

## 🚀 운영 상태

| 채널 | 상태 | 어디서 |
|---|---|---|
| **Obsidian 편집** | ✅ 가동 | `D:\HB\P.RAPA_DEV\Docs\Corpus` (이 폴더를 Vault로 열기) |
| **정적 사이트** | ✅ 가동 | https://rapa-corpus.pages.dev (Cloudflare Pages + Quartz) |
| **MCP RAG 서버** | ✅ 가동 | NAS Docker (Tailscale Funnel 외부 노출) |
| **자동 빌드/배포** | ✅ 가동 | git push → check_corpus → Quartz build → Cloudflare Pages |
| **자동 인덱스 rebuild** | ✅ 가동 | post-commit hook (vault 변경 시 RAG 인덱스 자동 갱신) |

### LLM 사용 — Claude Code/Desktop 에서

MCP 서버 등록되어 있어 채팅에 *자연어로 질문*만 하면 자동으로 corpus 검색.

예시:
```
나: 측위 백엔드는 어디 배치하기로 했지?

Claude: (rapa-corpus 도구 자동 호출 → corpus 검색)
        병원 온프레미스/DMZ 배치 제안됨 (proposed, 0004 ADR).
        근거: decisions/0004-backend-onpremise-hospital
              meetings/2026-05-18-스마트병원-AI-회의록
```

도구 목록:
- `ask(question, top_k)` — corpus 검색, 출처 chunk 반환
- `list_decisions()` — ADR 전체 목록 (status·date 순)

### Claude Code 에 MCP 등록 (PC, 1분)

PowerShell 또는 bash:

```bash
# 1. Bearer token 받기 — NAS .env 에서 (NAS 운영자에게 요청 또는 본인 NAS면 SSH로 확인)
#    cat /volume1/docker/rapa-corpus/scripts/.env  → RAPA_MCP_TOKEN=<값>

# 2. MCP 서버 등록
claude mcp add --transport sse rapa-corpus \
  https://famoz-nas.taile998dc.ts.net/sse \
  --header "Authorization: Bearer <TOKEN>"

# 3. 확인
claude mcp list
# rapa-corpus 가 보이면 OK

# 4. Claude Code 재시작 (현 세션 종료 후 새로 실행)
```

이후 채팅에 자연어 질문 → 자동으로 corpus 검색.

> **Claude.ai (웹) / Claude Desktop 의 custom connector 는 OAuth 2.0 강제** — 현재 NAS MCP 서버는 단순 Bearer 인증만 구현했으므로 *지원 안 됨*. 모바일·웹 클라이언트에서 corpus 검색이 필요해지면 OAuth 구현이 별도 작업으로 필요. 자세히는 `docs/superpowers/nas-mcp-deployment.md`.

### NAS MCP 서버 신규 구축 (없는 환경에서)

전체 셋업 절차 (NAS clone → 컨테이너 빌드 → Tailscale Funnel → Bearer auth) 는:
**`docs/superpowers/nas-mcp-deployment.md`** 참조.

---

## 구조

| 폴더 | 무엇 |
|---|---|
| `decisions/` | ADR — 시간순 번호. accepted 되면 본문 수정 금지, 새 ADR로 supersede |
| `specs/` | 현재 합의된 살아있는 스펙 |
| `meetings/` | 회의록 (`YYYY-MM-DD-주제.md`) |
| `people/` | 이해관계자·조직 카드 |
| `domain/` | 의료/측위/RAG 도메인 지식 |
| `deliverables/` | 공식 산출물 인덱스 |
| `_raw/` | 원본 archive (.docx/.hwp/.pdf/.pptx) — 절대 수정 X |
| `_converted/` | ETL 변환 중간물 (gitignore, 검토 후 분류 폴더로 이동) |
| `attachments/` | 이미지·스크린샷 |
| `scripts/` | ETL·무결성 체크·RAG 서버 (Python) |
| `docs/superpowers/` | 설계 문서·plan·배포 가이드 |
| `.obsidian/templates/` | ADR/spec/meeting 템플릿 |

## 컨벤션

- 모든 노트는 frontmatter 필수 (`type`, `status`, `date`, `related`)
- ADR status: `proposed` → `accepted` → `superseded` / `deprecated`
- 한 번 accepted 된 ADR은 본문 고치지 않음. 변경은 **새 ADR + `supersedes` 링크**
- `git log` 가 진짜 audit trail
- pre-commit hook이 무결성 체크 강제 (frontmatter 누락 / 깨진 wikilink / supersedes 비대칭 / orphan _raw)

설계 문서: `docs/superpowers/specs/2026-05-28-corpus-design.md`

---

## 개발자 셋업 (PC)

```bash
cd scripts
py -3.11 -m venv .venv
.venv/Scripts/pip install -r requirements.txt
bash install_hooks.sh
```

(Linux/macOS는 `python3.11 -m venv .venv` + `.venv/bin/pip`)

## ETL — 새 .docx/.hwp 흡수

```bash
# 1. _raw/ 에 원본 복사
cp ~/Downloads/회의록.docx _raw/

# 2. 변환 실행
cd scripts && .venv/Scripts/python -m ingest --vault ..

# 3. _converted/ 검토 후 분류 폴더로 이동
#    - 회의록 → meetings/YYYY-MM-DD-주제.md
#    - 결정 → decisions/NNNN-슬러그.md (ADR)
#    - 스펙 → specs/슬러그.md
#    - 그 외 → domain/

# 4. 무결성 체크
.venv/Scripts/python scripts/check_corpus.py .

# 5. commit + push (pre-commit hook이 자동 체크)
git add . && git commit -m "..." && git push
```

## NAS 배포

NAS MCP 서버 셋업/유지보수: `docs/superpowers/nas-mcp-deployment.md`

## 사이트 발행

git push → 자동 빌드 안 됨 (Corpus-Site repo의 workflow 수동 트리거). 자세히:
`Docs/Corpus-Site/DEPLOY.md`

---

## 자주 쓰는 명령 모음

```bash
# 무결성 체크
.venv/Scripts/python scripts/check_corpus.py .

# 새 raw 흡수
cd scripts && .venv/Scripts/python -m ingest --vault ..

# RAG 인덱스 수동 빌드 (보통 post-commit hook이 자동)
.venv/Scripts/python -c "from pathlib import Path; from rag.build_index import build_index; build_index(Path('.'), Path('scripts/rag/index'))"

# RAG 서버 로컬 테스트 (PC에서, dense 포함)
$env:CORPUS_INDEX_DIR = "$PWD/scripts/rag/index"
cd scripts && .venv/Scripts/python -m rag.mcp_server
```
