# Dashboard — Status

> RAPA 파모즈 작업 현황 단일 뷰. 2026-07-03 v0.1.
> 모든 Dataview 쿼리는 **현재 vault 기준** 자동 집계. 수동 갱신 불필요.

## 🚨 7월 임박 산출물 (D-day)

```dataview
TABLE
  WITHOUT ID
  link(file.link, "WBS") AS "WBS",
  dueDate AS "D-day",
  작업명 AS "작업",
  담당 AS "담당",
  산출물 AS "산출물"
FROM "WBS/L3"
WHERE 마감 >= date(today) AND 마감 <= date(2026-07-31)
SORT 마감 ASC
LIMIT 20
```

## 📊 WBS 진행률 (Linear 임베드)

```dataview
TABLE
  WITHOUT ID
  id AS "Linear",
  title AS "제목",
  status AS "Status",
  dueDate AS "마감",
  assignee AS "담당",
  project AS "프로젝트"
FROM ""
WHERE contains(project, "RAPA") OR contains(lower(project), "rapa")
SORT dueDate ASC
LIMIT 30
```

## 📈 1.3.x 진행 중 (Backlog/Todo 상태)

```dataview
TABLE
  WITHOUT ID
  id AS "Linear",
  title AS "제목",
  status AS "Status",
  dueDate AS "마감",
  priorityText AS "Priority"
FROM ""
WHERE contains(id, "RHIZOME") AND (status = "Todo" OR status = "Backlog")
SORT dueDate ASC
LIMIT 30
```

## 🔄 최근 WBS diff

```dataview
LIST
FROM "WBS"
WHERE contains(file.name, "diff")
```

## 📂 최근 산출물

```dataview
TABLE
  WITHOUT ID
  link(file.link, "산출물") AS "파일",
  WBS코드 AS "WBS",
  마감 AS "마감"
FROM "Deliverables/1.3"
SORT 마감 ASC
```

## 🔗 컨소 ADR 인덱스

```dataview
LIST
FROM "ADR"
SORT file.name ASC
```

---

## 외부 임포트 가이드

이 vault는 **수동 동기화** 가정. 자동화는:
- WBS: `Scripts/wbs_to_md.py` 실행 (xlsm → MD)
- Linear: Linear MCP 또는 수동 export
- Corpus ADR/Specs: cp 또는 symlink
