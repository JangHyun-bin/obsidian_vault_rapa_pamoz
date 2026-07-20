# Position SDK 기술자료 송부 패키지 인덱스

> 문서 등급: CONFIDENTIAL - Integration Partner Use Only
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 송부 목적

본 패키지는 실내측위·AR 내비게이션 SDK의 기술 검토와 호스트 앱 통합 설계를 위해 현재 공유 가능한 기술자료, API 초안, 단말 가이드 및 의사결정 항목을 제공한다.

모든 문서는 현재 저장소와 PoC 상태를 기준으로 작성되었다. `Current PoC`, `Integration Target`, `Decision Required`를 구분하며, 제품 SDK의 최종 성능·호환성·일정 또는 납품 완료를 보장하는 문서가 아니다.

## 2. 패키지 구성

| 순번 | 문서 | 목적 | 권장 용도 | 상태 |
|---|---|---|---|---|
| 00 | `00-delivery-package-index.md` | 전체 목차·요약·요청 대응표 | 최초 확인 | v0.1 Draft |
| 01 | `01-positioning-engine-architecture.md` | 엔진 경계·기능 블록·런타임 구조 | 기술 검토 부록 | v0.1 Draft |
| 02 | `02-sdk-integration-design.md` | SDK 제공 모듈·host 책임·lifecycle | 통합 설계 | v0.1 Draft |
| 03 | `03-data-flow-interface-spec.md` | 좌표·상태·데이터 흐름·interface | 개발 협의 | v0.1 Draft |
| 04 | `04-similar-project-references.md` | 병원·AR 내비게이션 공개 유사 사례 | 사전 참고 | v0.1 Draft |
| 05 | `05-positioning-engine-technical-overview.md` | 센서·측위 방식·플랫폼 현황 | 기술 개요 답변 | v0.1 Draft |
| 06 | `06-sdk-api-spec-draft.md` | Current API와 제품 API 초안 | API 검토 | v0.1 Draft |
| 07 | `07-device-compatibility-guide.md` | 최소 OS·단말 tier·시험 현황 | 호환성 검토 | v0.1 Draft |
| 08 | `08-sdk-integration-decision-sheet.md` | 5대 통합 쟁점의 상세 의사결정안 | 회의 본문 | v0.1 Draft |
| 09 | `09-meeting-decision-checklist.md` | 회의 결정사항·우선순위·결과 기록 | 회의 체크리스트 | v0.1 Draft |

## 3. 권장 검토 순서

### 3.1 사전 검토 필수 문서

1. `00-delivery-package-index.md`
2. `05-positioning-engine-technical-overview.md`
3. `06-sdk-api-spec-draft.md`
4. `07-device-compatibility-guide.md`
5. `08-sdk-integration-decision-sheet.md`
6. `09-meeting-decision-checklist.md`

### 3.2 필요 시 확인할 상세 부록

- 엔진 구조 확인: `01-positioning-engine-architecture.md`
- SDK 배포·책임·lifecycle 확인: `02-sdk-integration-design.md`
- 좌표·schema·보안 데이터 흐름 확인: `03-data-flow-interface-spec.md`
- 외부 유사 사례 확인: `04-similar-project-references.md`

## 4. 기술자료 요청 대응표

| 요청 항목 | 대응 문서 | 현재 답변 상태 |
|---|---|---|
| 유사 프로젝트 레퍼런스 | 04 | 공개 공식자료 기반 조사 완료 |
| 측위 엔진 기술 개요 | 05, 01 | 센서·측위 방식·공개 범위 작성 완료 |
| SDK 기술 문서 또는 API 명세 초안 | 06, 02, 03 | Current API와 Integration Target 작성 완료 |
| PoC 시연 영상·스크린샷 | 별도 시각자료 package | 선별·편집 필요 |
| 단말 호환성 테스트 또는 지원 가이드 | 07 | 현재 시험과 미검증 범위 작성 완료 |

## 5. 구현 관점 사전 확인 대응표

| 요청 항목 | 주요 대응 문서 | 현재 답변 |
|---|---|---|
| SDK 제공 형태와 최소 OS | 08 §4, 07 §5 | Android Maven/AAR, iOS XCFramework/SPM 목표. 최소 OS 검증 필요 |
| AR 안내 진입 파라미터·callback | 08 §5, 06 §6 | `NavigationRequest` + session stream 제안 |
| 권한 요청 주체 | 08 §6 | host 요청, SDK capability·typed error 반환 권장 |
| 공간 데이터 구축·관리 주체 | 08 §7 | 역할 분리와 versioned Venue Package 제안 |
| 단말 tier·폴백 UI | 08 §8, 07 §4 | SDK capability 판정, host 최종 UI 책임 제안 |

