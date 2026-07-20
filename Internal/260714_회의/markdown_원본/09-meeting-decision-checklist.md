# SDK 통합 회의 결정사항 체크리스트

> 문서 등급: CONFIDENTIAL - Integration Partner Use Only
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 목적

본 문서는 SDK 통합 회의에서 결정해야 할 항목을 우선순위별로 확인하고, 결정 결과·책임 영역·완료 시점을 기록하기 위한 체크리스트이다.

상세 근거와 선택지는 `08-sdk-integration-decision-sheet.md`를 참조한다. 본 문서에서는 회의 중 결론이 필요한 항목만 간결하게 관리한다.

## 2. 사용 방법

| 값 | 의미 |
|---|---|
| P0 | 통합 구현 착수 전에 반드시 결정 |
| P1 | API·UI·데이터 상세 설계 전에 결정 |
| P2 | 제품 release와 운영 전 결정 |
| Confirmed | 합의 완료 |
| Open | 논의 전 또는 결론 미도출 |
| Deferred | 후속 협의로 이관 |
| Blocked | 외부 입력이나 검증 없이는 결정 불가 |

각 항목은 최소 다음 정보를 기록한다.

- 결정 결과
- 대안 선택 사유
- 책임 조직 또는 책임 영역
- 완료 기한
- 완료를 증명할 artifact 또는 시험 결과

## 3. 현재 사실로 확인된 항목

다음 내용은 선택사항이 아니라 현재 저장소 기준 사실이다.

| ID | 확인된 사실 |
|---|---|
| F-01 | Android local release AAR은 생성 가능하다. |
| F-02 | Maven repository 게시 절차와 제품 POM은 완성되지 않았다. |
| F-03 | iOS local KMP static framework 경로는 존재한다. |
| F-04 | XCFramework와 SPM binary package는 완성되지 않았다. |
| F-05 | Android core minSdk는 24이고 PoC 앱 minSdk는 26이다. |
| F-06 | iOS PoC deployment target은 16.0이다. |
| F-07 | Android API 24와 iOS 15.6 실기기 검증은 완료되지 않았다. |
| F-08 | 현재 제품용 AR 진입 Facade와 typed callback 계약은 구현 전이다. |
| F-09 | 현재 PoC 앱이 권한 요청과 화면 흐름을 관리한다. |
| F-10 | 일부 venue 데이터와 구축 도구는 있으나 운영 RACI·SLA는 없다. |
| F-11 | 공식 단말 tier API와 전 단말 호환성 보고서는 없다. |
| F-12 | AI 챗봇 구현과 SDK 명세는 현재 Position SDK 저장소에 없다. |

## 4. P0 - 통합 착수 전 필수 결정

### 4.1 배포와 지원 범위

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| D-01 | Android SDK 배포 방식 | private Maven AAR | 미기입 | 공동 | 미기입 | Open |
| D-02 | iOS SDK 배포 방식 | XCFramework + SPM | 미기입 | 공동 | 미기입 | Open |
| D-03 | 목표 최소 OS | Android API 24 / iOS 15.6, 검증 후 공식화 | 미기입 | 공동 | 미기입 | Open |
| D-04 | Android repository 인증 | token 또는 내부 repository 정책 | 미기입 | Host/운영 | 미기입 | Open |
| D-05 | iOS simulator architecture | 개발환경에 필요한 최소 slice | 미기입 | Host | 미기입 | Open |

### 4.2 API와 UI 범위

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| D-06 | AR·2D 안내 진입 방식 | `NavigationRequest` + session stream | 미기입 | 공동 | 미기입 | Open |
| D-07 | SDK 필수 제공 범위 | headless core | 미기입 | SDK | 미기입 | Open |
| D-08 | SDK 선택 UI 제공 여부 | 기본 2D·AR optional module | 미기입 | 공동 | 미기입 | Open |
| D-09 | 최종 화면·branding·workflow | Host App 소유 | 미기입 | Host | 미기입 | Open |
| D-10 | UI/UX 컨셉 초안 완료 시점 | API v0.1 freeze 전 | 미기입 | 공동 | 미기입 | Open |

### 4.3 권한과 폴백

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| D-11 | OS 권한 요청 주체 | Host App | 미기입 | Host | 미기입 | Open |
| D-12 | 권한·capability 반환 | SDK typed 상태·오류 | 미기입 | SDK | 미기입 | Open |
| D-13 | 단말 분기 방식 | model allowlist보다 capability 기반 | 미기입 | SDK | 미기입 | Open |
| D-14 | AR 미지원 폴백 | Live 2D | 미기입 | 공동 | 미기입 | Open |
| D-15 | Motion·camera 미지원 폴백 | Static 2D 또는 지원 불가 | 미기입 | Host | 미기입 | Open |
| D-16 | 최종 폴백 UI 책임 | Host App | 미기입 | Host | 미기입 | Open |

