# 3.1.3 파일럿 실증 테스트 데이터 생성

## 메타

| 필드 | 값 |
|---|---|
| WBS 코드 | 3.1.3 |
| 레벨 | L3 |
| 시작 | 2026-09-01 |
| 종료 | 2026-12-04 |
| 담당 | 전남대병원 |
| 총 작업량 | 65 MD |
| 계획 작업량 | - MD |
| 총 기간 | 65 일 |
| 계획 기간 | - 일 |
| 산출물 | - |

## Linear 이슈

```dataview
TABLE id, status, dueDate, assignee, project
FROM ""
WHERE contains(id, "3.1.3") OR contains(title, "3.1.3")
```
