#!/usr/bin/env python3
"""D:/HB/P.RAPA_DEV/Docs/ → Obsidian vault 일일 sync + GitHub push.

워크플로:
1. Docs/ 하위 스캔 → .md / .xlsx / .xlsm / .pdf / .docx 변경분만 vault에 복사
2. wbs_to_md.py 실행 (WBS xlsm → vault/WBS/)
3. vault 변경분 git commit + push
4. 로그: _obsidian_vault/.sync.log

사용법:
    python sync_docs_to_vault.py [--dry-run]

cron 등록 예 (매일 09:00):
    0 9 * * * cd /d D:\\HB\\P.RAPA_DEV && python _obsidian_vault\\Scripts\\sync_docs_to_vault.py
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
DOCS_ROOT = Path(r"D:/HB/P.RAPA_DEV/Docs")
VAULT = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault")
SCRIPT_WBS = VAULT / "Scripts" / "wbs_to_md.py"
XL_WBS = DOCS_ROOT / "OUTPUT" / "WBS" / "(2-3-1) 스마트병원동행AI앱_WBS_20260703_v0.7.xlsm"
DIFF_WBS = DOCS_ROOT / "OUTPUT" / "WBS" / "wbs_diff_10am_vs_5pm.json"
LOG_FILE = VAULT / ".sync.log"

# Sync rules: 상대 경로 → vault 내 매핑
# (DOCS_ROOT 내부 경로) → (VAULT 내 경로)
# 패턴 단순화: 최상위 1-depth 디렉토리는 그대로 매핑
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

# Include / Exclude
INCLUDE_EXT = {".md", ".xlsx", ".xlsm", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".zip"}
EXCLUDE_DIRS = {
    ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".tmp.drivedownload", ".tmp.driveupload", ".obsidian", ".git",
    "Thumbs.db", ".DS_Store",
    # 임시/중간 산출물
    "Legacy", "legacy", "_workspace", "_raw",
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
    s = str(p)
    # 디렉토리명 매치
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    # 파일명 패턴 매치
    name = p.name
    for pat in EXCLUDE_NAME_PATTERNS:
        if pat in name:
            return True
    return False


def scan_docs():
    """Docs/ 아래 변경된 파일 스캔."""
    if not DOCS_ROOT.exists():
        log(f"FATAL: {DOCS_ROOT} not found")
        sys.exit(1)
    files = []
    for path in DOCS_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded(path):
            continue
        if path.suffix.lower() not in INCLUDE_EXT:
            continue
        files.append(path)
    return files


def map_to_vault(src_path):
    """Docs/ 내부 src_path → vault 내 매핑 경로."""
    rel = src_path.relative_to(DOCS_ROOT)
    rel_str = str(rel).replace("\\", "/")
    # 매핑 룰
    for src_prefix, dst_dir in SYNC_MAP.items():
        if rel_str.startswith(src_prefix):
            sub = rel_str[len(src_prefix):].lstrip("/")
            return VAULT / dst_dir / sub
    # 매핑 안 되는 경로: 최상위 디렉토리 이름으로
    top = rel.parts[0] if len(rel.parts) > 1 else "_root"
    return VAULT / "_inbox" / rel


def sync_files(dry_run=False):
    """변경/추가 파일을 vault에 복사."""
    copied = 0
    skipped = 0
    errors = []
    for src in scan_docs():
        dst = map_to_vault(src)
        # 동일성: SHA256 비교
        if dst.exists() and sha256(dst) == sha256(src):
            skipped += 1
            continue
        try:
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            copied += 1
            log(f"  {'[DRY] ' if dry_run else ''}copy: {src.relative_to(DOCS_ROOT)} → {dst.relative_to(VAULT)}")
        except Exception as e:
            errors.append((src, str(e)))
            log(f"  ERROR copy {src}: {e}")
    return copied, skipped, errors


def run_wbs_to_md(dry_run=False):
    """wbs_to_md.py 실행."""
    if not XL_WBS.exists():
        log(f"WARN: WBS xlsm not found: {XL_WBS}")
        return False
    if not SCRIPT_WBS.exists():
        log(f"WARN: wbs_to_md.py not found: {SCRIPT_WBS}")
        return False
    out_dir = VAULT / "WBS"
    cmd = [sys.executable, str(SCRIPT_WBS), str(XL_WBS), str(out_dir)]
    if DIFF_WBS.exists():
        cmd.append(str(DIFF_WBS))
    log(f"  run: {' '.join(cmd)}")
    if dry_run:
        return True
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log(f"  ERROR wbs_to_md: {res.stderr}")
        return False
    log(f"  wbs_to_md OK: {res.stdout.strip()}")
    return True


def git_commit_push(dry_run=False, message=None):
    """vault 변경분 commit + push."""
    if dry_run:
        log("  [DRY] would commit + push")
        return True
    # 1. status
    res = subprocess.run(["git", "status", "--porcelain"], cwd=VAULT,
                         capture_output=True, text=True)
    if not res.stdout.strip():
        log("  no changes to commit")
        return True
    # 2. add + commit
    subprocess.run(["git", "add", "-A"], cwd=VAULT, check=True)
    msg = message or f"daily sync: {datetime.now().strftime('%Y-%m-%d')} (auto)"
    subprocess.run(
        ["git", "-c", "user.name=JangHyun-bin", "-c", "user.email=narnia0900@gmail.com",
         "commit", "-m", msg],
        cwd=VAULT, check=True
    )
    # 3. push
    res = subprocess.run(["git", "push", "origin", "main"], cwd=VAULT,
                         capture_output=True, text=True)
    if res.returncode != 0:
        log(f"  ERROR push: {res.stderr}")
        return False
    log(f"  push OK: {res.stdout.strip().splitlines()[-1] if res.stdout else 'OK'}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 복사/실행/commit/push 없이 로그만")
    parser.add_argument("--skip-push", action="store_true",
                        help="commit까지만, push 안 함")
    parser.add_argument("--skip-wbs", action="store_true",
                        help="wbs_to_md.py 실행 안 함")
    args = parser.parse_args()

    log(f"=== daily sync START (dry_run={args.dry_run}, skip_push={args.skip_push}, skip_wbs={args.skip_wbs}) ===")
    # 1. 파일 sync
    log("[1/3] file sync")
    copied, skipped, errors = sync_files(args.dry_run)
    log(f"  result: copied={copied}, skipped={skipped}, errors={len(errors)}")
    # 2. WBS 변환
    if not args.skip_wbs:
        log("[2/3] wbs_to_md")
        run_wbs_to_md(args.dry_run)
    else:
        log("[2/3] wbs_to_md SKIPPED")
    # 3. commit + push
    log("[3/3] git commit + push")
    if args.skip_push:
        log("  push SKIPPED (--skip-push)")
    else:
        git_commit_push(args.dry_run)
    log("=== daily sync END ===\n")


if __name__ == "__main__":
    main()
