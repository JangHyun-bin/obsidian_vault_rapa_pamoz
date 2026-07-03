# GanttProject 사용 가이드

> RAPA 파모즈 WBS를 GanttProject로 시각화.

## 빠른 시작 (3분)

1. **GanttProject 다운로드** (이미 받음):
   - 위치: `C:\Users\user\Downloads\ganttproject\`
   - 실행: `ganttproject.bat` 더블클릭 (Java 23 필요)

2. **WBS .gan 파일 import**:
   - `File → Open...` → `vault/Attachments/RAPA_파모즈_v0.7.gan` 선택
   - 69 tasks + 44 dependencies 자동 표시

3. **PNG export (공유용)**:
   - `File → Export → PNG image`
   - 또는 `Ctrl+P` (인쇄) → PDF로 export

## .gan 파일은 어디서?

`vault/Attachments/RAPA_파모즈_v0.7.gan` (3.2KB, ZIP+XML)

- 69 L3 task
- D-day 기반 색상:
  - 🔴 빨강 `#ff6b6b`: D-7 이내 (긴급)
  - 🟠 주황 `#ffa500`: D-14 이내 (임박)
  - 🟢 청록 `#4ecdc4`: D-30 이내 (정상)
  - ⬜ 연청록 `#95e1d3`: D-30+ (여유)
- 44 dependencies (계층 + sequential)

## 갱신 주기

`Scripts/sync_intelligent.py`에 .gan 자동 갱신 stage 추가 가능 (현재는 1회성).

수동 갱신:
```bash
python _obsidian_vault/Scripts/wbs_to_gan.py
```

## 대안 (오픈소스 / 무료)

| 도구 | 형식 | 셀프호스트 | Gantt |
|---|---|---|---|
| **GanttProject** (현재) | .gan, .mpp | 데스크톱 | ✓ |
| [ProjectLibre](https://www.projectlibre.com/) | .mpp | 데스크톱 | ✓ |
| [Plane](https://plane.so/) | SaaS/SSO | ✓ (Docker) | ✓ |
| [OpenProject](https://www.openproject.org/) | MS Project 호환 | ✓ (Docker) | ✓ |

## vault 통합

- `Dashboard-Timeline.md` (Mermaid gantt, 자동 갱신)
- `Attachments/RAPA_파모즈_v0.7.gan` (GanttProject, 수동 갱신)
- Linear 이슈 (startDate 미지원, dueDate만)

두 가지 보완: Mermaid는 가벼운 snapshot, .gan은 인터랙티브 + PNG export.

## 다음 단계

1. 사용자가 직접 GanttProject 실행 → PNG screenshot 캡처
2. PNG를 `vault/Attachments/ganttproject-export-YYYY-MM-DD.png`로 저장
3. `Dashboard-Timeline.md`에 PNG embed 추가 (옵션)

## 관련

- [[README|Home / MOC]]
- [[Dashboards/Dashboard-Timeline|Timeline Dashboard]]
- [[WBS/WBS-july|7월 임박]]
