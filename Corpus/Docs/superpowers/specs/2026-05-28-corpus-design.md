---
title: P.RAPA Corpus — 설계 문서
date: 2026-05-28
status: approved
authors: [JangHyun-bin, Claude(superpowers:brainstorming)]
related:
  - "[[../../../README]]"
  - "[[../../../MOC]]"
---

# P.RAPA Corpus — 설계 문서

## 0. 메타

- **저장 위치**: `D:\HB\P.RAPA_DEV\Docs\Corpus\` (= Obsidian Vault = git repo)
- **첫 커밋**: `83b5182 — chore: initial vault skeleton`
- **다음 단계**: 본 설계 기반의 구현 plan 작성 (writing-plans 스킬)

---

## 1. 문제 정의 / 배경

### 1-1. 통증

`P.RAPA_DEV` 프로젝트는 스마트병원 AI 사업으로, 수개월에 걸쳐 다음과 같은 자산이 sibling 폴더에 흩어져 누적되어 왔다:

- `Docs/` — 회의록·R&R·사업계획 (한국어 .docx/.hwp/.pdf/.pptx/.xlsx) + 산출물 폴더
- `Domain_RAG/` — 한국어 의료 RAG 코드 레포 (BM25+Dense+Gemma-4-E4B-it)
- `Indoor_Positioning/` — 실내측위 리서치 (markdown)
- `positioning_deepresearch/` — 딥리서치 산출물
- `Prerequisites/Docs/` — 참고 교재 PDF
- `rag_positioning/` — 또 다른 코드 레포

**핵심 통증**: 시간이 지나며 합의된 결정사항이 계속 바뀌고 구체화된다. 사업 범위가 방대해 한 사람이 머릿속에 모두 기억할 수 없고, LLM에게 문서작성을 요청할 때 적절한 컨텍스트를 제공하기 어렵다.

### 1-2. 목표

- **사람이 읽는 위키** + **LLM/RAG 지식베이스** + **공식 산출물 SSoT** — 세 역할을 동시에 수행하는 corpus
- 시간순 결정 진화(decision evolution) 추적이 1급 시민
- 정합성 자동 알람 (오래된 스펙·깨진 링크·체인 끊김 감지)
- 외부 의존 최소 (plain markdown + git → 도구 lock-in 0)

### 1-3. 비목표

- 실시간 협업 편집 (Notion 대체 아님)
- 워크플로우/태스크 매니지먼트 (별도 도구)
- 사업 외부의 공개 컨텐츠 (DEX/블로그/문서 사이트 아님)

---

## 2. 결정한 접근법 (B)

### 2-1. 합의된 핵심 선택

| 결정 사항 | 선택 |
|---|---|
| corpus의 1차 목적 | **하이브리드** — 사람용 위키 + LLM 지식베이스 + 공식 SSoT |
| 원본↔corpus 관계 | **B. 새 SSoT** — Corpus가 진짜 권위, sibling 폴더는 raw archive |
| 편집·뷰 도구 | **Obsidian** (plain markdown, plugins, graph) |
| 발행 도구 | **Quartz 4** (Obsidian wikilink/백링크/그래프 그대로 발행) |
| RAG 인덱서 | **Domain_RAG 재활용** (BM25+Dense+Gemma — 이미 한국어 의료 도메인 튜닝됨) |
| 버전관리 | **git** — git log = 결정 진화 audit trail |
| 호스팅 | **GitHub + Cloudflare Pages + Cloudflare Access** (도메인 화이트리스트 게이팅) |

### 2-2. 의도적으로 채택하지 *않은* 것

- **OpenHuman 같은 단일 데스크탑 앱**: ingest-first 패턴이라 SSoT 모델과 거리. Vault는 plain markdown이라 OpenHuman/Khoj/Open WebUI를 *옵션 레이어*로 언제든 갈아끼울 수 있는 형태가 더 유연.
- **MkDocs/Docusaurus**: wikilink·백링크·그래프가 1급이 아니라 Obsidian Vault 발행에는 불리.
- **Logseq**: journal/outliner 모델이 매력적이나 학습곡선과 외부 공유 약점이 큼.

---

## 3. 아키텍처 개요

```
┌────────────────────────────────────────────────────────────────────┐
│                       P.RAPA_DEV/Docs/Corpus/                      │
│                       (= Obsidian Vault = git repo = SSoT)         │
│                                                                    │
│   decisions/  specs/  meetings/  people/  domain/  deliverables/   │
│   _raw/  _converted/  attachments/  scripts/  .obsidian/templates/ │
└────────────────────────────────────────────────────────────────────┘
        │                       │                       │
        │ (사람)                 │ (자동)                │ (자동)
        ▼                       ▼                       ▼
  ┌──────────┐         ┌───────────────┐         ┌──────────────────┐
  │ Obsidian │         │ Quartz build  │         │ Domain_RAG       │
  │ Dataview │         │ → 정적사이트  │         │ index builder    │
  │   graph  │         │  (사내 URL)   │         │ → /ask?mode=     │
  └──────────┘         └───────────────┘         │   corpus         │
                                                  └──────────────────┘

  ┌──────────────────────────────────────────────────────────┐
  │  ETL pipeline (scripts/ingest/)                           │
  │  raw → markitdown / hwp5txt / pandoc → 검토 → vault      │
  └──────────────────────────────────────────────────────────┘
