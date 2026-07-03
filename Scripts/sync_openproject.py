"""OpenProject RAPA 프로젝트 + WBS 98 Work Package 자동 import.

사용법:
    1. OpenProject web UI에서 API token 발급 (Dashboard-OpenProject-Setup.md 참고)
    2. _curator/.openproject_token 파일에 token 저장 (한 줄)
    3. python sync_openproject.py [--dry-run] [--rebuild]

cron 예시: sync_intelligent.py의 stage 7에서 호출.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from datetime import datetime

import httpx

# Paths
VAULT = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault")
WBS_JSON = Path(r"D:/HB/P.RAPA_DEV/Docs/OUTPUT/WBS/wbs_v07_20260703_5pm_extracted.json")
TOKEN_FILE = VAULT / "_curator" / ".openproject_token"
OP_BASE = "http://localhost:8082"
PROJECT_NAME = "RAPA 스마트병원동행AI앱 (파모즈)"
PROJECT_IDENTIFIER = "rapa-smart-hospital-pamoz"

# Load token
def get_token():
    if not TOKEN_FILE.exists():
        print(f"ERROR: token file not found: {TOKEN_FILE}")
        print(f"  발급: {VAULT/'Dashboards/Dashboard-OpenProject-Setup.md'}")
        sys.exit(1)
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def api(method, path, **kw):
    token = get_token()
    # OpenProject v16 uses Basic auth with "apikey:<token>" (not Bearer)
    import base64
    creds = base64.b64encode(f"apikey:{token}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}",
               "Content-Type": "application/json"}
    url = f"{OP_BASE}/api/v3{path}"
    with httpx.Client(timeout=30) as c:
        r = c.request(method, url, headers=headers, **kw)
    if r.status_code >= 400:
        print(f"  HTTP {r.status_code} {method} {path}: {r.text[:200]}")
        r.raise_for_status()
    return r.json() if r.text else {}


def find_or_create_project(dry_run=False):
    """RAPA 프로젝트 찾기 또는 생성."""
    print(f"[project] {PROJECT_NAME}")
    # 기존 검색
    r = api("GET", "/projects")
    for p in r.get("_embedded", {}).get("elements", []):
        if p.get("name") == PROJECT_NAME or p.get("identifier") == PROJECT_IDENTIFIER:
            print(f"  exists: id={p['id']} identifier={p['identifier']}")
            return p
    if dry_run:
        print("  [DRY] would create project")
        return None
    # 생성
    body = {
        "name": PROJECT_NAME,
        "identifier": PROJECT_IDENTIFIER,
        "description": {
            "format": "markdown",
            "raw": "RAPA 2026 AI가상융합 사회기반혁신 — 스마트병원 동행 AI 앱 파일럿 (1차년도).\n\n"
                    "본 프로젝트는 파모즈 담당분만 등록. WBS v0.7 (2026-07-03 17:02) 기반."
        },
        "public": False,
    }
    r = api("POST", "/projects", json=body)
    print(f"  created: id={r['id']} identifier={r['identifier']}")
    return r


def create_work_package(project_id, code, t, parent_id=None, dry_run=False,
                        is_milestone=False):
    """L3 task를 work package로 생성.

    OpenProject v16 WP API: project/type/status는 _links (HATEOAS)로 보내야 함.
    단순 id는 constraint violation. description은 strong_required (null 불가).
    """
    body = {
        "subject": f"{code} {t.get('name') or code}",
        "description": {
            "format": "markdown",
            "raw": (f"**WBS**: {code}\n"
                    f"**기간**: {t['start']} ~ {t['end']}\n"
                    f"**담당**: {t.get('owner') or '-'}\n"
                    f"**계획 작업량**: {t.get('plan_work', '-')} MD\n"
                    f"**계획 기간**: {t.get('plan_dur', '-')} 일\n"
                    f"**산출물**: {t.get('deliverable') or '-'}\n")
        },
        "startDate": t["start"],
        "dueDate": t["end"],
        "percentageDone": 0,
        "_links": {
            "project": {"href": f"/api/v3/projects/{project_id}"},
            "type": {"href": f"/api/v3/types/{2 if is_milestone else 1}"},
            "status": {"href": "/api/v3/statuses/1"},  # "New"
        }
    }
    if parent_id:
        body["_links"]["parent"] = {"href": f"/api/v3/work_packages/{parent_id}"}
    if dry_run:
        marker = " [M]" if is_milestone else ""
        print(f"  [DRY] {code}{marker} ({t.get('name')})")
        return {"id": -1, "subject": body["subject"]}
    r = api("POST", "/work_packages?notify=false", json=body)
    print(f"  created: {code} id={r['id']}")
    return r


def import_wbs(dry_run=False, rebuild=False):
    wbs = json.loads(WBS_JSON.read_text(encoding="utf-8"))
    project = find_or_create_project(dry_run=dry_run)
    if not project:
        return
    project_id = project["id"]

    # 기존 WP 정리 (rebuild 모드)
    if rebuild and not dry_run:
        print("[cleanup] existing work packages")
        r = api("GET", f"/projects/{project_id}/work_packages", params={"pageSize": 200})
        for wp in r.get("_embedded", {}).get("elements", []):
            api("DELETE", f"/work_packages/{wp['id']}")

    # L1 (그룹) → L2 (그룹) → L3 (task) 계층
    parent_ids = {}  # code -> wp_id
    for level in [1, 2, 3]:
        for code, t in wbs.items():
            if t.get("level") != level:
                continue
            if not t.get("start") or not t.get("end"):
                continue
            # 부모 찾기
            parts = code.split(".")
            parent_code = ".".join(parts[:-1]) if len(parts) > 1 else None
            parent_id = parent_ids.get(parent_code) if parent_code else None
            try:
                wp = create_work_package(project_id, code, t, parent_id, dry_run)
                parent_ids[code] = wp["id"]
                time.sleep(0.1)  # rate limit
            except Exception as e:
                print(f"  ERROR {code}: {e}")
    print(f"\n=== import complete: {len(parent_ids)} tasks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rebuild", action="store_true",
                        help="기존 WP 삭제 후 재생성")
    args = parser.parse_args()
    import_wbs(dry_run=args.dry_run, rebuild=args.rebuild)


if __name__ == "__main__":
    main()
