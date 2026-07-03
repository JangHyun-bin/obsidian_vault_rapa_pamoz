#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vault 지능적 sync: LLM 요약 + 태깅 + Chroma 인덱싱 + cross-link 추천.

호출 시 venv 호환성: 이 스크립트는 hermes venv site-packages (chromadb, httpx)
에 의존한다. cron/subprocess에서 'python'으로 호출하면 uv의 다른 python이
잡혀 ModuleNotFoundError가 발생한다. 권장 호출은 Scripts/run_smart.sh 참조.

워크플로 (매 24시간 cron):
1. Docs/ 변경분 diff (mtime + SHA256)
2. 변경된 .md 파일마다 LLM 호출 (요약 + 카테고리 + 태그)
3. Chroma vector DB 인덱싱 (incremental)
4. _summaries/ 폴더에 요약 노트 생성
5. vault 동기화 (복사 + cross-link frontmatter)
6. git commit + push

사용법:
    python sync_intelligent.py [--dry-run] [--skip-push] [--rebuild-index]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# .env 자동 로드 (subprocess 격리 대비)
_env_path = Path(r"C:/Users/user/AppData/Local/hermes/.env")
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# Paths
DOCS_ROOT = Path(r"D:/HB/P.RAPA_DEV/Docs")
VAULT = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault")
CURATOR = VAULT / "_curator"
CHROMA_DIR = CURATOR / "chroma"
SUMMARIES_DIR = VAULT / "_summaries"
LOG_FILE = VAULT / ".sync.log"
STATE_FILE = CURATOR / ".index_state.json"

# OpenRouter (OpenAI compatible)
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3-haiku"

# Sync rules
SYNC_MAP = {
    "Corpus/decisions": "ADR",
    "Corpus/specs": "Specs",
    "Corpus/domain": "Corpus/Domain",
    "Corpus/evidence": "Corpus/Evidence",
    "Corpus/meetings": "Corpus/Meetings",
    "Corpus/docs": "Corpus/Docs",
    "Corpus/_raw": "Corpus/_raw",
    "Corpus/scripts/tests": "Corpus/Tests",
    "Corpus/MOC.md": "MOC.md",
    "Corpus/README.md": "Corpus-README.md",
    "Corpus/index.md": "Corpus-index.md",
    "OUTPUT/deliverables_external": "Deliverables/external",
    "OUTPUT/1.3_deliverables_draft": "Deliverables/1.3",
    "OUTPUT/WBS": "WBS-source",
    "OUTPUT/요구사항정의서": "Requirements",
    "OUTPUT/주간보고": "Reports/weekly",
    "OUTPUT/월간보고": "Reports/monthly",
    "OUTPUT/회의록": "Meetings",
    "OUTPUT/병원정보": "Hospital-info",
    "OUTPUT/병원_착수보고": "Reports/kickoff",
    "OUTPUT/파모즈_내부_산출물": "Internal",
}

INCLUDE_EXT = {".md", ".xlsx", ".xlsm", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".zip"}
EXCLUDE_DIRS = {
    ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".tmp.drivedownload", ".tmp.driveupload", ".obsidian", ".git",
    "Thumbs.db", ".DS_Store", "Legacy", "legacy", "_workspace", "_raw",
}
EXCLUDE_NAME_PATTERNS = ["~$", ".tmp.", "_drafts"]


def log(msg):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def sha256(p):
    h = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception:
        return None
    return h.hexdigest()


def is_excluded(p):
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    name = p.name
    for pat in EXCLUDE_NAME_PATTERNS:
        if pat in name:
            return True
    return False


def call_llm(prompt, system=None, model=DEFAULT_MODEL, max_tokens=400,
              temperature=0.2, timeout=60):
    """OpenRouter (OpenAI 호환) 호출."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        log("WARN: OPENROUTER_API_KEY not set, LLM skip")
        return None
    import httpx
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(f"{OPENROUTER_BASE}/chat/completions",
                            headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"  LLM error: {e}")
        return None


SUMMARIZE_PROMPT = """아래 마크다운 문서를 보고 다음 JSON 형식으로만 답해. 다른 텍스트 없이.

