# P.RAPA Corpus Migration & Infrastructure Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** §9-2 spec의 5단계 마이그레이션을 수행 가능한 task 단위로 쪼개고, 무결성 체크 / ETL / RAG 인덱서 / Quartz 발행까지 구현해서 vault가 *살아있는 상태*로 운영 가능하게 만든다.

**Architecture:** Phase A(인프라 코드, TDD) → Phase B(콘텐츠, 사람+LLM 보조) → Phase C(RAG 인덱서·Quartz 발행). 모든 코드는 vault 자체 `scripts/` 아래에 둠. Domain_RAG가 비어있는 현 시점에서 RAG 인덱서는 vault에서 자체 운용하고, Domain_RAG가 성숙하면 그쪽으로 이관.

**Tech Stack:** Python 3.11+, pytest, markitdown, hwp5, python-frontmatter, BM25 (rank-bm25), sentence-transformers, FAISS, FastAPI, Node 20, Quartz 4, GitHub Actions, Cloudflare Pages.

---

## Spec ↔ Plan 조정 (필수 읽기)

설계 spec §8 은 "Domain_RAG 재활용 그대로" 를 가정했으나, 실제 `Domain_RAG/` 폴더는 빈 골격(폴더만)만 있고 아키텍처 md만 존재. 이에 따라 본 plan은:

- **RAG 인덱서·서버를 vault 자체 `scripts/rag/` 아래에 둠**. Domain_RAG가 성숙하면 동일 모듈을 그쪽으로 이관 (인터페이스를 호환되게 설계).
- spec §8-1의 `core/rag/corpus.py`, `index/build_corpus.py` 경로는 미래 이관 후 위치. 지금은 vault 안.
- 가드레일·평가는 vault 인덱서에서 제외 (corpus 모드는 내부 운영용).

이 조정 외 spec의 모든 결정은 그대로 적용.

---

## File Structure

### Vault 내부 (`Docs/Corpus/`)

| 경로 | 책임 |
|---|---|
| `scripts/requirements.txt` | Python 의존성 (잠금) |
| `scripts/pyproject.toml` | pytest 설정 + 패키지 메타 |
| `scripts/check_corpus.py` | 무결성 체크 CLI (frontmatter / supersedes / wikilink / orphan raw) |
| `scripts/tests/test_check_corpus.py` | pytest |
| `scripts/ingest/convert.py` | `_raw/` → `_converted/` ETL CLI |
| `scripts/ingest/tests/test_convert.py` | pytest |
| `scripts/rag/chunker.py` | markdown chunking (헤딩 경계, 800-1200토큰, 200토큰 overlap) |
| `scripts/rag/build_index.py` | Vault → BM25 + Dense 인덱스 빌드 |
| `scripts/rag/serve.py` | FastAPI `/ask` (corpus 모드 only) |
| `scripts/rag/index/` | 인덱스 산출물 저장 (gitignore) |
| `scripts/rag/tests/test_chunker.py` | pytest |
| `scripts/rag/tests/test_build_index.py` | pytest |
| `.github/workflows/check.yml` | PR/push마다 check_corpus.py 실행 |
| `.github/workflows/publish.yml` | Quartz 빌드 + Cloudflare Pages 배포 |
| `.git/hooks/pre-commit` | check_corpus 로컬 실행 (옵션) |
| `.git/hooks/post-commit` | RAG 인덱스 incremental rebuild (옵션) |
| `people/{전남대병원,RAPA,FAMOZ,레몬헬스케어}.md` | 이해관계자 카드 4장 |
| `_raw/260*.{docx,pdf,hwp}` | 원본 archive 이주 |
| `meetings/2026-05-*.md` | 회의록 8건 |
| `decisions/0001~..md` | retroactive ADR 5~10건 |
| `specs/{domain-rag-api,indoor-positioning,push-service,system-architecture}.md` | 살아있는 스펙 4건 |

### Vault 외부

| 경로 | 책임 |
|---|---|
| `D:\HB\P.RAPA_DEV\Docs\Corpus-Site\` | Quartz 4 프로젝트 (별 디렉토리, vault를 content 소스로 사용) |

---

## Phase A — 인프라 코드 (TDD)

### Task 1: Python 환경 + scripts 패키지 골격

**Files:**
- Create: `Docs/Corpus/scripts/requirements.txt`
- Create: `Docs/Corpus/scripts/pyproject.toml`
- Create: `Docs/Corpus/scripts/__init__.py`
- Create: `Docs/Corpus/scripts/tests/__init__.py`
- Modify: `Docs/Corpus/.gitignore`

- [ ] **Step 1: `requirements.txt` 작성**

```
python-frontmatter==1.1.0
markitdown==0.0.1a3
rank-bm25==0.2.2
sentence-transformers==3.0.1
faiss-cpu==1.8.0
fastapi==0.115.0
uvicorn==0.30.6
pytest==8.3.3
chardet==5.2.0
```

- [ ] **Step 2: `pyproject.toml` 작성 (pytest 설정)**

```toml
[tool.pytest.ini_options]
testpaths = ["tests", "ingest/tests", "rag/tests"]
python_files = "test_*.py"
addopts = "-q --strict-markers"
```

- [ ] **Step 3: `__init__.py` 두 개를 빈 파일로 생성**

```
Docs/Corpus/scripts/__init__.py        (빈 파일)
Docs/Corpus/scripts/tests/__init__.py  (빈 파일)
```

- [ ] **Step 4: `.gitignore` 에 venv·인덱스 추가**

`Docs/Corpus/.gitignore` 끝에 다음 블록 추가:

```
# --- Python ---
scripts/.venv/
scripts/**/__pycache__/
scripts/**/*.pyc
scripts/.pytest_cache/

# --- RAG 인덱스 산출물 ---
scripts/rag/index/
```

- [ ] **Step 5: venv 생성 + 의존성 설치 검증**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus/scripts
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/pytest --version
```
Expected: `pytest 8.3.3` 출력.

- [ ] **Step 6: 커밋**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
git add scripts/ .gitignore
git commit -m "chore: scripts python skeleton (deps + pytest)"
```

**Verification:** `pytest --version` 동작.
**Rollback:** `git reset --hard 543ea20` (직전 커밋으로).
**Estimated time:** 20분.

---

### Task 2: check_corpus — frontmatter 파싱 유틸 (TDD)

**Files:**
- Create: `Docs/Corpus/scripts/check_corpus.py`
- Create: `Docs/Corpus/scripts/tests/test_check_corpus.py`
- Create: `Docs/Corpus/scripts/tests/fixtures/` (테스트용 mini vault)

- [ ] **Step 1: 테스트 fixture 생성**

`Docs/Corpus/scripts/tests/fixtures/mini_vault/decisions/0001-test.md`:
```markdown
---
id: 0001
type: decision
status: accepted
date: 2026-05-28
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: null
related_specs: []
related_meetings: []
tags: []
---

# 0001 — Test ADR

본문.
```

`Docs/Corpus/scripts/tests/fixtures/mini_vault/decisions/0002-missing-type.md` (의도적 결함):
```markdown
---
id: 0002
status: accepted
date: 2026-05-28
---

# 0002 — type 누락
```

- [ ] **Step 2: 실패 테스트 작성**

`Docs/Corpus/scripts/tests/test_check_corpus.py`:
```python
from pathlib import Path
from check_corpus import load_notes, NoteError

FIXTURES = Path(__file__).parent / "fixtures" / "mini_vault"

def test_load_notes_returns_one_per_md_file():
    notes = load_notes(FIXTURES)
    assert len(notes) == 2

def test_load_notes_parses_frontmatter():
    notes = load_notes(FIXTURES)
    by_id = {n.meta.get("id"): n for n in notes}
    assert by_id[1].meta["status"] == "accepted"
    assert by_id[1].meta["type"] == "decision"
```

- [ ] **Step 3: 테스트 실행해 실패 확인**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus/scripts
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: `ModuleNotFoundError: No module named 'check_corpus'`.

- [ ] **Step 4: 최소 구현 작성**

`Docs/Corpus/scripts/check_corpus.py`:
```python
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import frontmatter

EXCLUDED_DIRS = {"_raw", "_converted", ".obsidian", ".git", "scripts", "docs"}

@dataclass
class Note:
    path: Path
    meta: dict[str, Any]
    body: str

class NoteError(Exception):
    pass

def load_notes(vault_root: Path) -> list[Note]:
    notes: list[Note] = []
    for md in vault_root.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in md.relative_to(vault_root).parts):
            continue
        with md.open(encoding="utf-8") as f:
            post = frontmatter.load(f)
        notes.append(Note(path=md, meta=dict(post.metadata), body=post.content))
    return notes
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 2 passed.

- [ ] **Step 6: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/
git commit -m "feat: check_corpus — frontmatter loading"
```

**Verification:** pytest 2 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 25분.

---

### Task 3: check_corpus — 필수 frontmatter 필드 검증 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/check_corpus.py`
- Modify: `Docs/Corpus/scripts/tests/test_check_corpus.py`

