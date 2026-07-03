# Linear 이슈 노트 (스냅샷)

> 2026-07-03 v0.1. Linear MCP로 자동 임포트 또는 수동 export.
> 본 vault는 **GitHub Codespaces / Personal OAuth** 인증 가정.

## 파모즈 task 트래킹 (RHIZOME-153~163, 1.3.3~1.3.6 + 2.10.1~2.10.3 + 1.7.1)

| Linear ID | WBS | 제목 | Status | 마감 |
|---|---|---|---|---|
| RHIZOME-153 | 1.3.3 | SDK 구성·연동 설계 | Todo | 2026-07-16 |
| RHIZOME-154 | 1.3.4 | 데이터 흐름·인터페이스 정의 | Todo | 2026-07-21 |
| RHIZOME-155 | 1.3.5 | 스캔·기준맵 파이프라인 구축 | Todo | 2026-07-27 |
| RHIZOME-156 | 1.3.6 | 빌드·배포(CI) 환경 구축 | Todo | 2026-07-24 |
| RHIZOME-157 | 1.8.1 | Native AR 설계 | Todo | 2026-07-31 |
| RHIZOME-158 | 1.8.2 | AI SDK 설계 | Todo | 2026-08-31 |
| RHIZOME-159 | 2.10.1 | 멀티 디바이스 호환성 검증 | Backlog | 2026-11-06 |
| RHIZOME-160 | 2.10.2 | AR 기능 검증 | Backlog | 2026-11-06 |
| RHIZOME-161 | 2.10.3 | SDK 통합 전 자체 QA | Backlog | 2026-11-06 |
| RHIZOME-163 | 1.7.1 | 환자용앱 AI챗봇/AR길찾기 화면 설계 | Todo | 2026-08-31 |

## Cycle 17/18 계획 이슈 (현재 Cycle 16 = 7/3~7/27)

| Linear ID | 제목 | 마감 |
|---|---|---|
| RHIZOME-122 | [C17] PF state 확장 설계 및 구현 스파이크 | 8/10 |
| RHIZOME-123 | [C17] Safe update gate 및 correction source 인터페이스 설계 | 8/10 |
| RHIZOME-124 | [C17] 기준 데이터셋 수집 스키마·체크리스트 확정 | 8/10 |
| RHIZOME-125 | [C17] Native AR 책임 범위 및 ARCore survey 연동 slice | 8/10 |
| RHIZOME-126 | [C17] AI SDK public API skeleton 설계 | 8/10 |
| RHIZOME-127 | [C18] Replay acceptance test 및 correction source 평가 harness | 8/24 |
| RHIZOME-128 | [C18] Map/floor constraint와 floorplan calibration 통합 slice | 8/24 |
| RHIZOME-129 | [C18] ARCore/survey/floorplan integration prototype | 8/24 |
| RHIZOME-130 | [C18] AI SDK prototype app integration | 8/24 |
| RHIZOME-131 | [C18] Safety/RAG/측위 불확실성 표기 UX 정책 확정 | 8/24 |

## 잘못 매핑된 이슈 (정리 필요)

| Linear ID | WBS 코드 | 실제 작업 | 권장 |
|---|---|---|---|
| RHIZOME-99 | 1.2.1 | 측위엔진 구조 설계 | WBS 1.3.2와 중복, archive |
| RHIZOME-100 | 1.2.2 | SDK 구성·연동 설계 | WBS 1.3.3과 중복, RHIZOME-153으로 통합 |
| RHIZOME-101 | 1.2.3 | 데이터 흐름·인터페이스 | WBS 1.3.4와 중복, RHIZOME-154로 통합 |
| RHIZOME-102 | 1.2.4 | 스캔·기준맵 파이프라인 | WBS 1.3.5와 중복, RHIZOME-155로 통합 |
| RHIZOME-103 | 1.2.5 | 빌드·배포(CI) 환경 | WBS 1.3.6과 중복, RHIZOME-156로 통합 |
| RHIZOME-106 | 1.4.1 | RAG 검색 파이프라인 설계 | WBS 1.5.1과 정합, 리네임 |
| RHIZOME-107 | 1.4.2 | Safety Guardrail 설계 | WBS 1.5.3과 정합, 리네임 |
| RHIZOME-108 | 1.7.1 | Native AR 설계 | WBS 1.8.1과 정합, RHIZOME-157로 통합 |
| RHIZOME-109 | 1.7.2 | AI SDK 설계 | WBS 1.8.2와 정합, RHIZOME-158로 통합 |
| RHIZOME-104 | 1.3.1 | LiDAR 전층 스캔 | WBS 1.3.1 시스템구성설계 ≠ LiDAR, 리네임 |

## Dataview 자동 임포트 (선택)

Linear MCP + Dataview로 실시간 동기화하려면 `.obsidian/plugins/linear-sync/` 같은 플러그인 또는 Hermes CLI로:

```bash
hermes linear list --project "RAPA 스마트 병원동행 AI앱 (파모즈)" > _obsidian_vault/Dashboards/linear-snapshot.md
```

## 관련

- 🔗 [[Dashboards/Dashboard-Status|Status Dashboard]]
- 🔗 [[README|Home]]
