"""Miro board에 RAPA WBS 98 task 자동 import.

Usage:
    python miro_import_wbs.py [--dry-run]

Output:
    - D:/HB/P.RAPA_DEV/_obsidian_vault/_curator/miro_import_wbs_log.json
    - 이미 만들어진 board가 있으면 log에서 읽어서 update만
    - 없으면 새로 생성

Layout:
    1 row = 1 L1 category (분석/설계 / 개발 / 테스트 / 홍보/특허)
    1 frame = 1 month (5월~12월)
    sticky = L3 task (3x3 grid per frame, 9 max)
    color: light_blue/green/yellow/pink (L1별)

Token: C:/Users/user/AppData/Local/hermes/secrets/miro_token
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import httpx

# ============== paths ==============
WBS_JSON = Path("D:/HB/P.RAPA_DEV/Docs/OUTPUT/WBS/wbs_v07_20260703_5pm_extracted.json")
LOG_FILE = Path("D:/HB/P.RAPA_DEV/_obsidian_vault/_curator/miro_import_wbs_log.json")
MIRO_TOKEN_FILE = Path("C:/Users/user/AppData/Local/hermes/secrets/miro_token")
MIRO_BASE = "https://api.miro.com/v2"

# ============== layout ==============
COL_MONTHS = ["5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
FRAME_BASE = (1200, 800)
FRAME_LARGE = (1500, 1000)
HEADER_W = 220
GAP_X, GAP_Y = 50, 80
CANVAS_PAD = 100
COLOR_L1 = {"1": "light_blue", "2": "light_green", "3": "light_yellow", "4": "light_pink"}


def parse_date(s):
    if not s: return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try: return datetime.strptime(s, fmt).date()
        except: pass
    return None


def month_idx(d):
    if not d: return None
    return (d.year - 2026) * 12 + (d.month - 5)


def xy(col, row):
    x = CANVAS_PAD + HEADER_W/2 + col * (FRAME_BASE[0] + GAP_X)
    y = CANVAS_PAD + row * (FRAME_BASE[1] + GAP_Y) + FRAME_BASE[1]/2
    return x, y


def api(method, path, **kw):
    token = MIRO_TOKEN_FILE.read_text(encoding="utf-8").strip()
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json", "Accept": "application/json"}
    url = f"{MIRO_BASE}{path}"
    with httpx.Client(timeout=30) as c:
        r = c.request(method, url, headers=headers, **kw)
    if r.status_code >= 400:
        print(f"  err {method} {path}: HTTP {r.status_code} {r.text[:200]}")
        return None
    return r.json() if r.text else {}


def get_all_items(board_id):
    items = []
    cursor = None
    while True:
        params = {"limit": 50}
        if cursor: params["cursor"] = cursor
        d = api("GET", f"/boards/{board_id}/items", params=params)
        if not d: break
        chunk = d.get("data", [])
        items.extend(chunk)
        cursor = d.get("cursor")
        if not cursor or not chunk: break
    return items


def delete_all_stickies(board_id):
    items = get_all_items(board_id)
    n = 0
    for it in items:
        if it.get("type") == "sticky_note":
            api("DELETE", f"/boards/{board_id}/sticky_notes/{it['id']}")
            n += 1
            time.sleep(0.03)
    return n


def place_3x3(n, fw, fh):
    """3x3 grid offset for sticky n (0..8)."""
    col = n % 3
    row = n // 3
    # safe: keep inside frame half bounds with margin for sticky size
    col_off = (col - 1) * (fw / 4 - 50)
    row_off = (row - 1) * (fh / 4 - 50)
    return col_off, row_off


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    wbs = json.loads(WBS_JSON.read_text(encoding="utf-8"))
    by_level = defaultdict(list)
    for code, t in wbs.items():
        by_level[t.get("level")].append((code, t))

    # 1. board
    log = {}
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        board_id = log.get("board_id")
        print(f"Reusing board: {board_id}")
    else:
        if args.dry_run:
            print("DRY: would create board")
            return
        b = api("POST", "/boards", json={
            "name": "RAPA 2026 스마트병원동행AI앱 — WBS Gantt",
            "description": "WBS v0.7 98 task import. Frame=월, Sticky=L3, Color=L1."
        })
        if not b:
            print("FATAL: board create failed")
            return
        board_id = b["id"]
        log = {"board_id": board_id, "view_link": b.get("viewLink"),
               "frames": {}, "stickies": {}, "stats": {}}
        print(f"Created board: {board_id}")
        print(f"  view: https://miro.com/app/board/{board_id}")

    # 2. delete existing stickies (idempotent re-run)
    if not args.dry_run:
        n_del = delete_all_stickies(board_id)
        if n_del: print(f"  cleared {n_del} old stickies")

    # 3. create 32 frames (idempotent — reuse from log if exists)
    l1_items = by_level[1]
    frame_ids = {}
    for k, v in log.get("frames", {}).items():
        l1, m = k.rsplit("_", 1)
        frame_ids[(l1, int(m))] = v

    if not frame_ids:
        print("Creating 32 frames...")
        for r, (l1_code, l1_t) in enumerate(l1_items):
            for c, month_name in enumerate(COL_MONTHS):
                x, y = xy(c, r)
                f = api("POST", f"/boards/{board_id}/frames", json={
                    "data": {"title": f"{l1_t.get('name','')} — {month_name}",
                             "format": "custom", "type": "freeform"},
                    "position": {"x": x, "y": y},
                    "geometry": {"width": FRAME_BASE[0], "height": FRAME_BASE[1]},
                    "style": {"fillColor": "#f5f6f8"}
                })
                if f:
                    frame_ids[(l1_code, c)] = f["id"]
                time.sleep(0.04)
        print(f"  ✓ {len(frame_ids)} frames")

    # 4. resize frames that have >6 tasks to FRAME_LARGE
    print("Resizing overloaded frames...")
    frame_tasks = defaultdict(list)
    for code, t in by_level[3]:
        s_d = parse_date(t.get("start"))
        if not s_d: continue
        s_idx = month_idx(s_d)
        l1 = code.split(".")[0]
        frame_tasks[(l1, s_idx)].append(code)
    for (l1, m_idx), tasks in frame_tasks.items():
        if len(tasks) > 6:
            fid = frame_ids.get((l1, m_idx))
            if fid:
                api("PATCH", f"/boards/{board_id}/frames/{fid}",
                    json={"geometry": {"width": FRAME_LARGE[0], "height": FRAME_LARGE[1]}})
                time.sleep(0.04)

    # 5. get frame positions
    items = get_all_items(board_id)
    frames_info = {it["id"]: (it.get("position"),
                              it.get("geometry", {}).get("width", 0),
                              it.get("geometry", {}).get("height", 0))
                   for it in items if it.get("type") == "frame"}

    # 6. create 69 stickies
    print(f"Creating 69 stickies...")
    sticky_ids = {}
    errors = []
    placed = defaultdict(int)
    for code, t in by_level[3]:
        s_d = parse_date(t.get("start"))
        if not s_d: continue
        s_idx = month_idx(s_d)
        l1 = code.split(".")[0]
        fid = frame_ids.get((l1, s_idx))
        if not fid: continue
        fpos, fw, fh = frames_info.get(fid, (None, 0, 0))
        if not fpos: continue
        n = placed[(l1, s_idx)]
        if n >= 9:
            errors.append((code, "frame full"))
            continue
        placed[(l1, s_idx)] = n + 1
        lx, ly = place_3x3(n, fw, fh)
        bx, by = fpos["x"] + lx, fpos["y"] + ly
        content = (
            f"**{code}** {t.get('name','')}\n"
            f"📅 {t.get('start','')}~{t.get('end','')}\n"
            f"👤 {t.get('owner','-')}"
        )
        color = COLOR_L1.get(l1, "light_yellow")
        s = api("POST", f"/boards/{board_id}/sticky_notes", json={
            "data": {"content": content, "shape": "square"},
            "position": {"x": bx, "y": by},
            "style": {"fillColor": color, "textAlign": "left"}
        })
        if s:
            sticky_ids[code] = s["id"]
        else:
            errors.append((code, "api fail"))
        time.sleep(0.04)

    log["frames"] = {f"{k[0]}_{k[1]}": v for k, v in frame_ids.items()}
    log["stickies"] = sticky_ids
    log["errors"] = errors
    log["stats"] = {
        "frames": len(frame_ids),
        "stickies": len(sticky_ids),
        "l1": len(l1_items),
        "l3_total": len(by_level[3]),
        "errors": len(errors)
    }
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== DONE ===")
    print(f"  board: https://miro.com/app/board/{board_id}")
    print(f"  frames: {len(frame_ids)}")
    print(f"  stickies: {len(sticky_ids)}/{len(by_level[3])}")
    print(f"  errors: {len(errors)}")


if __name__ == "__main__":
    main()