- [ ] **Step 1: 실패 테스트 추가**

`test_check_corpus.py` 끝에 추가:
```python
from check_corpus import check_required_fields

def test_check_required_fields_flags_missing_type():
    notes = load_notes(FIXTURES)
    errors = check_required_fields(notes)
    msgs = [e.message for e in errors]
    assert any("type" in m and "0002" in str(e.path) for m, e in zip(msgs, errors))

def test_check_required_fields_passes_on_complete_note():
    notes = load_notes(FIXTURES)
    good = [n for n in notes if n.meta.get("id") == 1]
    errors = check_required_fields(good)
    assert errors == []
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 2 failed (`check_required_fields` not defined).

- [ ] **Step 3: 구현 추가**

`check_corpus.py` 끝에 추가:
```python
REQUIRED_BY_TYPE = {
    "decision": {"id", "type", "status", "date"},
    "spec":     {"type", "status", "last_reviewed"},
    "meeting":  {"type", "date"},
    "org":      {"type"},
}

@dataclass
class Error:
    path: Path
    message: str

def check_required_fields(notes: list[Note]) -> list[Error]:
    errors: list[Error] = []
    for n in notes:
        t = n.meta.get("type")
        if t is None:
            errors.append(Error(n.path, "frontmatter missing required field: type"))
            continue
        required = REQUIRED_BY_TYPE.get(t, set())
        for field_name in required:
            if field_name not in n.meta:
                errors.append(Error(n.path, f"frontmatter missing required field: {field_name}"))
    return errors
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 4 passed.

- [ ] **Step 5: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/test_check_corpus.py
git commit -m "feat: check_corpus — required frontmatter fields per type"
```

**Verification:** 4 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 20분.

---

### Task 4: check_corpus — supersedes 양방향 정합 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/check_corpus.py`
- Modify: `Docs/Corpus/scripts/tests/test_check_corpus.py`
- Create: `Docs/Corpus/scripts/tests/fixtures/mini_vault/decisions/0003-old.md`
- Create: `Docs/Corpus/scripts/tests/fixtures/mini_vault/decisions/0004-new.md`

- [ ] **Step 1: fixture 추가 (의도적으로 한쪽만 채움)**

`decisions/0003-old.md`:
```markdown
---
id: 3
type: decision
status: superseded
date: 2026-05-01
superseded_by: null   # 의도적 결함: 0004가 supersede하는데 빈 채로 둠
---

# 0003 — Old
```

`decisions/0004-new.md`:
```markdown
---
id: 4
type: decision
status: accepted
date: 2026-05-15
supersedes: "[[0003-old]]"
---

# 0004 — New
```

- [ ] **Step 2: 실패 테스트 추가**

```python
from check_corpus import check_supersedes_chain

def test_supersedes_one_way_only_is_flagged():
    notes = load_notes(FIXTURES)
    errors = check_supersedes_chain(notes)
    msgs = [e.message for e in errors]
    assert any("0003" in str(e.path) and "superseded_by" in m for m, e in zip(msgs, errors))
```

- [ ] **Step 3: 실패 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 1 failed (`check_supersedes_chain` not defined).

- [ ] **Step 4: 구현 추가**

`check_corpus.py` 끝에 추가:
```python
import re
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")

def _stem(s: str | None) -> str | None:
    if not s:
        return None
    m = WIKILINK.search(s)
    target = m.group(1) if m else s
    return target.split("/")[-1].strip()

def check_supersedes_chain(notes: list[Note]) -> list[Error]:
    errors: list[Error] = []
    by_stem = {n.path.stem: n for n in notes}

    for n in notes:
        if n.meta.get("type") != "decision":
            continue

        sup = _stem(n.meta.get("supersedes"))
        if sup:
            target = by_stem.get(sup)
            if not target:
                errors.append(Error(n.path, f"supersedes target not found: {sup}"))
            else:
                back = _stem(target.meta.get("superseded_by"))
                if back != n.path.stem:
                    errors.append(Error(
                        target.path,
                        f"superseded_by must point back to [[{n.path.stem}]]"))
    return errors
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 5 passed.

- [ ] **Step 6: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/
git commit -m "feat: check_corpus — supersedes bidirectional consistency"
```

**Verification:** 5 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 30분.

---

### Task 5: check_corpus — 깨진 wikilink 검사 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/check_corpus.py`
- Modify: `Docs/Corpus/scripts/tests/test_check_corpus.py`

- [ ] **Step 1: fixture에 깨진 링크 추가**

`decisions/0001-test.md` 본문 끝에 추가:
```
관련: [[nonexistent-target]]
```

- [ ] **Step 2: 실패 테스트 추가**

```python
from check_corpus import check_wikilinks

def test_broken_wikilink_is_flagged():
    notes = load_notes(FIXTURES)
    errors = check_wikilinks(notes)
    msgs = [e.message for e in errors]
    assert any("nonexistent-target" in m for m in msgs)
```

- [ ] **Step 3: 실패 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 1 failed.

- [ ] **Step 4: 구현 추가**

```python
def check_wikilinks(notes: list[Note]) -> list[Error]:
    errors: list[Error] = []
    by_stem = {n.path.stem: n for n in notes}

    for n in notes:
        for m in WIKILINK.finditer(n.body):
            target = m.group(1).split("/")[-1].strip()
            if target not in by_stem:
                errors.append(Error(n.path, f"broken wikilink: [[{target}]]"))
    return errors
```

- [ ] **Step 5: 테스트 통과 확인 + 다른 fixture에 영향 없는지**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 6 passed.

- [ ] **Step 6: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/
git commit -m "feat: check_corpus — broken wikilink detection"
```

**Verification:** 6 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 20분.

---

### Task 6: check_corpus — orphan _raw 경고 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/check_corpus.py`
- Modify: `Docs/Corpus/scripts/tests/test_check_corpus.py`
- Create: `Docs/Corpus/scripts/tests/fixtures/mini_vault/_raw/orphan.pdf` (빈 파일)
- Create: `Docs/Corpus/scripts/tests/fixtures/mini_vault/_raw/cited.pdf` (빈 파일)
- Modify: `Docs/Corpus/scripts/tests/fixtures/mini_vault/decisions/0001-test.md` (cited.pdf 인용)

- [ ] **Step 1: fixture 준비**

빈 파일 2개:
```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus/scripts/tests/fixtures/mini_vault
mkdir -p _raw
type nul > _raw/orphan.pdf      # Windows에서 빈 파일
type nul > _raw/cited.pdf
```

`decisions/0001-test.md` 본문에 추가:
```
원본: [[_raw/cited]]
```

- [ ] **Step 2: 실패 테스트 추가**

```python
from check_corpus import check_orphan_raw

def test_orphan_raw_warned():
    notes = load_notes(FIXTURES)
    warnings = check_orphan_raw(FIXTURES, notes)
    assert any("orphan.pdf" in w.message for w in warnings)

def test_cited_raw_not_warned():
    notes = load_notes(FIXTURES)
    warnings = check_orphan_raw(FIXTURES, notes)
    assert not any("cited.pdf" in w.message for w in warnings)
```

- [ ] **Step 3: 실패 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 2 failed.

- [ ] **Step 4: 구현 추가**

```python
def check_orphan_raw(vault_root: Path, notes: list[Note]) -> list[Error]:
    raw_dir = vault_root / "_raw"
    if not raw_dir.exists():
        return []
    cited_stems: set[str] = set()
    for n in notes:
        for m in WIKILINK.finditer(n.body):
            target = m.group(1).strip()
            if target.startswith("_raw/"):
                cited_stems.add(target.removeprefix("_raw/").split(".")[0])
    warnings: list[Error] = []
    for f in raw_dir.iterdir():
        if f.is_file() and f.name != ".gitkeep" and f.stem not in cited_stems:
            warnings.append(Error(f, f"orphan in _raw/: {f.name} (not cited from any note)"))
    return warnings
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 8 passed.

- [ ] **Step 6: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/
git commit -m "feat: check_corpus — orphan _raw warning"
```

**Verification:** 8 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 25분.

---

### Task 7: check_corpus CLI 통합 + exit code

**Files:**
- Modify: `Docs/Corpus/scripts/check_corpus.py`
- Modify: `Docs/Corpus/scripts/tests/test_check_corpus.py`

- [ ] **Step 1: 실패 테스트 추가 (subprocess로 CLI 호출)**

```python
import subprocess, sys

def test_cli_clean_vault_exits_0(tmp_path):
    # 합격용 mini vault 만들기
    note = tmp_path / "decisions" / "0001-x.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        "---\nid: 1\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0001 — X\n",
        encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "check_corpus.py", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr

def test_cli_failing_vault_exits_1():
    result = subprocess.run(
        [sys.executable, "check_corpus.py", str(FIXTURES)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True)
    assert result.returncode == 1
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py::test_cli_clean_vault_exits_0 -v
```
Expected: failed (CLI 진입점 없음).

- [ ] **Step 3: CLI 구현 추가**