```

**책임 분리 3대 원칙**:
1. Vault (Corpus) = 사람이 쓰는 진짜 SSoT, plain markdown
2. 발행 파이프라인 = Vault → 정적 사이트 (derived, 언제든 폐기·재빌드)
3. 인덱스 파이프라인 = Vault → RAG 인덱스 (derived, 언제든 폐기·재빌드)

---

## 4. 디렉토리 구조

```
Docs/Corpus/
├── README.md, MOC.md              # 진입점
├── decisions/                     # ADR (시간순 NNNN-...)
├── specs/                         # 살아있는 스펙
├── meetings/                      # 회의록 (YYYY-MM-DD-주제)
├── people/                        # 이해관계자·조직 카드
├── domain/                        # 도메인 지식
├── deliverables/                  # 공식 산출물 인덱스
├── _raw/                          # 원본 archive (절대 수정 X)
├── _converted/                    # ETL 중간물 (검토 후 분류 폴더로 이동)
├── attachments/                   # 이미지·스크린샷
├── scripts/                       # ETL·무결성 체크
├── docs/superpowers/specs/        # 본 설계 문서
└── .obsidian/templates/           # ADR/spec/meeting 템플릿
```

**파일명 컨벤션**:
- `decisions/`: `NNNN-kebab-case-슬러그.md` (예: `0007-push-service-stack.md`)
- `meetings/`: `YYYY-MM-DD-주제.md`
- `specs/`: `kebab-case-슬러그.md`
- `_raw/`: 원본 파일명 보존 + 출처 추적 (`YYMMDD_원본명_출처.확장자`)

---

## 5. 결정사항 추적 컨벤션

### 5-1. Frontmatter

**ADR (`decisions/*.md`)**:
```yaml
---
id: 0007
type: decision
status: accepted          # proposed | accepted | superseded | deprecated
date: 2026-05-26
deciders: [[FAMOZ]], [[전남대병원]], [[RAPA]]
supersedes: [[0003-app-side-stack]]
superseded_by: null
related_specs: [[push-service]]
related_meetings: [[2026-05-18-RAPA-스마트병원AI]]
tags: [push, infra]
---
```

**스펙 (`specs/*.md`)**:
```yaml
---
type: spec
status: living            # draft | living | frozen | retired
last_reviewed: 2026-05-26
owner: [[FAMOZ]]
implements: [[0007-push-service-stack]]
version: v2
---
```

**회의록 (`meetings/*.md`)**:
```yaml
---
type: meeting
date: 2026-05-18
attendees: [[전남대병원]], [[FAMOZ]], [[RAPA]], [[레몬헬스케어]]
produced_decisions: [[0007-push-service-stack]]
agenda_source: [[_raw/260518_RAPA_스마트병원AI_회의록]]
---
```

### 5-2. ADR 본문 구조 (Nygard 표준 변형)

`컨텍스트` → `옵션` → `결정` → `근거` → `결과` → `변경 이력`

### 5-3. status 라이프사이클 철칙

```
proposed ──→ accepted ──→ superseded   (새 ADR이 대체)
                     └──→ deprecated   (대체 없이 폐기)
```

1. **수정 금지 원칙** — `accepted` 된 ADR은 본문을 *고치지 않는다*. 변경은 **새 ADR + `supersedes` 링크**로만.
2. **체인 양방향** — `supersedes` ↔ `superseded_by` 가 양쪽에서 서로를 가리킴.
3. **git이 진짜 audit trail** — frontmatter는 빠른 조회용, 누가 언제 뭘 바꿨나는 `git log -p`.

### 5-4. Dataview 보드 (정합성 알람)

- **살아있는 결정** (status=accepted, 날짜순)
- **Decision evolution 타임라인** (전체 ADR + supersede 체인)
- **특정 조직 관여 결정** (deciders 필터)
- **검토 시점 오래된 스펙** (last_reviewed > 60일 → 정합성 알람)

### 5-5. git commit 컨벤션

```
adr:       <id> <slug> <status>      # ADR 변경
spec:      <slug> ...                # 스펙 변경
meeting:   <date> <topic>            # 회의록
ingest:    <raw filename> → <폴더>   # 원본 흡수
chore:     ...                       # 기타
```

`git log --grep="^adr"` 한 줄로 결정 변경만 추출 가능.

### 5-6. 자동 무결성 체크 (`scripts/check_corpus.py`)

- `supersedes` ↔ `superseded_by` 양방향 정합
- 깨진 `[[...]]` 백링크
- frontmatter 필수 필드 누락
- `_raw/` 파일 중 어떤 ADR/스펙/회의록에서도 인용 안 된 것 (orphan raw)
- 본문 수정된 `status: accepted` ADR (pre-commit hook)

CI(GitHub Actions)에서 강제. **실패하면 Quartz 발행과 RAG 인덱스 rebuild 모두 차단.**

---

## 6. 변환 ETL 파이프라인

### 6-1. 포맷별 도구

| 포맷 | 1차 도구 | 폴백 |
|---|---|---|
| `.docx` | markitdown | pandoc, mammoth |
| `.pdf` (텍스트) | markitdown | pymupdf4llm |
| `.pdf` (스캔) | olmocr / marker | tesseract |
| `.pptx` | markitdown | python-pptx |
| `.xlsx` | markitdown | openpyxl |
| `.hwp` | hwp5txt → 사람 정리 | LibreOffice → docx → markitdown |
| `.hwpx` | libhwp / LibreOffice | hwp5txt |

→ markitdown 하나로 80% 커버. .hwp만 별도 핸들링.

### 6-2. 5단계 흐름

```
① 입수 → ② _raw/ 저장 → ③ convert.py 자동 변환 → ④ 사람 검토 (REVIEW.md 체크리스트) → ⑤ 분류 폴더로 이동
```

`_converted/{stem}/` 디렉토리에 `content.md` + `meta.yaml` + `assets/` + `REVIEW.md` 생성.

### 6-3. convert.py 동작 명세

- 마지막 실행 이후 추가된 `_raw/` 파일만 처리 (ledger로 mtime 추적)
- 자동 품질 점검: 빈 결과, 1KB 미만, 표 깨짐 추정, 한국어 비율 < 30% → REVIEW.md에 경고
- 한국어 인코딩(EUC-KR 등) 감지 → UTF-8 정규화

### 6-4. 한국어 처리 주의점

- 인코딩 자동 감지 + UTF-8 정규화
- 한국어 .docx의 셀 병합은 markdown으로 깔끔히 안 됨 → 복잡한 표는 이미지로 보존
- 약어(RAPA, FAMOZ 등)는 첫 등장시 `[[people/...]]` 백링크 (Templater 보조)

### 6-5. 자동화하지 *않는* 게이트 (반드시 사람)

1. 어느 폴더(`decisions`/`specs`/`meetings`/...)로 분류
2. frontmatter의 `status`, `deciders`, `related` 채우기
3. ADR로 만들지, 기존 ADR을 supersede할지 판단

---

## 7. Quartz 발행

### 7-1. 공개 범위 (opt-out 기본 정책)

`draft: true` 또는 `publish: false` frontmatter가 있으면 발행 제외.

| 폴더 | 기본 공개? |
|---|---|
| decisions, specs, domain, deliverables, attachments | ✅ 공개 |
| meetings, people | ⚠️ 선택적 (민감 노트는 `publish: false`) |
| _raw, _converted, .obsidian | ❌ 비공개 (`.quartzignore`) |

### 7-2. 한국어 처리

- 폰트: Pretendard 또는 Noto Sans KR (본문), D2Coding / JetBrains Mono (코드)
- 검색: Quartz 기본 FlexSearch + n-gram 인덱스로 시작 → 답답하면 Pagefind로 교체
- URL slug: 한국어 percent-encode로 동작하나, 영문 슬러그 컨벤션 권장

### 7-3. 호스팅

```
git push to main
    ↓
GitHub Actions (Quartz 빌드 + 무결성 체크)
    ↓
Cloudflare Pages (배포)
    ↓
rapa-corpus.famoz.kr  (Cloudflare DNS + Access 게이팅)
```

- 무료, 자동 HTTPS, 빌드 캐시
- Cloudflare Access로 도메인 화이트리스트(`@famoz.com`, `@jnuh.kr`, `@rapa.or.kr`) 게이팅

### 7-4. 빌드 워크플로우

`.github/workflows/publish.yml` 단계:
1. checkout → 2. node setup → 3. npm ci → 4. `check_corpus.py` (실패시 중단) → 5. `npx quartz build` → 6. Cloudflare Pages 업로드

---

## 8. Domain_RAG 인덱서 연결

### 8-1. Domain_RAG 재활용 범위

- **재활용 그대로**: `index/`, `core/retrieval/`, `core/llm/`, FastAPI `/ask`
- **신규 추가**: `index/build_corpus.py`, `core/rag/corpus.py` (corpus 모드)
- **모드 분기**: `/ask?mode=clinician|corpus` — corpus 모드는 의료 가드레일 off, citation 형식 다름

### 8-2. Chunking 전략 (markdown 친화)

- 헤딩 경계(`##`/`###`) 우선 분할
- 한 chunk 800~1200 토큰
- 코드블록·표는 절대 분할 금지
- 각 chunk 앞에 breadcrumb (`[decisions/0007 > 결과]`)
- 200토큰 overlap

### 8-3. 메타데이터 (chunk별)

frontmatter → 인덱스 메타로 매핑. `obsidian://` URI + Quartz 웹 URL 양쪽 함께 저장 → citation 시 두 view 동시 인용.

```json
{
  "chunk_id": "...",
  "obsidian_uri": "obsidian://open?vault=Corpus&file=...",
  "web_url": "https://rapa-corpus.famoz.kr/...",
  "type": "decision", "status": "accepted",
  "date": "2026-05-26",
  "deciders": [...], "supersedes": [...], "tags": [...],
  "heading_path": [...], "text": "..."
}
```

→ 메타 필터 검색 가능 ("2026-05 이후 결정만", "전남대병원 관여만", "status=accepted만").

### 8-4. /ask 엔드포인트 (corpus 모드)

```
POST /ask
{ "mode": "corpus", "question": "...", "top_k": 8, "filters": {...} }

응답:
{
  "answer": "...",
  "citations": [{ "obsidian_uri": "...", "web_url": "...", "score": 0.87 }, ...]
}
```

가드레일은 corpus 모드에서 off (내부 운영용). 외부 공개시에만 output guardrail 옵션 on.

### 8-5. 인덱스 갱신 — git hook 방식 채택

`.git/hooks/post-commit` (또는 GitHub Action):
- `git diff --name-only HEAD~1` 로 변경된 .md만 골라 incremental rebuild
- Quartz 발행과 같은 트리거에서 동시 실행
- 부담 거의 0, 최신성 우수

### 8-6. 부차 인덱서 (선택)

같은 Vault를 다른 도구가 동시 인덱싱해도 무방:
- OpenHuman (데스크탑 Memory Tree)
- Khoj (Obsidian 플러그인 사이드바 챗)
- Open WebUI / AnythingLLM (동료용 채팅 UI)

Domain_RAG가 기본, 나머지는 옵션 — 갈아끼움 자유.

---

## 9. 운영 워크플로우 + 마이그레이션

### 9-1. 일상 시나리오 3개

**A. 회의 후 결정 1건**: meeting 노트 → ADR 새 노트 → 옛 ADR supersede → spec last_reviewed 갱신 → commit → push (auto-build) — 5~10분.

**B. 새 .docx 흡수**: `_raw/` 저장 → `convert.py` → `_converted/` 검토 → frontmatter 채움 → 분류 폴더 이동 → commit — 파일당 5~30분.

**C. LLM 보고서 작성**: Claude Code에 Vault 통째로 컨텍스트 / 또는 `/ask?mode=corpus` 호출 — 인용 포함 초안.

### 9-2. 마이그레이션 (3주 / 5단계)

| Step | 기간 | 내용 |
|---|---|---|
| 1. 골격 + 사람 카드 | 1일 | people/ 4장 (전남대병원·RAPA·FAMOZ·레몬헬스케어), MOC 정리 |
| 2. 회의록 흡수 | 3~5일 | `Docs/*260*` 회의 파일 → `_raw/` → `convert.py` → `meetings/` |
| 3. **ADR 발굴** | 5~7일 | 회의록에서 *이미 합의된 결정*을 retroactive ADR로 (5~10건 예상) |
| 4. 살아있는 스펙 작성 | 5~7일 | `specs/domain-rag-api`, `indoor-positioning`, `push-service`, `system-architecture` |
| 5. 인덱서·발행 가동 | 2~3일 | `build_corpus.py` + Quartz + GitHub Actions + Cloudflare Pages |

→ **Step 3이 사용자 통증 핵심 해소 지점**. 머릿속 결정사항이 처음으로 외부화.

### 9-3. 운영 부담 추정

| 활동 | 빈도 | 1회 소요 |
|---|---|---|
| ADR 작성 | 주 1~3건 | 10~20분 |
| .docx 흡수 | 주 1~5건 | 5~30분 |
| spec 검토 갱신 | 월 1~2회 | 5~10분 |
| 인덱스·발행 | 자동 | 0 |

→ **주 1~2시간**으로 vault 살아있는 상태 유지. 순증 부담은 변환·검토 30분~1시간/주 정도.

### 9-4. 실패 모드 & 가드

| 위험 | 가드 |
|---|---|
| ADR 안 쓰고 spec만 고침 | 큰 spec PR에 ADR 링크 요구 (check_corpus) |
| accepted ADR 본문 사후 수정 | pre-commit hook이 감지 |
| 깨진 백링크 / orphan raw | CI 무결성 체크가 빌드 차단 |
| .hwp 변환 품질 | REVIEW.md 자동 경고 + 검토 게이트 |
| _raw 부피 폭주 | 3개월 후 100MB 넘으면 git LFS 활성화 (.gitattributes 한 줄 주석 해제) |
| Vault 백업 | git remote (GitHub private) + Obsidian Sync(선택) |

---

## 10. 성공 지표 (3개월 후)

- ADR 누적 ≥ 15건 (활발한 의사결정 외부화)
- "60일 이상 검토 안 된 살아있는 스펙" 항상 ≤ 3개 (정합성 알람 작동)
- LLM 보고서 초안 시 인용된 corpus chunk ≥ 5개/건 (LLM이 실제 corpus 의존)
- 컨소시엄 보고시 "이 URL 보세요"가 정착 (Quartz URL 공유 횟수)

---

## 11. 미결정 / 다음 결정 후보

설계 단계에서 의도적으로 미룬 항목 (구현 plan 또는 운영 중에 결정):

- **GitHub 레포 위치**: private org (예: `famoz/`) vs personal — 컨소시엄 권한 정책 확정 후
- **Cloudflare Access 정책 구체화**: 도메인 화이트리스트 vs 명단 기반
- **Obsidian Sync 사용 여부**: 모바일 사용 빈도에 따라
- **임베딩 모델 선택**: Domain_RAG가 현재 쓰는 모델 그대로 vs corpus용 별도 (한국어 sentence embedding)
- **첫 ADR 발굴 우선순위**: 마이그레이션 Step 3에서 어떤 결정부터 retroactive 작성할지

---

## 12. 다음 단계

1. **본 설계 문서 사용자 리뷰** (현재 단계)
2. 승인 후 → `superpowers:writing-plans` 스킬로 구체적 구현 plan 작성
3. 구현 plan은 마이그레이션 5단계를 각각의 task 단위로 쪼개고, 각 task별로 검증 기준·롤백 절차·예상 시간을 포함

---

## 부록 A. 현재 git 상태

```
첫 커밋: 83b5182 chore: initial vault skeleton
브랜치: main

생성된 파일:
  README.md, MOC.md
  .gitignore, .gitattributes
  .obsidian/templates/{adr,spec,meeting}.md
  decisions/.gitkeep ... (9개 디렉토리 .gitkeep)
  scripts/README.md
```

## 부록 B. 참고

- Quartz 4: https://quartz.jzhao.xyz/
- markitdown: https://github.com/microsoft/markitdown
- hwp5: https://github.com/mete0r/pyhwp
- ADR (Michael Nygard): https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Domain_RAG 아키텍처: `D:\HB\P.RAPA_DEV\Docs\260513_Domain_RAG_ARCHITECTURE.md`