### 4.4 공간 데이터

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| D-17 | 최초 구축 대상 범위 | 병원·건물·층 단위로 명시 | 미기입 | 공동 | 미기입 | Open |
| D-18 | 원천 도면·BIM·POI 제공 | 공간 데이터 원천 영역 | 미기입 | Data Owner | 미기입 | Open |
| D-19 | 현장 서베이와 runtime map 생성 | SDK 범위 | 미기입 | SDK | 미기입 | Open |
| D-20 | 최종 공간 데이터 승인 | 공간 데이터 원천 영역 | 미기입 | Data Owner | 미기입 | Open |
| D-21 | 측위 맵 전달 방식 | versioned Venue Package | 미기입 | 공동 | 미기입 | Open |
| D-22 | digital twin 전달 방식 | 별도 package 또는 선택 layer | 미기입 | 공동 | 미기입 | Open |

### 4.5 착수 조건

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| D-23 | API v0.1 승인 절차 | schema review 후 freeze | 미기입 | 공동 | 미기입 | Open |
| D-24 | 최초 통합 sample 범위 | 위치 시작·중지·2D 폴백 | 미기입 | 공동 | 미기입 | Open |
| D-25 | 개발 endpoint와 접근 방식 | 인증 가능한 개발환경 | 미기입 | 공동 | 미기입 | Open |
| D-26 | integration acceptance | build·lifecycle·기본 동선 기준 | 미기입 | 공동 | 미기입 | Open |

## 5. P1 - 상세 설계 전 결정

### 5.1 API 상세

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| I-01 | `destinationId` 원천과 mapping | 업무 ID를 venue POI ID로 변환 | 미기입 | Host/Data | 미기입 | Open |
| I-02 | 시작층 입력 | `floorId` optional hint | 미기입 | 공동 | 미기입 | Open |
| I-03 | 목적지 변경 | 새 session 또는 명시적 update API | 미기입 | 공동 | 미기입 | Open |
| I-04 | 접근성 경로 옵션 | 계단 회피 등 request에 포함 | 미기입 | 공동 | 미기입 | Open |
| I-05 | 위치 정확도 필드 의미 | uncertainty 정의 후 문서화 | 미기입 | SDK | 미기입 | Open |
| I-06 | background 정책 | suspend 또는 stop 중 하나로 고정 | 미기입 | 공동 | 미기입 | Open |
| I-07 | Swift stream 제공 | AsyncSequence 또는 callback adapter | 미기입 | SDK | 미기입 | Open |
| I-08 | 오류와 재시도 정보 | typed code + recoverable | 미기입 | SDK | 미기입 | Open |

### 5.2 서비스·보안

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| I-09 | 위치 확인 서비스 배치 | 승인된 운영환경 | 미기입 | 공동 | 미기입 | Open |
| I-10 | 서비스 인증 | Host token provider 또는 SDK credential | 미기입 | 공동 | 미기입 | Open |
| I-11 | 카메라 이미지 저장 | 기본 미보관, 필요 시 명시 동의 | 미기입 | 보안/운영 | 미기입 | Open |
| I-12 | 위치·진단 로그 | 최소 수집·보관기간 명시 | 미기입 | 보안/운영 | 미기입 | Open |
| I-13 | 전송 보안 | TLS·인증·무결성 검증 | 미기입 | SDK/운영 | 미기입 | Open |

### 5.3 Venue Package 운영

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| I-14 | package schema | manifest·schemaVersion·checksum | 미기입 | SDK | 미기입 | Open |
| I-15 | package 배포 | 앱 동봉·download 혼합 검토 | 미기입 | 공동 | 미기입 | Open |
| I-16 | package 저장소 | 접근 제어된 versioned repository | 미기입 | 운영 | 미기입 | Open |
| I-17 | 공간 변경 통보 | 변경 영향도별 기한 정의 | 미기입 | Data Owner | 미기입 | Open |
| I-18 | 기술·현장 검수 | QA 후 승인 단계 분리 | 미기입 | 공동 | 미기입 | Open |
| I-19 | rollback | 이전 승인 version 유지 | 미기입 | SDK/운영 | 미기입 | Open |
| I-20 | 갱신 SLA와 비용 | 운영계약으로 별도 확정 | 미기입 | 공동 | 미기입 | Open |

### 5.4 UI/UX 산출물

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| I-21 | UI/UX 컨셉 책임 | 공동 flow, Host 최종 design | 미기입 | 공동 | 미기입 | Open |
| I-22 | 필수 화면 상태 | 진입·권한·측위·2D·AR·폴백·도착 | 미기입 | 공동 | 미기입 | Open |
| I-23 | 선택 UI customization | theme·icon·문구·layout 범위 | 미기입 | 공동 | 미기입 | Open |
| I-24 | 시연 영상·스크린샷 | 대표 흐름과 한계 caption 포함 | 미기입 | SDK | 미기입 | Open |