`check_corpus.py` 끝에 추가:
```python
def run_all_checks(vault_root: Path) -> tuple[list[Error], list[Error]]:
    notes = load_notes(vault_root)
    errors = (
        check_required_fields(notes)
        + check_supersedes_chain(notes)
        + check_wikilinks(notes))
    warnings = check_orphan_raw(vault_root, notes)
    return errors, warnings

def main(argv: list[str] | None = None) -> int:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    vault_root = Path(args[0] if args else ".").resolve()
    errors, warnings = run_all_checks(vault_root)
    for w in warnings:
        print(f"WARN  {w.path.relative_to(vault_root)}: {w.message}")
    for e in errors:
        print(f"ERROR {e.path.relative_to(vault_root)}: {e.message}")
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/pytest tests/test_check_corpus.py -v
```
Expected: 10 passed.

- [ ] **Step 5: 실제 vault에 돌려서 동작 확인**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
.venv/Scripts/python scripts/check_corpus.py .
```
Expected: `0 errors, 0 warnings` (현 vault는 깨끗).

- [ ] **Step 6: 커밋**

```bash
git add scripts/check_corpus.py scripts/tests/
git commit -m "feat: check_corpus — CLI integration with exit code"
```

**Verification:** 10 passed + 실제 vault에서 `0 errors`.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 25분.

---

### Task 8: pre-commit hook으로 check_corpus 호출

**Files:**
- Create: `Docs/Corpus/scripts/hooks/pre-commit`
- Create: `Docs/Corpus/scripts/install_hooks.sh`
- Modify: `Docs/Corpus/README.md`

- [ ] **Step 1: hook 스크립트 작성**

`Docs/Corpus/scripts/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
set -e
ROOT="$(git rev-parse --show-toplevel)"
PY="$ROOT/scripts/.venv/Scripts/python"
if [ ! -x "$PY" ]; then
  PY="$ROOT/scripts/.venv/bin/python"
fi
if [ ! -x "$PY" ]; then
  echo "scripts/.venv not found — skip corpus check"
  exit 0
fi
"$PY" "$ROOT/scripts/check_corpus.py" "$ROOT"
```

- [ ] **Step 2: 인스톨 스크립트 작성**

`Docs/Corpus/scripts/install_hooks.sh`:
```bash
#!/usr/bin/env bash
set -e
ROOT="$(git rev-parse --show-toplevel)"
cp "$ROOT/scripts/hooks/pre-commit" "$ROOT/.git/hooks/pre-commit"
chmod +x "$ROOT/.git/hooks/pre-commit"
echo "pre-commit hook installed."
```

- [ ] **Step 3: README에 설치 안내 추가**

`Docs/Corpus/README.md` 끝에 추가:
```markdown
## 개발자 셋업

```bash
cd scripts
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
bash install_hooks.sh
```
```

- [ ] **Step 4: hook 동작 검증 (의도적 결함 노트로)**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
bash scripts/install_hooks.sh
echo "---" > decisions/_bad.md
git add decisions/_bad.md
git commit -m "test: should fail"
```
Expected: pre-commit이 실패하며 "frontmatter missing" 에러 출력, 커밋 차단.

- [ ] **Step 5: 결함 노트 제거 + hook 파일 커밋**

```bash
git restore --staged decisions/_bad.md
rm decisions/_bad.md
git add scripts/hooks/ scripts/install_hooks.sh README.md
git commit -m "feat: pre-commit hook for corpus integrity check"
```

**Verification:** 의도적 깨진 노트 커밋이 차단됨.
**Rollback:** `git reset --hard HEAD~1` + `rm .git/hooks/pre-commit`.
**Estimated time:** 20분.

---

### Task 9: convert.py — markitdown 래퍼 (.docx) (TDD)

**Files:**
- Create: `Docs/Corpus/scripts/ingest/__init__.py`
- Create: `Docs/Corpus/scripts/ingest/convert.py`
- Create: `Docs/Corpus/scripts/ingest/tests/__init__.py`
- Create: `Docs/Corpus/scripts/ingest/tests/test_convert.py`
- Create: `Docs/Corpus/scripts/ingest/tests/fixtures/sample.docx` (mini .docx)

- [ ] **Step 1: 테스트용 .docx fixture 생성 스크립트**

`Docs/Corpus/scripts/ingest/tests/make_fixture.py`:
```python
from docx import Document
from pathlib import Path

d = Document()
d.add_heading("샘플 문서", level=1)
d.add_paragraph("이것은 변환 테스트용 .docx 파일입니다.")
d.add_heading("섹션 A", level=2)
d.add_paragraph("문단 하나.")
out = Path(__file__).parent / "fixtures" / "sample.docx"
out.parent.mkdir(exist_ok=True)
d.save(out)
print(f"wrote {out}")
```

requirements.txt에 `python-docx==1.1.2` 추가 후 실행:
```bash
.venv/Scripts/pip install python-docx
.venv/Scripts/python scripts/ingest/tests/make_fixture.py
```
Expected: `wrote .../sample.docx`.

- [ ] **Step 2: 실패 테스트 작성**

`Docs/Corpus/scripts/ingest/tests/test_convert.py`:
```python
from pathlib import Path
from ingest.convert import convert_to_markdown

FIXTURES = Path(__file__).parent / "fixtures"

def test_convert_docx_returns_markdown_with_heading():
    md, warnings = convert_to_markdown(FIXTURES / "sample.docx")
    assert "# 샘플 문서" in md or "샘플 문서" in md
    assert "섹션 A" in md
    assert warnings == []
```

- [ ] **Step 3: 실패 확인**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```
Expected: ModuleNotFoundError.

- [ ] **Step 4: 구현**

`Docs/Corpus/scripts/ingest/__init__.py` 빈 파일.

`Docs/Corpus/scripts/ingest/convert.py`:
```python
from __future__ import annotations
from pathlib import Path
from markitdown import MarkItDown

_md = MarkItDown()

SUPPORTED = {".docx", ".pdf", ".pptx", ".xlsx", ".html", ".htm", ".txt", ".md"}

def convert_to_markdown(src: Path) -> tuple[str, list[str]]:
    """Return (markdown_text, warnings)."""
    ext = src.suffix.lower()
    if ext not in SUPPORTED:
        return "", [f"unsupported extension: {ext}"]

    result = _md.convert(str(src))
    text = result.text_content
    warnings: list[str] = []
    if len(text.strip()) < 50:
        warnings.append(f"very short output ({len(text)} chars) — conversion likely failed")
    return text, warnings
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```
Expected: 1 passed.

- [ ] **Step 6: 커밋**

```bash
git add scripts/ingest/ scripts/requirements.txt
git commit -m "feat: ingest.convert — .docx → markdown via markitdown"
```

**Verification:** 1 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 30분.

---

### Task 10: convert.py — .hwp 처리 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/ingest/convert.py`
- Modify: `Docs/Corpus/scripts/ingest/tests/test_convert.py`
- Modify: `Docs/Corpus/scripts/requirements.txt`

- [ ] **Step 1: requirements.txt에 hwp5 추가**

```
pyhwp==0.1b16
```

설치:
```bash
.venv/Scripts/pip install pyhwp
```

- [ ] **Step 2: .hwp 샘플 fixture를 실제 vault `_raw/`에서 복사 (Step 17에서 이미 .hwp가 있음 — 그 전에 진행할 경우 임시 .hwp 한 개 사용)**

만약 fixture가 없다면 이 task는 *동작 검증을 실제 회의록 파일 .hwp* 로 진행하고 (Task 16에서 자연스럽게 연결), 테스트는 skipif로 처리.

`test_convert.py` 끝에 추가:
```python
import pytest, shutil

HWP_FIXTURE = FIXTURES / "sample.hwp"

@pytest.mark.skipif(not HWP_FIXTURE.exists(), reason="hwp fixture not available")
def test_convert_hwp_returns_korean_text():
    md, warnings = convert_to_markdown(HWP_FIXTURE)
    assert any("가" <= c <= "힣" for c in md), "no Korean chars in output"
```

- [ ] **Step 3: 실패 확인 (fixture 없으면 skip)**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```
Expected: 1 passed, 1 skipped (또는 fixture 있으면 1 failed).

- [ ] **Step 4: 구현 — .hwp 분기 추가**

`convert.py` 위쪽 import 다음에 추가:
```python
import subprocess
```

`SUPPORTED` 에 `.hwp` 추가:
```python
SUPPORTED = {".docx", ".pdf", ".pptx", ".xlsx", ".html", ".htm", ".txt", ".md", ".hwp"}
```

`convert_to_markdown` 내부, `_md.convert` 호출 전에 분기 추가:
```python
def convert_to_markdown(src: Path) -> tuple[str, list[str]]:
    ext = src.suffix.lower()
    if ext not in SUPPORTED:
        return "", [f"unsupported extension: {ext}"]

    if ext == ".hwp":
        return _convert_hwp(src)

    result = _md.convert(str(src))
    text = result.text_content
    warnings: list[str] = []
    if len(text.strip()) < 50:
        warnings.append(f"very short output ({len(text)} chars) — conversion likely failed")
    return text, warnings