{
  "summary": "1-2줄 한국어 요약",
  "category": "ADR|Specs|Meeting|WBS|Deliverable|Report|Other",
  "tags": ["태그1", "태그2", "태그3"],
  "related_keywords": ["관련1", "관련2"]
}

문서:
```
{content}
```"""


def summarize_with_llm(content, max_chars=4000):
    """LLM으로 요약 + 태깅."""
    truncated = content[:max_chars]
    if len(content) > max_chars:
        truncated += "\n\n[... truncated ...]"
    prompt = SUMMARIZE_PROMPT.replace("{content}", truncated)
    raw = call_llm(prompt, system="문서 메타데이터 추출기. JSON만 답해.")
    if not raw:
        return None
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


_chroma_client = None
_chroma_collection = None


def get_chroma():
    global _chroma_client, _chroma_collection
    if _chroma_client is None:
        import chromadb
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _chroma_collection = _chroma_client.get_or_create_collection(
            name="vault",
            metadata={"hnsw:space": "cosine"},
        )
    return _chroma_collection


def chroma_index_file(path, rel_path, summary_meta, dry_run=False):
    """단일 파일을 Chroma에 인덱싱."""
    if dry_run:
        return
    try:
        col = get_chroma()
        content = path.read_text(encoding="utf-8", errors="ignore")[:8000]
        meta = {
            "path": str(path),
            "rel": rel_path,
            "category": (summary_meta or {}).get("category", "Other"),
            "summary": (summary_meta or {}).get("summary", "")[:500],
            "mtime": path.stat().st_mtime,
        }
        doc_id = hashlib.md5(rel_path.encode()).hexdigest()[:16]
        col.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[meta],
        )
    except Exception as e:
        log(f"  chroma error ({rel_path}): {e}")


def chroma_search(query, n=3):
    """top-k 의미 검색."""
    try:
        col = get_chroma()
        return col.query(query_texts=[query], n_results=n)
    except Exception as e:
        log(f"  chroma search error: {e}")
        return None


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"indexed": {}}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def scan_docs():
    if not DOCS_ROOT.exists():
        log(f"FATAL: {DOCS_ROOT} not found")
        sys.exit(1)
    files = []
    for path in DOCS_ROOT.rglob("*"):
        if not path.is_file() or is_excluded(path):
            continue
        if path.suffix.lower() not in INCLUDE_EXT:
            continue
        files.append(path)
    return files


def map_to_vault(src_path):
    rel = src_path.relative_to(DOCS_ROOT)
    rel_str = str(rel).replace("\\", "/")
    for src_prefix, dst_dir in SYNC_MAP.items():
        if rel_str.startswith(src_prefix):
            sub = rel_str[len(src_prefix):].lstrip("/")
            return VAULT / dst_dir / sub
    top = rel.parts[0] if len(rel.parts) > 1 else "_root"
    return VAULT / "_inbox" / rel


def make_summary_note(src_path, vault_dst, meta):
    """_summaries/<rel>.md 노트 생성 (LLM 결과)."""
    rel = src_path.relative_to(DOCS_ROOT)
    rel_str = str(rel).replace("\\", "/").replace("/", "__").rstrip(".md")
    summary_path = SUMMARIES_DIR / f"{rel_str}.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = [
        "---",
        f'original: "{rel_str}"',
        f"category: \"{meta.get('category', 'Other')}\"",
        f"tags: [{', '.join(meta.get('tags', []))}]",
        f"related: [{', '.join(meta.get('related_keywords', []))}]",
        f"indexed_at: \"{datetime.now().isoformat(timespec='seconds')}\"",
        "---",
    ]
    body = [
        f"# {rel}",
        "",
        f"**원본**: [[{vault_dst.relative_to(VAULT).as_posix()}|{rel}]]",
        "",
        "## 요약",
        meta.get("summary", "(no summary)"),
        "",
        "## 태그",
        ", ".join(meta.get("tags", [])) or "-",
        "",
        "## 관련 키워드",
        ", ".join(meta.get("related_keywords", [])) or "-",
        "",
    ]
    summary_path.write_text("\n".join(frontmatter + body), encoding="utf-8")
    return summary_path


def sync_intelligent(dry_run=False, skip_push=False, rebuild_index=False):
    log(f"=== intelligent sync START (dry={dry_run}, skip_push={skip_push}, rebuild={rebuild_index}) ===")
    state = load_state() if not rebuild_index else {"indexed": {}}

    files = scan_docs()
    log(f"  scanned {len(files)} files in Docs/")

    copied, skipped, summarized, indexed, errors = 0, 0, 0, 0, 0
    changed_files = []

    log("[1/5] file diff + copy")
    for src in files:
        rel = str(src.relative_to(DOCS_ROOT)).replace("\\", "/")
        src_sha = sha256(src)
        if state["indexed"].get(rel) == src_sha:
            skipped += 1
            continue
        dst = map_to_vault(src)
        if dst.exists() and sha256(dst) == src_sha:
            state["indexed"][rel] = src_sha
            skipped += 1
            continue
        try:
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            copied += 1
            changed_files.append((src, dst, src_sha))
        except Exception as e:
            errors += 1
            log(f"  copy error: {src}: {e}")
    log(f"  copied={copied}, skipped={skipped}, errors={errors}")

    log("[2/5] wbs_to_md")
    wbs_xlsm_dir = DOCS_ROOT / "OUTPUT" / "WBS"
    xlsm_files = sorted(wbs_xlsm_dir.glob("*.xlsm"))
    if not dry_run and xlsm_files:
        latest = xlsm_files[-1]
        diff = DOCS_ROOT / "OUTPUT" / "WBS" / "wbs_diff_10am_vs_5pm.json"
        cmd = [sys.executable, str(VAULT / "Scripts" / "wbs_to_md.py"),
               str(latest), str(VAULT / "WBS")]
        if diff.exists():
            cmd.append(str(diff))
        subprocess.run(cmd, capture_output=True, text=True)

    log("[3/5] LLM summarize + tag")
    md_changed = [(s, d, h) for s, d, h in changed_files
                  if s.suffix.lower() == ".md"]
    log(f"  {len(md_changed)} .md files to summarize")
    summaries = {}
    for src, dst, sha in md_changed:
        rel = str(src.relative_to(DOCS_ROOT)).replace("\\", "/")
        if not dry_run:
            content = src.read_text(encoding="utf-8", errors="ignore")
            meta = summarize_with_llm(content) or {
                "summary": "(LLM skip)",
                "category": "Other",
                "tags": [],
                "related_keywords": [],
            }
            summaries[rel] = meta
            try:
                make_summary_note(src, dst, meta)
            except Exception as e:
                log(f"  summary note error ({rel}): {e}")
            summarized += 1
            time.sleep(0.5)
    log(f"  summarized={summarized}")

    log("[4/5] Chroma index")
    if not dry_run:
        for src, dst, sha in changed_files:
            rel = str(src.relative_to(DOCS_ROOT)).replace("\\", "/")
            meta = summaries.get(rel)
            chroma_index_file(src, rel, meta)
            indexed += 1
            state["indexed"][rel] = sha
    log(f"  indexed={indexed}")

    log("[5/5] git commit + push")
    if not skip_push:
        save_state(state)
        if not dry_run:
            subprocess.run(["git", "add", "-A"], cwd=VAULT, check=False)
            res = subprocess.run(
                ["git", "-c", "user.name=JangHyun-bin",
                 "-c", "user.email=narnia0900@gmail.com",
                 "commit", "-m",
                 f"intelligent sync: {datetime.now().strftime('%Y-%m-%d')} "
                 f"({copied} copied, {summarized} summarized, {indexed} indexed)"],
                cwd=VAULT, capture_output=True, text=True
            )
            combined = (res.stdout or "") + (res.stderr or "")
            if "nothing to commit" in combined:
                log("  no changes to commit")
            else:
                push = subprocess.run(
                    ["git", "push", "origin", "main"], cwd=VAULT,
                    capture_output=True, text=True
                )
                if push.returncode == 0:
                    log("  push OK")
                else:
                    log(f"  push failed: {push.stderr[:200]}")
    else:
        log("  push SKIPPED")

    log("=== intelligent sync END ===\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-push", action="store_true")
    parser.add_argument("--rebuild-index", action="store_true",
                        help="Chroma 인덱스 전체 재빌드")
    args = parser.parse_args()
    sync_intelligent(dry_run=args.dry_run,
                     skip_push=args.skip_push,
                     rebuild_index=args.rebuild_index)


if __name__ == "__main__":
    main()