## 6. P2 - Release·운영 전 결정

### 6.1 단말과 성능

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| R-01 | 공식 Android 시험 matrix | OS·OEM·SoC·센서 tier 조합 | 미기입 | 공동 | 미기입 | Open |
| R-02 | 공식 iOS 시험 matrix | 최소·중간·최신 OS와 hardware | 미기입 | 공동 | 미기입 | Open |
| R-03 | AR 성능 기준 | 목표 FPS·발열·메모리 | 미기입 | 공동 | 미기입 | Open |
| R-04 | 위치 성능 기준 | 대표 venue·동선별 acceptance | 미기입 | 공동 | 미기입 | Open |
| R-05 | 층 판정 기준 | 계단·엘리베이터 정확도 | 미기입 | 공동 | 미기입 | Open |
| R-06 | 초기 위치 확인 기준 | 성공률·응답시간·재시도 | 미기입 | 공동 | 미기입 | Open |
| R-07 | 장시간 안정성 | 배터리·발열·메모리·resource 해제 | 미기입 | 공동 | 미기입 | Open |

### 6.2 Release와 운영

| ID | 결정사항 | 권장 기본안 | 결정 결과 | 책임 영역 | 완료 기한 | 상태 |
|---|---|---|---|---|---|---|
| R-08 | SDK version 정책 | SemVer | 미기입 | SDK | 미기입 | Open |
| R-09 | 지원 기간 | release별 지원기간 명시 | 미기입 | 공동 | 미기입 | Open |
| R-10 | 장애 대응 | severity·응답시간·진단자료 정의 | 미기입 | 공동 | 미기입 | Open |
| R-11 | dependency·license | SBOM·NOTICE·승인 절차 | 미기입 | SDK/보안 | 미기입 | Open |
| R-12 | release notes | OS·단말·제한·migration 포함 | 미기입 | SDK | 미기입 | Open |
| R-13 | 운영 모니터링 | 개인정보 최소화 지표 | 미기입 | 운영/보안 | 미기입 | Open |

## 7. 후속 협의 항목

### 7.1 AI 챗봇 SDK

AI 챗봇 SDK는 이번 Position SDK 통합 회의의 확정 대상에서 제외한다.

공식 답변:

> AI 챗봇 SDK의 제공 형태, 기능 범위 및 연동 방식은 전남대학교와 세부적으로 논의한 후 추후 상세 내용을 별도로 전달드릴 예정입니다. 현 단계의 Position SDK 기술자료 및 통합 범위에는 AI 챗봇 SDK를 포함하지 않습니다.

| ID | 후속 항목 | 처리 방식 | 상태 |
|---|---|---|---|
| X-01 | AI 챗봇 기능 범위 | 전남대학교 협의 후 별도 정의 | Deferred |
| X-02 | AI 챗봇 제공 형태 | 서버 API·SDK·web component 등 후속 결정 | Deferred |
| X-03 | Position SDK 연계 | 위치·POI context 전달 여부 후속 결정 | Deferred |

## 8. 회의 종료 전 확인

회의 종료 전 다음 항목을 확인한다.

- [ ] P0 항목별 결정 결과가 기록되었는가
- [ ] 미결정 항목에 필요한 추가 입력이 명시되었는가
- [ ] 책임 영역과 완료 기한이 기록되었는가
- [ ] UI module 제공 여부와 UI/UX 초안 일정이 정해졌는가
- [ ] 최초 venue·층·원천자료 범위가 정해졌는가
- [ ] 최소 OS 검증과 대표 단말 시험 범위가 정해졌는가
- [ ] API v0.1 검토·동결 시점이 정해졌는가
- [ ] 시연 영상·스크린샷 준비 범위가 정해졌는가
- [ ] 다음 회의의 입력자료와 목표가 정해졌는가
- [ ] AI 챗봇 항목이 후속 협의로 분리되었는가

## 9. 회의 결과 요약 템플릿

```text
회의 목적:
결정 완료 항목:
조건부 승인 항목:
미결정 항목:
추가 필요 자료:
SDK 구현 착수 가능 여부:
공간 데이터 구축 착수 가능 여부:
UI/UX 초안 완료 목표:
API v0.1 동결 목표:
최소 OS·단말 검증 목표:
다음 회의 목표:
```

## 10. 착수 판정

| 판정 | 조건 |
|---|---|
| GO | P0 결정 완료, API·배포·공간 범위·UI 책임·시험 계획 승인 |
| CONDITIONAL GO | 일부 P1 미정이나 구현 경계와 임시값이 승인됨 |
| NO-GO | SDK 제공 형태, API, 공간 데이터 책임 또는 UI 범위 중 핵심 항목 미결정 |

착수 판정은 문서 작성 완료 여부가 아니라 결정 결과와 필요한 입력자료 확보 여부를 기준으로 한다.