def _convert_hwp(src: Path) -> tuple[str, list[str]]:
    try:
        out = subprocess.check_output(
            ["hwp5txt", str(src)], text=True, encoding="utf-8", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return "", [f"hwp5txt failed: {e}"]
    warnings = ["hwp conversion: manual review required — formatting limited to plain text"]
    return out, warnings
```

- [ ] **Step 5: 테스트 통과 확인 (fixture 있을 때)**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```

- [ ] **Step 6: 커밋**

```bash
git add scripts/ingest/convert.py scripts/ingest/tests/ scripts/requirements.txt
git commit -m "feat: ingest.convert — .hwp via hwp5txt"
```

**Verification:** pytest 통과 (또는 fixture 없으면 skip).
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 30분.

---

### Task 11: convert.py — REVIEW.md 자동 생성 + ledger (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/ingest/convert.py`
- Modify: `Docs/Corpus/scripts/ingest/tests/test_convert.py`

- [ ] **Step 1: 실패 테스트 추가**

```python
def test_run_ingest_creates_converted_dir_and_review(tmp_path):
    from ingest.convert import run_ingest
    raw = tmp_path / "_raw"
    raw.mkdir()
    converted = tmp_path / "_converted"

    # 샘플 docx fixture를 복사
    src = FIXTURES / "sample.docx"
    target = raw / "260513_샘플.docx"
    target.write_bytes(src.read_bytes())

    processed = run_ingest(raw, converted, ledger_path=tmp_path / ".ledger.json")

    assert len(processed) == 1
    out_dir = converted / "260513_샘플"
    assert (out_dir / "content.md").exists()
    assert (out_dir / "meta.yaml").exists()
    assert (out_dir / "REVIEW.md").exists()

def test_run_ingest_skips_already_processed(tmp_path):
    from ingest.convert import run_ingest
    raw = tmp_path / "_raw"
    raw.mkdir()
    converted = tmp_path / "_converted"
    src = FIXTURES / "sample.docx"
    (raw / "x.docx").write_bytes(src.read_bytes())

    run_ingest(raw, converted, ledger_path=tmp_path / ".ledger.json")
    processed_2 = run_ingest(raw, converted, ledger_path=tmp_path / ".ledger.json")
    assert processed_2 == []
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```
Expected: 2 failed.

- [ ] **Step 3: 구현 추가**

`convert.py` 끝에 추가:
```python
import json, time, datetime

def _make_review(src: Path, warnings: list[str]) -> str:
    lines = [
        f"# 검토 체크리스트 — {src.stem}",
        "",
        "## 자동 경고",
    ]
    if warnings:
        for w in warnings:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("- 없음")
    lines += [
        "",
        "## 검토 항목",
        "- [ ] 표가 제대로 변환됐는가",
        "- [ ] 헤딩 레벨이 의미 있게 들어갔는가",
        "- [ ] frontmatter 채움 (type / date / deciders / related)",
        "- [ ] 분류 폴더 결정 (decisions / specs / meetings / ...)",
        "- [ ] [[백링크]] 추가",
        "- [ ] 검토 완료 후 분류 폴더로 이동, _converted/ 디렉토리 삭제",
    ]
    return "\n".join(lines) + "\n"

def _load_ledger(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def _save_ledger(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def run_ingest(raw_dir: Path, converted_dir: Path, ledger_path: Path) -> list[Path]:
    converted_dir.mkdir(exist_ok=True)
    ledger = _load_ledger(ledger_path)
    processed: list[Path] = []

    for src in raw_dir.iterdir():
        if not src.is_file() or src.name == ".gitkeep":
            continue
        mtime = src.stat().st_mtime
        key = src.name
        if ledger.get(key, {}).get("mtime") == mtime:
            continue  # already processed

        md, warnings = convert_to_markdown(src)

        out_dir = converted_dir / src.stem
        out_dir.mkdir(exist_ok=True)
        (out_dir / "content.md").write_text(md, encoding="utf-8")
        (out_dir / "meta.yaml").write_text(
            f"source: {src.name}\nconverted_at: {datetime.datetime.utcnow().isoformat()}Z\n"
            f"warnings: {warnings}\n",
            encoding="utf-8")
        (out_dir / "REVIEW.md").write_text(_make_review(src, warnings), encoding="utf-8")

        ledger[key] = {"mtime": mtime, "warnings": warnings}
        processed.append(src)

    _save_ledger(ledger_path, ledger)
    return processed
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/pytest scripts/ingest/tests/test_convert.py -v
```
Expected: 2 more passed (총 3+).

- [ ] **Step 5: 커밋**

```bash
git add scripts/ingest/
git commit -m "feat: ingest.run_ingest — REVIEW.md + ledger-based skipping"
```

**Verification:** 모든 pytest 통과.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 35분.

---

### Task 12: convert.py CLI 통합

**Files:**
- Modify: `Docs/Corpus/scripts/ingest/convert.py`
- Create: `Docs/Corpus/scripts/ingest/__main__.py`

- [ ] **Step 1: `__main__.py` 작성**

`Docs/Corpus/scripts/ingest/__main__.py`:
```python
from pathlib import Path
from ingest.convert import run_ingest

def main(argv: list[str] | None = None) -> int:
    import sys, argparse
    p = argparse.ArgumentParser()
    p.add_argument("--vault", default=".", help="vault root (default: cwd)")
    args = p.parse_args(argv)
    vault = Path(args.vault).resolve()
    processed = run_ingest(
        raw_dir=vault / "_raw",
        converted_dir=vault / "_converted",
        ledger_path=vault / "_converted" / ".ledger.json")
    if processed:
        print(f"Processed {len(processed)} new files:")
        for s in processed:
            print(f"  • {s.name}")
        print(f"\n→ 검토: _converted/<file>/REVIEW.md")
    else:
        print("No new files to process.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: 실제 vault에 빈 dry-run**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
.venv/Scripts/python -m ingest --vault .
```
Expected: `No new files to process.` (vault _raw가 비어있으니).

- [ ] **Step 3: 커밋**

```bash
git add scripts/ingest/__main__.py
git commit -m "feat: ingest CLI — python -m ingest --vault ."
```

**Verification:** CLI 출력 정상.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 15분.

---

### Task 13: GitHub Actions — check.yml

**Files:**
- Create: `Docs/Corpus/.github/workflows/check.yml`

- [ ] **Step 1: workflow 작성**

`Docs/Corpus/.github/workflows/check.yml`:
```yaml
name: Corpus Integrity Check

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - name: Install deps
        run: pip install -r scripts/requirements.txt
      - name: Run pytest
        run: |
          cd scripts
          pytest -v
      - name: Run check_corpus on vault
        run: python scripts/check_corpus.py .
```

- [ ] **Step 2: 커밋 + push (선택 — origin 있을 때만)**

```bash
git add .github/workflows/check.yml
git commit -m "ci: add corpus integrity check workflow"
```

(remote 설정 후 push)

**Verification:** GitHub UI에서 PR/push마다 워크플로우 실행되는지 확인 (다음 push 때).
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 15분.

---

## Phase B — 콘텐츠 마이그레이션 (사람 작업 + LLM 보조)

콘텐츠 task는 TDD가 적용되지 않음. 대신 **체크리스트 + 검증 기준**으로 진행. LLM(Claude Code)에게 *변환된 markdown을 보면서 ADR 후보를 도출하라*고 요청 가능.

### Task 14: People 카드 4장 작성 (Step 1)

**Files:**
- Create: `Docs/Corpus/people/전남대병원.md`
- Create: `Docs/Corpus/people/RAPA.md`
- Create: `Docs/Corpus/people/FAMOZ.md`
- Create: `Docs/Corpus/people/레몬헬스케어.md`

- [ ] **Step 1: 4개 파일에 frontmatter + 기본 골격 작성**

각 파일의 frontmatter:
```yaml
---
type: org
role: 수요기관   # 전남대병원
# role: 발주기관 # RAPA
# role: 컨소시엄리드 / 개발사 # FAMOZ
# role: 컨소시엄  # 레몬헬스케어
---
```

본문 골격:
```markdown
# {조직명}

## 역할
- 사업 내에서의 위치
- 의사결정 권한 범위

## 주요 연락점
- 담당자, 연락 채널 (필요시)

## 관련 산출물
- [[_raw/...]] (관련된 원본 문서들 wikilink)

## 관련 결정
- [[decisions/...]]  ← 이 조직이 deciders로 참여한 ADR
```

- [ ] **Step 2: LLM에게 회의록·R&R 문서 기반 보강 요청 (Claude Code)**

```
프롬프트 예: "people/전남대병원.md 를 Docs/260518_RAPA_R&R_정의서_v2_FAMOZ.docx 와 
              Docs/260518_RAPA_스마트병원AI_회의록.hwp 의 내용을 참고해 채워줘."
```

- [ ] **Step 3: 검증**

```bash
.venv/Scripts/python scripts/check_corpus.py .
```
Expected: `0 errors` (사람 카드들이 frontmatter 정상).

- [ ] **Step 4: 커밋**

```bash
git add people/
git commit -m "content: add 4 organization cards (전남대병원, RAPA, FAMOZ, 레몬헬스케어)"
```

**Verification:** check_corpus 통과 + 4개 파일 존재.
**Rollback:** `git rm people/*.md && git commit -m "revert"`.
**Estimated time:** 1~2시간 (사람 검토 시간 포함).

---

### Task 15: 회의·R&R 관련 원본 8개를 `_raw/` 로 이주 + 변환 실행

**Files:**
- Copy: `Docs/260*.{docx,pdf,hwp}` → `Docs/Corpus/_raw/`
- Generated: `Docs/Corpus/_converted/...`

**대상 8개 (회의·R&R 우선)**:
- `260513_스마트병원_개발협의_아젠다.docx`
- `260514_스마트병원_개발협의_아젠다.docx`
- `260518_RAPA_R&R_정의서_v2_FAMOZ.docx`
- `260518_RAPA_스마트병원AI_회의록.hwp`
- `260518_RAPA_위치기반서비스_검토.docx`
- `260518_위치기반서비스_신고의무_검토_v1.0.docx`
- `260526_SDK개발_사전문의_.docx`
- (필요시 `260513_Domain_RAG_ARCHITECTURE.md` — 이미 .md니 변환 불필요, 직접 이주 가능)

- [ ] **Step 1: `_raw/`로 복사 (이동 아님 — Docs/ 원본 보존)**

PowerShell:
```powershell
$src = "D:\HB\P.RAPA_DEV\Docs"
$dst = "D:\HB\P.RAPA_DEV\Docs\Corpus\_raw"
$files = @(
  "260513_스마트병원_개발협의_아젠다.docx",
  "260514_스마트병원_개발협의_아젠다.docx",
  "260518_RAPA_R&R_정의서_v2_FAMOZ.docx",
  "260518_RAPA_스마트병원AI_회의록.hwp",
  "260518_RAPA_위치기반서비스_검토.docx",
  "260518_위치기반서비스_신고의무_검토_v1.0.docx",
  "260526_SDK개발_사전문의_.docx"
)
foreach ($f in $files) { Copy-Item "$src\$f" -Destination "$dst\$f" }
```

- [ ] **Step 2: ETL 실행**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
.venv/Scripts/python -m ingest --vault .
```
Expected: `Processed 7 new files:` + 각 파일의 변환 디렉토리 생성.

- [ ] **Step 3: 각 `_converted/*/REVIEW.md` 따라 검토 (사람 + LLM 보조)**

LLM 프롬프트 예:
```
"_converted/260518_RAPA_R&R_정의서_v2_FAMOZ/content.md 를 검토해서:
 1. 표가 깨졌으면 수정
 2. frontmatter 채움 (type, date, attendees 등)
 3. 분류 — 이건 R&R 문서이니 specs/r-and-r.md 가 적절할지, 또는 decisions/로 갈지 판단해줘"
```

- [ ] **Step 4: 분류된 파일 → 각 폴더로 이동**

회의 아젠다·회의록 → `meetings/2026-MM-DD-주제.md`
R&R 정의서 → `specs/r-and-r.md` 또는 별도 처리
위치기반서비스 검토 → `domain/위치기반서비스-신고의무.md`

각 파일은 `_converted/` 에서 git mv 로 이동, `_converted/<dir>/` 비우기.

- [ ] **Step 5: check_corpus 통과 확인**

```bash
.venv/Scripts/python scripts/check_corpus.py .
```
Expected: `0 errors` (warnings는 orphan raw 0개여야 — 모든 _raw가 어떤 노트에서 인용되어야).

- [ ] **Step 6: 커밋 (의미 단위로 쪼개기)**

```bash
git add _raw/
git commit -m "ingest: copy 7 source files (meetings/R&R/위치기반) → _raw/"

git add meetings/
git commit -m "content: 7 meetings from May 2026"

git add specs/  # 새로 만든 specs 있을 시
git commit -m "content: r-and-r spec (from 260518_RAPA_R&R_정의서_v2)"

git add domain/  # 새로 만든 domain 노트 있을 시
git commit -m "content: 위치기반서비스 신고의무 검토"
```

**Verification:** check_corpus 0 errors + 7개 회의록/스펙 노트 작성됨.
**Rollback:** 커밋들을 거꾸로 `git reset --hard <previous>`.
**Estimated time:** 3~5일 (분량 큰 작업).

---

### Task 16: ADR 발굴 — retroactive 5~10건 작성 (Step 3, 가장 중요)

**Files:**
- Create: `Docs/Corpus/decisions/0001-rag-backbone-bm25-dense.md`
- Create: `Docs/Corpus/decisions/0002-positioning-camera-free.md`
- Create: `Docs/Corpus/decisions/0003-r-and-r-FAMOZ-led.md` (예시 — 회의록 보고 정함)
- ... (회의 검토 중 식별된 결정사항)

목표: 사용자 통증의 핵심 해소 — 머릿속 결정사항을 처음으로 외부화.

- [ ] **Step 1: 후보 도출 — LLM에게 회의록·아키텍처 md 기반 ADR 후보 추출 요청**

Claude Code 프롬프트:
```
"Docs/Corpus/meetings/ 전체와 Docs/260513_Domain_RAG_ARCHITECTURE.md 를 읽고
 retroactive ADR 후보 5~10건을 도출해줘.
 각 후보에 대해:
 - 짧은 제목 (kebab-case)
 - status (대부분 accepted, 일부는 superseded)
 - 컨텍스트·옵션·결정·근거 요약
 - 관련 회의록/스펙 wikilink
 출력은 markdown 표로."
```

- [ ] **Step 2: 사용자 검토 — 후보 중 실제 합의된 것만 선별**

각 후보를 다음 기준으로 통과/탈락:
- ☐ 실제로 합의된 결정인가 (의견·검토는 결정 아님)
- ☐ 시점이 명확한가
- ☐ 누가 deciders인지 식별 가능한가
- ☐ 영향받는 스펙이 있는가

- [ ] **Step 3: 각 ADR을 `.obsidian/templates/adr.md` 템플릿으로 작성**

LLM 보조 가능:
```
"templates/adr.md 형식으로 0001-rag-backbone-bm25-dense.md 작성해줘.
 근거: 260513_Domain_RAG_ARCHITECTURE.md.
 deciders: [[FAMOZ]]"
```

- [ ] **Step 4: supersede 관계 정리 (필요시)**

만약 0003 → 0007 같은 진화가 있다면 supersedes/superseded_by 양쪽 채움.
무결성 체크가 잡아줄 것.

- [ ] **Step 5: check_corpus 통과 확인**

```bash
.venv/Scripts/python scripts/check_corpus.py .
```
Expected: `0 errors`. supersedes 한쪽만 있는 경우가 있으면 잡아냄.

- [ ] **Step 6: 각 ADR 별로 commit (audit trail 명확하게)**

```bash
git add decisions/0001-rag-backbone-bm25-dense.md
git commit -m "adr: 0001 rag-backbone-bm25-dense accepted"

git add decisions/0002-positioning-camera-free.md
git commit -m "adr: 0002 positioning-camera-free accepted"

# ...
```

**Verification:** check_corpus 통과 + 5~10건 ADR 파일 존재.
**Rollback:** 각 commit 별로 `git revert`.
**Estimated time:** 5~7일 (도출·검토·작성).

---

### Task 17: 살아있는 스펙 4개 작성 (Step 4)

**Files:**
- Create: `Docs/Corpus/specs/domain-rag-api.md`
- Create: `Docs/Corpus/specs/indoor-positioning.md`
- Create: `Docs/Corpus/specs/push-service.md`
- Create: `Docs/Corpus/specs/system-architecture.md`

- [ ] **Step 1: `specs/domain-rag-api.md` 작성**

소스: `Docs/260513_Domain_RAG_ARCHITECTURE.md` 의 정수 + 0001 ADR
`.obsidian/templates/spec.md` 사용. frontmatter:
```yaml
---
type: spec
status: living
last_reviewed: 2026-05-28
owner: "[[FAMOZ]]"
implements: ["[[0001-rag-backbone-bm25-dense]]"]
version: v1
---
```

- [ ] **Step 2: `specs/indoor-positioning.md` 작성**

소스: `Indoor_Positioning/Research/camera_free_indoor_localization_research_roadmap.md` + 0002 ADR.

- [ ] **Step 3: `specs/push-service.md` 작성**

소스: `Docs/Received/전남대학교병원_푸시서비스_개발가이드.docx` (필요시 _raw/로 추가 흡수). 관련 ADR이 있다면 implements 채움, 없으면 *이 spec이 ADR을 만들어야 한다*는 신호.

- [ ] **Step 4: `specs/system-architecture.md` 작성**

소스: `Docs/스마트병원AI_시스템구성도_v4.pptx` → 이미지 + 텍스트 요약.

`.pptx` → 이미지 변환:
```bash
.venv/Scripts/python -m ingest --vault .   # 만약 _raw에 .pptx 흡수했다면
```

- [ ] **Step 5: 각 spec 본문에 *implements* 가 가리키는 ADR 와의 일관성 확인**

LLM 프롬프트:
```
"specs/domain-rag-api.md 와 decisions/0001-rag-backbone-bm25-dense.md 의 내용이 모순되는지 확인해줘"
```

- [ ] **Step 6: check_corpus + commit**

```bash
.venv/Scripts/python scripts/check_corpus.py .

git add specs/
git commit -m "content: 4 living specs (domain-rag-api, indoor-positioning, push-service, system-architecture)"
```

**Verification:** 4개 specs 존재 + check_corpus 통과 + ADR과 모순 없음.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 5~7일.

---

## Phase C — RAG 인덱서 + Quartz 발행

### Task 18: scripts/rag/chunker.py — markdown chunking (TDD)

**Files:**
- Create: `Docs/Corpus/scripts/rag/__init__.py`
- Create: `Docs/Corpus/scripts/rag/chunker.py`
- Create: `Docs/Corpus/scripts/rag/tests/__init__.py`
- Create: `Docs/Corpus/scripts/rag/tests/test_chunker.py`

- [ ] **Step 1: 실패 테스트 작성**

`scripts/rag/tests/test_chunker.py`:
```python
from rag.chunker import chunk_markdown

SAMPLE = """\
# 0007 — Push Service

## 컨텍스트
컨텍스트 본문. 한국어 컨텍스트가 길게 이어진다고 가정.

## 결정
B를 채택.

## 결과
- 긍정: ...
- 부정: ...
"""

def test_chunks_split_at_heading_boundaries():
    chunks = chunk_markdown(SAMPLE, file_path="decisions/0007-test.md", target_tokens=200)
    assert len(chunks) >= 3
    # 첫 chunk은 컨텍스트 헤딩 포함
    assert "컨텍스트" in chunks[0]["text"]
    # breadcrumb이 들어가야
    assert "decisions/0007-test" in chunks[0]["chunk_id"]

def test_chunks_have_heading_path():
    chunks = chunk_markdown(SAMPLE, file_path="decisions/0007-test.md", target_tokens=200)
    by_heading = {c["heading_path"][-1]: c for c in chunks if c["heading_path"]}
    assert "결정" in by_heading
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_chunker.py -v
```

- [ ] **Step 3: 구현**

`scripts/rag/__init__.py` 빈 파일.

`scripts/rag/chunker.py`:
```python
from __future__ import annotations
import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

def _est_tokens(text: str) -> int:
    """한국어 거친 추정: 1.5자 = 1토큰."""
    return int(len(text) / 1.5)

def chunk_markdown(text: str, file_path: str, target_tokens: int = 1000, overlap: int = 200) -> list[dict]:
    """Split markdown by heading boundaries; return list of chunk dicts."""
    # 헤딩 위치 인덱스
    spans = []
    for m in HEADING_RE.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        spans.append((m.start(), level, title))
    spans.append((len(text), 0, ""))  # sentinel

    sections: list[tuple[list[str], str]] = []  # (heading_path, text)
    stack: list[str] = []

    for i in range(len(spans) - 1):
        start, level, title = spans[i]
        end, _, _ = spans[i + 1]
        section_text = text[start:end].strip()
        # 헤딩 path 갱신
        stack = stack[:level - 1] if level else stack
        if level:
            stack = stack + [title]
        sections.append((list(stack), section_text))

    # 한 섹션이 target보다 크면 그대로 1 chunk (코드블록 안전 우선)
    # 작으면 인접 섹션 묶음 시도 — 단순 1:1 매핑부터 시작 (YAGNI)
    chunks: list[dict] = []
    file_stem = file_path.split("/")[-1].rsplit(".", 1)[0]
    for idx, (path, body) in enumerate(sections):
        if not body:
            continue
        bc = "/".join(path)
        chunk_text = f"[{file_stem} > {bc}]\n\n{body}" if bc else body
        chunks.append({
            "chunk_id": f"{file_path}#{bc}:{idx}",
            "file_path": file_path,
            "heading_path": path,
            "text": chunk_text,
            "est_tokens": _est_tokens(chunk_text),
        })
    return chunks
```

- [ ] **Step 4: 통과 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_chunker.py -v
```
Expected: 2 passed.

- [ ] **Step 5: 커밋**

```bash
git add scripts/rag/
git commit -m "feat: rag.chunker — heading-boundary markdown chunking"
```

**Verification:** 2 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 35분.

---

### Task 19: scripts/rag/build_index.py — BM25 + Dense (TDD)

**Files:**
- Create: `Docs/Corpus/scripts/rag/build_index.py`
- Create: `Docs/Corpus/scripts/rag/tests/test_build_index.py`

- [ ] **Step 1: 실패 테스트 작성**

`scripts/rag/tests/test_build_index.py`:
```python
from pathlib import Path
from rag.build_index import build_index, load_index

def test_build_index_creates_artifacts(tmp_path):
    # 미니 vault
    vault = tmp_path / "vault"
    (vault / "decisions").mkdir(parents=True)
    (vault / "decisions" / "0001.md").write_text(
        "---\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0001\n본문 한국어.",
        encoding="utf-8")

    out = tmp_path / "index"
    build_index(vault, out)
    assert (out / "chunks.jsonl").exists()
    assert (out / "bm25.pkl").exists()

def test_load_index_returns_chunks_and_bm25(tmp_path):
    vault = tmp_path / "vault"
    (vault / "decisions").mkdir(parents=True)
    (vault / "decisions" / "0001.md").write_text(
        "---\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0001\n푸시 서비스 결정.",
        encoding="utf-8")
    out = tmp_path / "index"
    build_index(vault, out)
    chunks, bm25 = load_index(out)
    assert len(chunks) >= 1
    scores = bm25.get_scores("푸시 서비스".split())
    assert any(s > 0 for s in scores)
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_build_index.py -v
```

- [ ] **Step 3: 구현 (Dense는 다음 step에서; 일단 BM25만)**

`scripts/rag/build_index.py`:
```python
from __future__ import annotations
from pathlib import Path
import json, pickle
import frontmatter
from rank_bm25 import BM25Okapi
from rag.chunker import chunk_markdown

EXCLUDED = {"_raw", "_converted", ".obsidian", ".git", "scripts", "docs", "node_modules"}

def _tokenize_ko(text: str) -> list[str]:
    """한국어 거친 토크나이저: 공백 + 2-gram 보조."""
    base = text.lower().split()
    grams = [text[i:i+2] for i in range(len(text) - 1)]
    return base + grams

def _walk_md(vault: Path):
    for md in vault.rglob("*.md"):
        if any(part in EXCLUDED for part in md.relative_to(vault).parts):
            continue
        yield md

def build_index(vault: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_chunks: list[dict] = []
    for md in _walk_md(vault):
        with md.open(encoding="utf-8") as f:
            post = frontmatter.load(f)
        rel = md.relative_to(vault).as_posix()
        chunks = chunk_markdown(post.content, file_path=rel)
        for c in chunks:
            c["meta"] = dict(post.metadata)
            c["obsidian_uri"] = f"obsidian://open?vault=Corpus&file={rel}"
            all_chunks.append(c)

    # chunks.jsonl
    with (out_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # BM25
    tokenized = [_tokenize_ko(c["text"]) for c in all_chunks]
    bm25 = BM25Okapi(tokenized) if tokenized else None
    with (out_dir / "bm25.pkl").open("wb") as f:
        pickle.dump(bm25, f)

def load_index(out_dir: Path) -> tuple[list[dict], BM25Okapi]:
    chunks = [json.loads(l) for l in (out_dir / "chunks.jsonl").open(encoding="utf-8")]
    with (out_dir / "bm25.pkl").open("rb") as f:
        bm25 = pickle.load(f)
    return chunks, bm25
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_build_index.py -v
```
Expected: 2 passed.

- [ ] **Step 5: 실제 vault에 빌드 실행 (사람 sanity check)**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
.venv/Scripts/python -c "from pathlib import Path; from rag.build_index import build_index; build_index(Path('.'), Path('scripts/rag/index'))"
ls scripts/rag/index/
```
Expected: `chunks.jsonl`, `bm25.pkl` 생성. chunks.jsonl 라인 수가 vault의 노트 수와 대충 매치.

- [ ] **Step 6: 커밋 (인덱스 산출물은 gitignore되어 있음 확인)**

```bash
git status                          # scripts/rag/index/ 가 untracked로도 안 떠야 함
git add scripts/rag/build_index.py scripts/rag/tests/
git commit -m "feat: rag.build_index — BM25 + chunks.jsonl"
```

**Verification:** 2 passed + 실제 vault에서 인덱스 빌드 성공.
**Rollback:** `git reset --hard HEAD~1` + `rm -rf scripts/rag/index/`.
**Estimated time:** 40분.

---

### Task 20: build_index에 Dense (sentence-transformers + FAISS) 추가 (TDD)

**Files:**
- Modify: `Docs/Corpus/scripts/rag/build_index.py`
- Modify: `Docs/Corpus/scripts/rag/tests/test_build_index.py`

- [ ] **Step 1: 실패 테스트 추가**

```python
def test_dense_index_returns_relevant_chunk(tmp_path):
    vault = tmp_path / "vault"
    (vault / "decisions").mkdir(parents=True)
    (vault / "decisions" / "0001.md").write_text(
        "---\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0001\n푸시 알림 전송 결정.",
        encoding="utf-8")
    (vault / "decisions" / "0002.md").write_text(
        "---\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0002\n실내 측위 카메라프리.",
        encoding="utf-8")
    out = tmp_path / "index"
    build_index(vault, out)
    chunks, bm25, dense = load_index(out)
    # 의미 검색
    from rag.build_index import dense_search
    top = dense_search(dense, chunks, "알림 보내는 방법", k=1)
    assert "푸시" in top[0]["text"]
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_build_index.py::test_dense_index_returns_relevant_chunk -v
```

- [ ] **Step 3: 구현 추가**

`build_index.py` 위쪽 import 추가:
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "jhgan/ko-sroberta-multitask"  # 한국어 SBERT
```

`build_index` 끝에 dense 추가:
```python
    # Dense
    model = SentenceTransformer(EMBED_MODEL)
    if all_chunks:
        embeds = model.encode([c["text"] for c in all_chunks], normalize_embeddings=True)
        dim = embeds.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeds.astype(np.float32))
        faiss.write_index(index, str(out_dir / "dense.faiss"))
```

`load_index` 수정:
```python
def load_index(out_dir: Path):
    chunks = [json.loads(l) for l in (out_dir / "chunks.jsonl").open(encoding="utf-8")]
    with (out_dir / "bm25.pkl").open("rb") as f:
        bm25 = pickle.load(f)
    dense = faiss.read_index(str(out_dir / "dense.faiss")) if (out_dir / "dense.faiss").exists() else None
    return chunks, bm25, dense

_model_cache: dict[str, SentenceTransformer] = {}
def _get_model() -> SentenceTransformer:
    if EMBED_MODEL not in _model_cache:
        _model_cache[EMBED_MODEL] = SentenceTransformer(EMBED_MODEL)
    return _model_cache[EMBED_MODEL]

def dense_search(dense, chunks: list[dict], query: str, k: int = 5) -> list[dict]:
    model = _get_model()
    q = model.encode([query], normalize_embeddings=True).astype(np.float32)
    scores, idxs = dense.search(q, k)
    return [chunks[i] for i in idxs[0] if i >= 0]
```

- [ ] **Step 4: 테스트 (기존 BM25 테스트는 load_index unpacking이 3-tuple로 바뀌니까 수정)**

기존 두 테스트의 load_index 호출도 3-tuple로 업데이트:
```python
chunks, bm25, dense = load_index(out)
```

```bash
.venv/Scripts/pytest scripts/rag/tests/test_build_index.py -v
```
Expected: 3 passed.

- [ ] **Step 5: 커밋**

```bash
git add scripts/rag/
git commit -m "feat: rag.build_index — dense FAISS index via ko-sroberta"
```

**Verification:** 3 passed.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 40분.

---

### Task 21: scripts/rag/serve.py — FastAPI `/ask` (corpus 모드)

**Files:**
- Create: `Docs/Corpus/scripts/rag/serve.py`
- Create: `Docs/Corpus/scripts/rag/tests/test_serve.py`

- [ ] **Step 1: 실패 테스트 작성**

```python
from fastapi.testclient import TestClient
import pytest, os

@pytest.fixture
def client(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    (vault / "decisions").mkdir(parents=True)
    (vault / "decisions" / "0001.md").write_text(
        "---\ntype: decision\nstatus: accepted\ndate: 2026-05-28\n---\n# 0001\n푸시 알림 전송.",
        encoding="utf-8")
    out = tmp_path / "index"
    from rag.build_index import build_index
    build_index(vault, out)
    monkeypatch.setenv("CORPUS_INDEX_DIR", str(out))
    monkeypatch.setenv("CORPUS_VAULT_DIR", str(vault))

    from rag.serve import app
    return TestClient(app)

def test_ask_returns_citations(client):
    r = client.post("/ask", json={"mode": "corpus", "question": "알림", "top_k": 2})
    assert r.status_code == 200
    body = r.json()
    assert "citations" in body
    assert len(body["citations"]) >= 1
    assert "obsidian_uri" in body["citations"][0]
```

- [ ] **Step 2: 실패 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_serve.py -v
```

- [ ] **Step 3: 구현 (LLM 응답은 placeholder — retrieval만 동작)**

`scripts/rag/serve.py`:
```python
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from rag.build_index import load_index, dense_search, _tokenize_ko

app = FastAPI(title="P.RAPA Corpus RAG", version="0.1")

_state: dict = {}

def _ensure_loaded():
    if "chunks" in _state:
        return
    out_dir = Path(os.environ["CORPUS_INDEX_DIR"])
    chunks, bm25, dense = load_index(out_dir)
    _state["chunks"] = chunks
    _state["bm25"] = bm25
    _state["dense"] = dense

class AskRequest(BaseModel):
    mode: str = "corpus"
    question: str
    top_k: int = 5

class Citation(BaseModel):
    chunk_id: str
    file_path: str
    obsidian_uri: str
    score: float
    snippet: str

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]

def _rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda i: -scores[i])

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if req.mode != "corpus":
        return AskResponse(answer=f"unsupported mode: {req.mode}", citations=[])
    _ensure_loaded()
    chunks = _state["chunks"]
    bm25 = _state["bm25"]
    dense = _state["dense"]

    # BM25 ranking
    bm25_scores = bm25.get_scores(_tokenize_ko(req.question))
    bm25_rank = sorted(range(len(chunks)), key=lambda i: -bm25_scores[i])[:50]

    # Dense ranking
    dense_top = dense_search(dense, chunks, req.question, k=50)
    dense_rank = [chunks.index(c) for c in dense_top]

    # RRF
    merged = _rrf([bm25_rank, dense_rank])[:req.top_k]
    citations = [
        Citation(
            chunk_id=chunks[i]["chunk_id"],
            file_path=chunks[i]["file_path"],
            obsidian_uri=chunks[i]["obsidian_uri"],
            score=float(bm25_scores[i]),
            snippet=chunks[i]["text"][:200])
        for i in merged
    ]
    # 본 plan에서는 LLM 호출 부분은 stub — Domain_RAG가 LLM 통합 가능해지면 그쪽으로 이관
    answer = f"[retrieval-only mode] top {len(citations)} chunks returned."
    return AskResponse(answer=answer, citations=citations)
```

- [ ] **Step 4: 통과 확인**

```bash
.venv/Scripts/pytest scripts/rag/tests/test_serve.py -v
```
Expected: passed.

- [ ] **Step 5: 로컬 실행 확인**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus
$env:CORPUS_INDEX_DIR="$PWD/scripts/rag/index"
.venv/Scripts/uvicorn rag.serve:app --reload --app-dir scripts --port 8765
```

별도 터미널에서:
```bash
curl -X POST http://localhost:8765/ask -H "Content-Type: application/json" -d '{\"mode\":\"corpus\",\"question\":\"push service\",\"top_k\":3}'
```
Expected: citations 배열 응답.

- [ ] **Step 6: 커밋**

```bash
git add scripts/rag/
git commit -m "feat: rag.serve — /ask endpoint with BM25+Dense RRF (retrieval-only)"
```

**Verification:** pytest + curl 응답 정상.
**Rollback:** `git reset --hard HEAD~1`.
**Estimated time:** 50분.

---

### Task 22: post-commit hook — 인덱스 incremental rebuild (단순화: 전체 재빌드)

**Files:**
- Create: `Docs/Corpus/scripts/hooks/post-commit`
- Modify: `Docs/Corpus/scripts/install_hooks.sh`

- [ ] **Step 1: hook 작성**

`Docs/Corpus/scripts/hooks/post-commit`:
```bash
#!/usr/bin/env bash
set -e
ROOT="$(git rev-parse --show-toplevel)"
PY="$ROOT/scripts/.venv/Scripts/python"
if [ ! -x "$PY" ]; then PY="$ROOT/scripts/.venv/bin/python"; fi
if [ ! -x "$PY" ]; then exit 0; fi

# 변경된 .md 중 vault에 해당하는 것만 있을 때 rebuild (단순 mtime 기반 — incremental은 yagni)
if git diff-tree --no-commit-id --name-only -r HEAD | grep -q '\.md$'; then
  echo "→ rebuilding RAG index..."
  "$PY" -c "from pathlib import Path; from rag.build_index import build_index; build_index(Path('$ROOT'), Path('$ROOT/scripts/rag/index'))" &
  disown
  echo "  (running in background)"
fi
```

(incremental은 YAGNI — 작은 vault에서 전체 rebuild 1~3분이면 충분, background 실행으로 사람 부담 0.)

- [ ] **Step 2: install_hooks.sh 업데이트**

```bash
cp "$ROOT/scripts/hooks/post-commit" "$ROOT/.git/hooks/post-commit"
chmod +x "$ROOT/.git/hooks/post-commit"
```

- [ ] **Step 3: 재설치 + 검증**

```bash
bash scripts/install_hooks.sh
# 더미 커밋해서 hook 동작 확인
echo "" >> README.md
git add README.md
git commit -m "test: trigger post-commit"
```
Expected: `→ rebuilding RAG index...` 출력, 백그라운드에서 인덱스 갱신.

- [ ] **Step 4: 더미 커밋 되돌리기**

```bash
git reset --hard HEAD~1
```

- [ ] **Step 5: 정상 커밋**

```bash
git add scripts/hooks/post-commit scripts/install_hooks.sh
git commit -m "feat: post-commit hook — auto rebuild RAG index"
```

**Verification:** 커밋시 background rebuild 메시지 출력.
**Rollback:** `git reset --hard HEAD~1` + `rm .git/hooks/post-commit`.
**Estimated time:** 20분.

---

### Task 23: Quartz 프로젝트 셋업 (별 디렉토리)

**Files:**
- Create: `D:\HB\P.RAPA_DEV\Docs\Corpus-Site\` (Quartz 4 clone)

- [ ] **Step 1: Quartz clone**

```bash
cd D:/HB/P.RAPA_DEV/Docs
git clone https://github.com/jackyzha0/quartz.git Corpus-Site
cd Corpus-Site
npm i
```
Expected: 설치 완료.

- [ ] **Step 2: `quartz.config.ts` 수정**

`Docs/Corpus-Site/quartz.config.ts` 의 `configuration` 객체:
```ts
const config: QuartzConfig = {
  configuration: {
    pageTitle: "P.RAPA Corpus",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "ko-KR",
    baseUrl: "rapa-corpus.famoz.kr",
    ignorePatterns: ["_raw", "_converted", "scripts", "docs/superpowers", "private", "templates", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Pretendard",
        body: "Pretendard",
        code: "JetBrains Mono",
      },
      colors: {
        // 기본값 유지 또는 사용자 취향
      },
    },
  },
  plugins: { /* 기본값 유지 */ },
}
export default config
```

- [ ] **Step 3: vault content를 Quartz `content/` 로 가리키기**

옵션 a (간단): vault 디렉토리를 통째 복사. 옵션 b (권장): Quartz의 `npx quartz build --directory ...` 사용.

`package.json` 의 스크립트에 추가:
```json
"scripts": {
  "build:vault": "quartz build --directory ../Corpus --output public",
  "serve:vault": "quartz build --directory ../Corpus --serve"
}
```

- [ ] **Step 4: 로컬 빌드**

```bash
npm run build:vault
```
Expected: `public/` 디렉토리에 정적 사이트 생성 + 콘솔에 에러 없음.

- [ ] **Step 5: 로컬 서빙 + 브라우저 확인**

```bash
npm run serve:vault
```
브라우저에서 http://localhost:8080 열어 MOC, decisions 트리, 검색 동작 확인.

- [ ] **Step 6: Corpus-Site 자체 commit**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus-Site
git add quartz.config.ts package.json
git commit -m "config: quartz for P.RAPA corpus (Korean fonts, vault path)"
```