## 6. 핵심 요약

### 6.1 SDK 범위

- headless 측위 코어와 공개 session API를 필수 SDK 범위로 한다.
- 기본 2D·AR UI는 선택 module로 제공할 수 있으나 범위와 일정은 별도 결정한다.
- 최종 화면, branding, 예약·진료 workflow와 navigation stack은 host 앱이 소유한다.

### 6.2 측위 방식

- 카메라 기반 초기 절대 위치 확인과 모바일 모션 센서 기반 연속 추적을 결합한다.
- 위치·방향·불확실성·추적 상태를 제공한다.
- 자력계와 기압계는 지원 venue·단말에서 보조적으로 사용한다.
- BLE와 Wi-Fi는 현재 제품 런타임의 기본 측위 입력이 아니다.

### 6.3 SDK 제공 목표

- Android: versioned Maven artifact/AAR
- iOS: XCFramework + SPM binary target
- 목표 최소 OS: Android API 24, iOS 15.6
- 현재 PoC와 목표 최소 OS·도구체인의 공식 호환성 검증은 남아 있다.

### 6.4 공간 데이터

- 도면·POI·앵커·측위 맵·경로 데이터는 SDK binary에 고정하지 않는다.
- 병원·건물·층별 versioned Venue Package로 구축·검수·배포한다.
- 3D digital twin asset은 Venue Package의 선택 layer 또는 별도 package로 관리한다.

### 6.5 UI와 폴백

- SDK가 단말 capability와 사용 가능한 mode를 반환한다.
- host 앱이 AR, 실시간 2D, 정적 2D 또는 지원 불가 화면을 선택한다.
- 권한 설명과 OS 권한 요청도 host 앱이 담당한다.

## 7. 현재 검증 현황

| 항목 | 결과 | 제한 |
|---|---|---|
| core 단위 테스트 | 138 tests, 0 failures, 3 ignored | 전체 정확도·실기기 인증 아님 |
| Android 앱 단위 테스트 | 12 tests, 0 failures | instrumentation·장시간 시험 아님 |
| Android release AAR | local 생성 가능 | Maven 게시 전 |
| iOS simulator arm64 framework | link 가능 | XCFramework/SPM 전 |
| Android 실기기 | Galaxy S22 PoC 기록 | OS·다기종 회귀 부족 |
| iOS 실기기 | iPhone 14 Pro Max PoC 기록 | 목표 iOS 15.6 검증 아님 |

## 8. 이번 송부에 포함되지 않는 산출물

- Maven repository에 게시된 제품 Android SDK
- XCFramework/SPM으로 설치 가능한 제품 iOS SDK
- 최종 확정 API v0.1 binary
- 전체 병원·층의 승인 완료 Venue Package
- 운영 위치 확인 endpoint와 production credential
- 공식 전 단말 호환성 인증 보고서
- 정확도·가용성 SLA acceptance 보고서
- 최종 UI/UX 화면 설계서와 디자인 asset
- 편집 완료된 PoC 시연 영상·스크린샷 package
- AI 챗봇 SDK 상세 명세

## 9. 회의 목표

회의에서는 기술 구현 세부사항을 다시 설명하는 것보다 다음 결과를 확보하는 것을 목표로 한다.

1. Android·iOS SDK 배포 방식 승인
2. 최소 OS의 목표값과 검증 계획 승인
3. API v0.1 확정 절차와 담당 범위 승인
4. 권한 요청 주체 확정
5. SDK UI module과 최종 UI 소유 범위 결정
6. 공간 데이터 구축·검수·운영 RACI 결정
7. 단말 tier와 폴백 UI 책임 결정
8. 최초 통합·서베이·검증 일정의 입력조건 확정

구체적인 결정 항목과 기록표는 `09-meeting-decision-checklist.md`를 사용한다.

## 10. 문서 사용 제한

- 외부 공개 사례는 당사의 수행 실적 또는 동일 성능 보장 자료가 아니다.
- PoC 수치는 해당 단말·공간·조건에 한정된다.
- Integration Target API는 구현과 호환성 검증 전 변경될 수 있다.
- 내부 모델, 학습 데이터, 융합 수식, 임계값 및 공간 데이터 생성 알고리즘은 본 패키지 공개 범위에서 제외한다.
