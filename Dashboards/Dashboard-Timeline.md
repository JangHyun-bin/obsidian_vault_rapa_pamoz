# RAPA 스마트병원 동행 AI앱 — Timeline Dashboard

> WBS v0.7 (2026-07-03 17:02) + Linear 이슈 통합

> 생성: 2026-07-03 18:10 | Mermaid Gantt 형식


## 📊 Timeline (Gantt)

**색상**: 🟢 진행중 / 🟠 임박(D-14) / 🔴 긴급(D-7) / ⚪ 기본

**태그**: ✅ Linear 동기화됨 / ❌ Linear 미생성 / ⚠️  잘못 매핑


```mermaid
gantt
    title RAPA 파모즈 1차년도 핵심 일정 (7~11월)
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    excludes weekends
    section 1. 분석/설계 (1.3.x)
    1.3.1 시스템_구성_설계 [RHIZOME-163 (화면설계)] :active, 2026-06-01, 2026-07-16
    1.3.2 측위엔진_구조_설계 [no-linear] :active, 2026-06-11, 2026-07-15
    1.3.3 SDK_구성연동_설계 [RHIZOME-153] :active, 2026-06-22, 2026-07-16
    1.3.4 데이터_흐름인터페이스_정의 [RHIZOME-154] :2026-07-01, 2026-07-21
    1.3.5 스캔기준맵_파이프라인_구축 [RHIZOME-155] :2026-07-03, 2026-07-27
    1.3.6 빌드배포CI_환경_구축 [RHIZOME-156] :2026-07-01, 2026-07-24
    1.7.1 환자용앱_AI챗봇___AR길찾기_화면_설계 [RHIZOME-163] :2026-07-15, 2026-08-31
    1.8.1 Native_AR_설계 [RHIZOME-157] :2026-06-15, 2026-07-31
    1.8.2 AI_SDK_설계 [RHIZOME-158] :2026-07-15, 2026-08-31
    section 2. 개발 (2.x)
    2.2.2 측위_엔진_통합정확도_최적화 [RHIZOME-112] :2026-11-02, 2026-11-27
    2.5.1 AI_SDK_개발 [RHIZOME-113] :2026-08-03, 2026-11-30
    2.9.1 OCR_파이프라인_구축 [RHIZOME-114] :2026-08-03, 2026-11-30
    2.10.1 멀티_디바이스_호환성_검증_iOS_Android_기기군 [RHIZOME-159] :2026-09-21, 2026-11-06
    2.10.2 AR_기능_검증 [RHIZOME-160] :2026-10-12, 2026-11-06
    2.10.3 SDK_통합_전_자체_QA_회귀안정성 [RHIZOME-161] :2026-10-12, 2026-11-06
    2.6.1 푸시_발송_개발 [no-linear] :2026-05-26, 2026-10-30
    section Milestones
    1차 컨소 meeting (1.3.1 합의) :milestone, 2026-07-16, 0d
    Cycle 16 종료 :milestone, 2026-07-27, 0d
    Cycle 17 시작 :milestone, 2026-07-27, 0d
    측위엔진 통합 종료 :milestone, 2026-11-27, 0d
    SDK 자체 검증 종료 :milestone, 2026-11-06, 0d
    1차 보도자료 :milestone, 2026-07-31, 0d
    사업 종료 :milestone, 2026-12-31, 0d
```

## 📋 핵심 Task 목록 (Linear 동기화 상태)