**Verification:** http://localhost:8080 에 vault가 사이트로 보임.
**Rollback:** `Corpus-Site/` 디렉토리 삭제.
**Estimated time:** 1~2시간.

---

### Task 24: GitHub Actions publish.yml + Cloudflare Pages 연동

**Files:**
- Create: `Docs/Corpus-Site/.github/workflows/publish.yml`

- [ ] **Step 1: workflow 작성**

```yaml
name: Publish Quartz

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/checkout@v4
        with:
          # ⚠️ 사용자가 GitHub 레포 위치 확정 후 실제 org/repo 명으로 교체 필요
          # (spec §11 "GitHub 레포 위치 결정" 미결 항목)
          repository: REPLACE_ME_org/rapa-corpus
          path: Corpus
          token: ${{ secrets.CORPUS_VAULT_TOKEN }}    # vault repo 권한 토큰
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - name: Run vault integrity check first
        run: |
          pip install -r Corpus/scripts/requirements.txt
          python Corpus/scripts/check_corpus.py Corpus
      - run: npx quartz build --directory Corpus --output public
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: rapa-corpus
          directory: public
```

- [ ] **Step 2: Cloudflare 사전 설정 (수동, 콘솔)**

  1. Cloudflare Pages > Create project > Connect Git repository (Corpus-Site)
  2. Build command: `npm run build:vault`
  3. Output directory: `public`
  4. Custom domain: `rapa-corpus.famoz.kr`
  5. API token + account ID를 GitHub secrets에 저장

