---
type: doc
status: living
last_reviewed: 2026-05-28
---

# MOC — Map of Content

Vault 진입 페이지. 핵심 보드와 인덱스가 여기 모인다.

## 📋 살아있는 결정 (status = accepted)

```dataview
TABLE status, date, supersedes
FROM "decisions"
WHERE status = "accepted"
SORT date DESC
```

## ⏳ 검토 시점이 오래된 살아있는 스펙 (>60일)

```dataview
TABLE last_reviewed, owner
FROM "specs"
WHERE status = "living" AND date(today) - last_reviewed > dur(60 days)
SORT last_reviewed ASC
```

## 🗓️ 최근 회의

```dataview
TABLE date, attendees, produced_decisions
FROM "meetings"
SORT date DESC
LIMIT 10
```

## 🧭 폴더 바로가기

- `decisions/` — ADR
- `specs/` — 살아있는 스펙
- `meetings/` — 회의록
- `people/` — 이해관계자
- `domain/` — 도메인 지식
- `deliverables/` — 공식 산출물 인덱스

(폴더 안 노트가 생기면 직접 wikilink로 교체)