| WBS | 작업명 | 시작 | 종료 | D-day | Linear |
|---|---|---|---|---|---|
| 1.3.1 | 시스템 구성 설계 | 2026-06-01 | 2026-07-16 | 🟠 D-13 | RHIZOME-163 (화면설계) |
| 1.3.2 | 측위엔진 구조 설계 | 2026-06-11 | 2026-07-15 | 🟠 D-12 | ❌ 없음 |
| 1.3.3 | SDK 구성·연동 설계 | 2026-06-22 | 2026-07-16 | 🟠 D-13 | RHIZOME-153 |
| 1.3.4 | 데이터 흐름·인터페이스 정의 | 2026-07-01 | 2026-07-21 | D-18 | RHIZOME-154 |
| 1.3.5 | 스캔·기준맵 파이프라인 구축 | 2026-07-03 | 2026-07-27 | D-24 | RHIZOME-155 |
| 1.3.6 | 빌드·배포(CI) 환경 구축 | 2026-07-01 | 2026-07-24 | D-21 | RHIZOME-156 |
| 1.7.1 | 환자용앱 AI챗봇 / AR길찾기 화면 설계 | 2026-07-15 | 2026-08-31 | D-59 | RHIZOME-163 |
| 1.8.1 | Native AR 설계 | 2026-06-15 | 2026-07-31 | D-28 | RHIZOME-157 |
| 1.8.2 | AI SDK 설계 | 2026-07-15 | 2026-08-31 | D-59 | RHIZOME-158 |
| 2.2.2 | 측위 엔진 통합·정확도 최적화 | 2026-11-02 | 2026-11-27 | D-147 | RHIZOME-112 |
| 2.5.1 | AI SDK 개발 | 2026-08-03 | 2026-11-30 | D-150 | RHIZOME-113 |
| 2.9.1 | OCR 파이프라인 구축 | 2026-08-03 | 2026-11-30 | D-150 | RHIZOME-114 |
| 2.10.1 | 멀티 디바이스 호환성 검증 (iOS/Android 기기군) | 2026-09-21 | 2026-11-06 | D-126 | RHIZOME-159 |
| 2.10.2 | AR 기능 검증 | 2026-10-12 | 2026-11-06 | D-126 | RHIZOME-160 |
| 2.10.3 | SDK 통합 전 자체 QA (회귀·안정성) | 2026-10-12 | 2026-11-06 | D-126 | RHIZOME-161 |
| 2.6.1 | 푸시 발송 개발 | 2026-05-26 | 2026-10-30 | D-119 | ❌ 없음 |

## 🔗 의존성 그래프 (Flow)

```mermaid
flowchart LR
    A[1.3.1 시스템구성설계<br/>D-13 컨소 합의] --> B[1.3.2 측위엔진]
    A --> C[1.3.3 SDK구성]
    A --> D[1.3.4 데이터흐름]
    A --> E[1.3.6 CI환경]
    A --> F[1.3.5 스캔파이프라인]
    B --> G[2.2.1 융합측위]
    G --> H[2.2.2 측위엔진통합<br/>D-130]
    H --> I[2.10 SDK 자체검증<br/>D-126 ⚠️ 단축됨]
    I --> J[2.9.1 멀티디바이스]
    I --> K[2.9.2 AR기능]
    I --> L[2.9.3 SDK QA]
    C --> M[2.1.1 Native AR]
    D --> N[2.5.1 AI SDK<br/>D-150]
    style A fill:#ff6b6b,color:#fff
    style I fill:#ffd93d,color:#000
```

**범례**: 🔴 임박/긴급 / 🟡 주의 (의존성 모순) / ⬜ 일반

## ⚠️ 주의 사항

- **2.10 SDK 자체 검증** (D-126) 이 **2.2.2 측위엔진 통합** (D-130) 보다 4일 먼저 끝남 → 의존성 모순. 컨소 재논의 필요
- **1.3.2 LiDAR** (Linear RHIZOME-104)는 WBS 1.3.1 시스템구성설계와 다른 작업. 잘못 매핑됨.

## 🔗 관련
## 🔗 관련
- [[README|Home / MOC]]
- [[Dashboards/Dashboard-Status|Status Dashboard]]
- [[WBS/WBS-july|7월 임박]]
- [[Linear-Issues|Linear 이슈 노트]]
- GitHub: https://github.com/JangHyun-bin/obsidian_vault_rapa_pamoz

## 🌐 외부 Timeline (실시간)

**OpenProject** (Gantt, Calendar, Work packages):
- 프로젝트: http://localhost:8082/projects/rapa-smart-hospital-pamoz
- Gantt view: http://localhost:8082/projects/rapa-smart-hospital-pamoz/work_packages?view=gantt
- 98 work packages (L1 4 + L2 25 + L3 69, startDate/dueDate 기반)
- OpenProject API v3 (Basic apikey auth)
- 동기화: `Scripts/sync_openproject.py` (cron 자동 갱신)

**Linear** (실시간 task 관리):
- 프로젝트: RAPA 스마트병원동행AI앱 (파모즈) (RHIZOME-153~163)
- 4.3.x 잘못 매핑된 이슈는 별도 정리 필요

**GanttProject** (인터랙티브 + PNG export):
- 위치: `Attachments/RAPA_파모즈_v0.7.gan`