- [ ] **Step 3: 첫 배포 검증**

```bash
git push origin main
```
Expected: GitHub Actions UI 에 워크플로우 성공 + Cloudflare Pages 에 배포 완료.

- [ ] **Step 4: Access 정책 설정 (Cloudflare Zero Trust > Access)**

Application 추가:
- Domain: `rapa-corpus.famoz.kr`
- Policy: `Include > Emails ending in @famoz.com`, `@jnuh.kr`, `@rapa.or.kr`
- Identity: Email OTP

브라우저로 도메인 접속해 OTP 흐름 확인.

- [ ] **Step 5: 커밋 + push**

```bash
cd D:/HB/P.RAPA_DEV/Docs/Corpus-Site
git add .github/workflows/publish.yml
git commit -m "ci: Quartz build + Cloudflare Pages deploy"
git push
```

**Verification:** `rapa-corpus.famoz.kr` 접속 → OTP → vault 사이트 표시.
**Rollback:** Cloudflare Pages project 비활성화 + DNS 제거.
**Estimated time:** 2~3시간.

---

## 마이그레이션 순서 권장 (Phase 의존)

```
Task 1                      [환경]
  ↓
Task 2 → 3 → 4 → 5 → 6 → 7  [check_corpus 무결성 — 무엇을 먼저 만들지 알게 됨]
  ↓
Task 8                      [pre-commit hook — 이후 콘텐츠 작업 시 안전망]
  ↓
Task 9 → 10 → 11 → 12       [ETL — Phase B 시작 전 필수]
  ↓
Task 13                     [CI check.yml — 옵션, remote 있을 때]
  ↓
Task 14                     [people 카드 4장]
  ↓
Task 15                     [회의록 흡수 — ETL 실전]
  ↓
Task 16                     [ADR 발굴 — 사용자 통증 해소 정점]
  ↓
Task 17                     [살아있는 specs 4개]
  ↓
Task 18 → 19 → 20 → 21      [RAG 인덱서·서버]
  ↓
Task 22                     [post-commit hook]
  ↓
Task 23 → 24                [Quartz + Cloudflare]
```

