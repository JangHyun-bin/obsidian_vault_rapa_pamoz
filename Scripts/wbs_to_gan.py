"""wbs_to_gan.py: WBS v0.7 → GanttProject .gan 변환기 (재실행 가능).

GanttProject .gan 포맷 = ZIP 안에 project.xml. 텍스트로 작성 가능.
사용법:
    python wbs_to_gan.py
산출물: vault/Attachments/RAPA_파모즈_v0.7.gan
"""
import json
import zipfile
import io
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:/HB/P.RAPA_DEV")
WBS_JSON = ROOT / "Docs/OUTPUT/WBS/wbs_v07_20260703_5pm_extracted.json"
OUT_GAN = ROOT / "_obsidian_vault/Attachments/RAPA_파모즈_v0.7.gan"


def xml_esc(s):
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def main():
    wbs = json.loads(WBS_JSON.read_text(encoding="utf-8"))
    tasks = []
    for code, t in wbs.items():
        if t.get("level") != 3:
            continue
        if not t.get("start") or not t.get("end"):
            continue
        tasks.append((code, t))
    tasks.sort(key=lambda x: x[1]["start"])
    task_ids = {code: i + 1 for i, (code, _) in enumerate(tasks)}

    today = datetime(2026, 7, 3)
    tasks_xml = []
    for code, t in tasks:
        tid = task_ids[code]
        start = t["start"]
        end = t["end"]
        name = t.get("name") or code
        duration = (datetime.strptime(end, "%Y-%m-%d")
                    - datetime.strptime(start, "%Y-%m-%d")).days + 1
        dday = (datetime.strptime(end, "%Y-%m-%d") - today).days
        if dday <= 7:
            color = "#ff6b6b"
        elif dday <= 14:
            color = "#ffa500"
        elif dday <= 30:
            color = "#4ecdc4"
        else:
            color = "#95e1d3"
        tasks_xml.append(
            f'  <task>\n'
            f'    <taskid>{tid}</taskid>\n'
            f'    <taskname>{xml_esc(name)} ({code})</taskname>\n'
            f'    <start>{start}</start>\n'
            f'    <end>{end}</end>\n'
            f'    <duration>{duration}</duration>\n'
            f'    <progress>0</progress>\n'
            f'    <priority>0</priority>\n'
            f'    <color>{color}</color>\n'
            f'    <shape>0</shape>\n'
            f'  </task>')

    deps = []
    for code, t in tasks:
        parts = code.split(".")
        if len(parts) >= 3:
            parent_code = ".".join(parts[:-1])
            if parent_code in task_ids:
                deps.append(
                    f'  <depend task="{task_ids[parent_code]}" '
                    f'difference="0" hardness="2" type="1"/>')
        next_code = ".".join(parts[:-1] + [str(int(parts[-1]) + 1)])
        if next_code in task_ids:
            deps.append(
                f'  <depend task="{task_ids[next_code]}" '
                f'difference="0" hardness="2" type="1"/>')

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<project name="RAPA 스마트병원동행AI앱 (파모즈)" '
        'company="㈜파모즈">\n'
        '  <taskdisplayinfo id="0"><name>1. 분석/설계</name>'
        '<color>#26b5ce</color><isexpanded>true</isexpanded></taskdisplayinfo>\n'
        '  <taskdisplayinfo id="1"><name>2. 개발</name>'
        '<color>#eb5757</color><isexpanded>true</isexpanded></taskdisplayinfo>\n'
        '  <taskdisplayinfo id="2"><name>3. 테스트</name>'
        '<color>#f2c94c</color><isexpanded>true</isexpanded></taskdisplayinfo>\n'
        '  <taskdisplayinfo id="3"><name>4. 홍보 및 특허출원</name>'
        '<color>#9b51e0</color><isexpanded>true</isexpanded></taskdisplayinfo>\n'
        + "\n".join(tasks_xml) + "\n"
        '  <resources/>\n'
        '  <tasks>\n'
        + "\n".join(deps) + "\n"
        '  </tasks>\n'
        '</project>')

    OUT_GAN.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.xml", xml)
        z.writestr("version.txt", "3.3.3316")
    OUT_GAN.write_bytes(buf.getvalue())
    print(f"saved: {OUT_GAN} ({OUT_GAN.stat().st_size:,} bytes, "
          f"{len(tasks)} tasks, {len(deps)} deps)")


if __name__ == "__main__":
    main()