**가장 큰 가치 / 가장 빠른 ROI**: Task 1~8 + 14~16 (인프라 기본 + 콘텐츠 핵심). RAG와 Quartz는 그 위에서 자연스럽게 얹힘.

---

## 자기 검토 — Spec 커버리지

| Spec 섹션 | 커버하는 Task |
|---|---|
| §3 아키텍처 | 전체 plan (3가지 책임 분리 유지) |
| §4 디렉토리 구조 | git skeleton (이미 완료) + Task 15·16·17 (콘텐츠 폴더 채움) |
| §5 결정 추적 컨벤션 | Task 2~7 (frontmatter, supersedes, wikilink 무결성), Task 16 (ADR 발굴) |
| §6 변환 ETL | Task 9~12 (markitdown + hwp5 + REVIEW + ledger + CLI) |
| §7 Quartz 발행 | Task 23~24 |
| §8 Domain_RAG 인덱서 | Task 18~22 (vault 자체에 구현 — spec과 조정 명시) |
| §9-2 마이그레이션 5단계 | Step 1=Task 14, Step 2=Task 15, Step 3=Task 16, Step 4=Task 17, Step 5=Task 18~24 |
| §9-3 운영 부담 | post-commit hook (Task 22) + GitHub Actions (Task 13, 24) |
| §9-4 실패 모드 가드 | Task 7·8 (CI 차단) + Task 22 (자동 rebuild) |

**미커버 항목 (의도적 미룸 — spec §11에 명시됨)**:
- GitHub 레포 위치 결정 → 사용자가 직접
- Cloudflare Access 정책 구체화 → Task 24 Step 4에서 사용자 결정
- Obsidian Sync 사용 여부 → 운영 중 결정
- 임베딩 모델 (현재 ko-sroberta 채택, 변경시 Task 20만 수정)

**전체 예상 시간**: Phase A 약 5시간 (코딩) + Phase B 약 2~3주 (콘텐츠) + Phase C 약 5시간 (코딩+배포) = **2~3주 총 캘린더 시간** (콘텐츠가 병목).
