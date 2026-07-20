# SDK 통합 회의 예상 질문 및 주요 답변

> 문서 등급: CONFIDENTIAL - Integration Partner Use Only
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 목적

본 문서는 SDK 기술 검토와 통합 회의에서 예상되는 질문에 대해 현재 저장소 상태와 권장 통합안을 기준으로 일관된 답변을 제공하기 위한 자료이다.

답변은 다음 상태로 구분한다.

| 상태 | 의미 |
|---|---|
| Ready | 현재 사실과 권장안으로 즉시 답변 가능 |
| Decision Required | 회의 또는 계약에서 범위·책임 결정 필요 |
| Validation Required | 빌드·실기기·현장 시험 후 확정 가능 |
| Deferred | 별도 후속 협의 항목 |

## 2. 답변 원칙

- Current PoC와 제품 SDK 완료 상태를 구분한다.
- 목표 최소 OS와 공식 지원 OS를 구분한다.
- PoC 정확도와 제품 SLA를 구분한다.
- 외부 공개 사례를 자체 납품 실적으로 표현하지 않는다.
- 모델 구조, 학습 데이터, 융합 수식, 임계값 등 재현 가능한 내부 기술은 답변하지 않는다.
- 미정인 일정이나 성능은 임의 날짜·수치로 확답하지 않고 확정 조건을 설명한다.

## 3. 가장 가능성이 높은 질문

| 번호 | 예상 질문 | 핵심 답변 | 상태 |
|---|---|---|---|
| Q-01 | 지금 SDK를 바로 전달할 수 있습니까? | PoC 검토용 local artifact는 있으나 제품 배포본은 아직 아니다. | Ready |
| Q-02 | SDK 안에 화면이 전부 포함됩니까? | headless core가 필수이며 기본 UI는 선택 module로 협의한다. | Decision Required |
| Q-03 | 측위 맵과 digital twin도 SDK에 포함됩니까? | SDK binary와 분리된 Venue Package 또는 data layer로 전달한다. | Ready |
| Q-04 | 최소 지원 OS는 확정입니까? | API 24·iOS 15.6은 목표이며 공식 검증 전이다. | Validation Required |
| Q-05 | AR 화면은 어떻게 진입합니까? | `NavigationRequest`로 session을 생성하고 stream을 구독하는 구조를 제안한다. | Decision Required |
| Q-06 | 권한은 누가 요청합니까? | Host App이 요청하고 SDK가 capability·typed error를 반환한다. | Ready |
| Q-07 | 정확도는 어느 정도입니까? | PoC 참고 결과는 있으나 제품 보장값은 대표 venue·단말 acceptance 후 확정한다. | Validation Required |
| Q-08 | 인터넷 없이 동작합니까? | 연속 추적은 단말에서 가능하나 현재 초기 위치 확인은 service-assisted 방식이다. | Ready |
| Q-09 | AR 미지원 단말은 어떻게 합니까? | 실시간 2D, 조건 부족 시 정적 2D로 폴백한다. | Decision Required |
| Q-10 | 병원 도면·POI·서베이는 누가 담당합니까? | 원천자료·승인과 서베이·runtime map 생성을 역할 분리한다. | Decision Required |
| Q-11 | UI/UX는 언제 확정합니까? | API v0.1 동결 전에 핵심 flow와 폴백 wireframe을 확정해야 한다. | Decision Required |
| Q-12 | AI 챗봇 SDK는 어떻게 제공됩니까? | 전남대학교와 세부 협의 후 별도로 전달한다. | Deferred |

## 4. SDK 범위와 제공 형태

### Q-01. 현재 SDK를 바로 전달할 수 있습니까?

**답변 상태: Ready**

현재 Android local release AAR과 iOS local KMP static framework를 생성할 수 있고 PoC 앱과 테스트 자료가 존재한다. 
다만 Maven에 게시된 제품 Android SDK, XCFramework/SPM 제품 package, 운영 endpoint, 최종 API v0.1과 공식 호환성 보고서는 아직 완성되지 않았다.

현재 artifact는 구조와 PoC 동작 검토용이며 제품 통합 완료본으로 전달하면 안 된다.

### Q-02. 최종 제공 형태는 무엇입니까?

**답변 상태: Decision Required**

권장 제공 형태는 다음과 같다.

- Android: versioned Maven artifact/AAR
- iOS: XCFramework를 포함한 SPM binary target
- 공간 데이터: SDK와 별도 versioned Venue Package
- UI: 선택 제공 시 별도 UI module
- 문서: API reference, release notes, integration sample, compatibility matrix

Repository 위치, 인증, simulator architecture와 release 절차는 회의에서 결정해야 한다.

### Q-03. 소스코드도 전달합니까?

**답변 상태: Decision Required**

소스 코드는 전달하지 않을 예정이며 binary SDK와 공개 API 문서를 전달 할 예정이다.

### Q-04. 호스트 앱이 KMP이므로 SDK도 KMP dependency 하나로 제공됩니까?

**답변 상태: Decision Required**

측위 코어는 KMP 공통 코드로 구성되어 있지만 제품 배포는 Android Maven/AAR와 iOS XCFramework/SPM의 플랫폼 artifact가 기본안이다. 호스트 공통 코드에서 직접 소비할 KMP library publication까지 제공할지는 빌드·Swift export·dependency 충돌을 검토한 뒤 결정한다.

### Q-05. SDK 안에 프론트엔드가 모두 포함됩니까?

**답변 상태: Decision Required**

SDK 본체는 위치·상태·이벤트·오류를 제공하는 headless core가 기준이다. 최종 화면, branding, 예약·진료 flow와 navigation stack은 Host App이 소유하는 것을 권장한다.

통합 속도를 위해 기본 2D 지도·블루닷·AR 화면을 optional UI module로 제공할 수 있지만 제공 범위, customization과 일정은 별도 확정이 필요하다.

### Q-06. Compose Multiplatform UI module이 이미 있습니까?

**답변 상태: Ready**

Android Compose와 iOS SwiftUI·3D PoC 화면은 존재하지만 외부 통합용 Compose Multiplatform 제품 UI module은 없다. 현재 화면을 바로 제품 component로 간주할 수 없으며 API, theme, accessibility, lifecycle과 폴백을 정리하는 제품화 작업이 필요하다.

## 5. API와 Host App 연동

### Q-07. AR 안내는 어떤 API로 시작합니까?

**답변 상태: Decision Required**

다음 request를 이용해 session을 생성하는 방식을 제안한다.

```kotlin
NavigationRequest(
    venueId = "hospital-main",
    destinationId = "clinic-301",
    floorId = null,
    preferredMode = NavigationMode.AUTO,
)
```

Host App은 `positions`, `states`, `events`, `errors` stream을 구독하고 `start()`와 `stop()`으로 lifecycle을 제어한다.

### Q-08. Host App이 전달해야 하는 필수 값은 무엇입니까?

**답변 상태: Ready**

필수 값은 `venueId`이다. 경로 안내에는 `destinationId`가 필요하며 시작층을 알고 있는 경우 `floorId`를 hint로 전달할 수 있다. 예약번호, 사용자 식별정보와 진료정보는 SDK에 전달하지 않고 Host App이 목적지 ID로 변환한다.

### Q-09. SDK가 반환하는 정보는 무엇입니까?

**답변 상태: Ready**

- venue·floor
- x/y 위치
- 사용자 진행 방향
- 위치 불확실성
- timestamp
- 초기 측위·정렬·추적·보류·재획득 상태
- 층 변경·경로 이탈·목적지 도착·재확인 이벤트
- 권한·단말·공간 데이터·네트워크·위치 확인 오류

현재 코어에는 x/y·방향·불확실성·추적 단계가 존재하고 나머지는 제품 Facade에서 통합할 목표이다.

### Q-10. 예약정보를 SDK에 전달해야 합니까?

**답변 상태: Ready**

전달할 필요가 없다. Host App이 예약정보에서 목적지 ID를 결정해 SDK에 전달한다. SDK가 예약·사용자·진료 domain을 직접 알게 하면 결합도와 개인정보 범위가 불필요하게 커진다.

### Q-11. 목적지를 안내 중에 변경할 수 있습니까?

**답변 상태: Decision Required**

현재 제품 API에는 확정된 변경 계약이 없다. 새 session을 생성하는 방식과 동일 session의 `updateDestination` 방식 중 하나를 API v0.1에서 결정해야 한다.

### Q-12. 앱이 background로 이동하면 측위는 계속됩니까?

**답변 상태: Decision Required**

현재 제품 정책은 미정이다. 개인정보, 배터리, OS 제한과 사용 흐름을 고려하면 기본은 suspend 또는 stop으로 두고 복귀 시 재확인하는 방식을 우선 검토한다.

### Q-13. iOS에서는 Kotlin Flow를 어떻게 사용합니까?

**답변 상태: Decision Required**

Swift `AsyncSequence`, callback adapter 또는 KMP Swift export 중 하나를 제품 API로 제공해야 한다. 취소, main actor와 메모리 해제를 sample app에서 검증한 뒤 방식을 확정한다.

## 6. 권한·개인정보·보안

### Q-14. 카메라·Motion·위치 권한은 누가 요청합니까?

**답변 상태: Ready**

권한 사전 설명과 OS 권한 요청은 Host App이 담당한다. SDK는 현재 mode에 필요한 권한과 누락 상태를 반환하고, 권한이 없으면 typed error를 제공한다. SDK가 임의 시점에 OS 권한 팝업을 직접 띄우지 않는다.

### Q-15. 위치 권한이 항상 필요합니까?

**답변 상태: Ready**

기본 모션 센서·카메라 측위만으로 위치 권한이 항상 필요한 것은 아니다. BLE 또는 Wi-Fi 보조 기능과 플랫폼 정책에 따라 필요할 수 있다. 현재 Android PoC의 위치·Wi-Fi 권한은 survey 기능을 포함한 데모 설정이므로 제품 기본 권한으로 그대로 사용하지 않는다.

### Q-16. 카메라는 계속 촬영합니까?

**답변 상태: Ready**

Current PoC에서는 초기 위치 확인 또는 재획득 시 정지 이미지 한 장을 사용하고 이후 연속 추적은 모션 센서 기반으로 수행한다. AR 화면을 사용하는 동안에는 화면 표시를 위해 camera session이 활성화될 수 있다.

### Q-17. 촬영 이미지는 서버로 전송하거나 저장합니까?

**답변 상태: Decision Required**

현재 PoC의 초기 위치 확인은 service-assisted 방식이라 이미지가 개발용 서비스로 전송된다. 운영 환경에서는 TLS, 인증, 전송·보관·삭제 정책을 별도로 확정해야 한다. 권장 기본안은 측위 처리 후 이미지를 저장하지 않는 방식이다.

### Q-18. 사용자 위치나 이동 경로를 저장합니까?

**답변 상태: Decision Required**

SDK의 기본 기능은 실시간 위치 결과 제공이며 장기 저장을 필수로 하지 않는다. 운영 진단 로그가 필요하면 사용자 동의, 수집 범위, 익명화, 보관 기간과 삭제 정책을 별도로 결정해야 한다.

### Q-19. 현재 PoC 통신 설정을 운영에 사용할 수 있습니까?

**답변 상태: Ready**

사용할 수 없다. 현재 local network와 개발용 통신 예외는 PoC 전용이다. 운영에서는 TLS, endpoint 인증, credential 관리, 요청 무결성, rate limit과 장애 정책이 필요하다.

## 7. 측위 방식과 성능

### Q-20. 어떤 센서를 사용합니까?

**답변 상태: Ready**

기본 입력은 가속도계, 자이로스코프, 단말 자세·회전 정보와 카메라이다. 자력계와 기압계는 선택적 보조 입력이다. BLE는 확장 interface 단계이며 Wi-Fi는 현재 survey 도구 중심이라 기본 런타임 입력으로 설명하지 않는다.

### Q-21. 측위 방식은 무엇입니까?

**답변 상태: Ready**

카메라 기반 절대 위치 확인, 모션 센서 기반 연속 상대 이동 추정, 공간 데이터 기반 제약과 보조 신호를 결합하는 하이브리드 방식이다. 내부 모델 구조, 특징량, 융합 수식과 임계값은 비공개 엔진 구현이다.

### Q-22. 정확도는 몇 미터입니까?

**답변 상태: Validation Required**

통제 환경과 일부 현장에서 PoC 참고 결과는 존재하지만 전체 병원, 군중, 조도와 단말군에 대한 제품 보장값은 아직 없다. 공식 정확도는 대상 venue, 대표 동선, 단말, 시작 조건과 성공 기준을 고정한 acceptance 시험 후 제시한다.

단일 최고 수치나 통제 환경 중앙값을 제품 SLA처럼 답변하지 않는다.

### Q-23. 위치가 틀렸을 때 계속 안내합니까?

**답변 상태: Ready**

위치 불확실성과 추적 상태를 함께 평가한다. 신뢰도가 낮으면 `HOLD`로 안내 갱신을 제한하고, 필요하면 `RE_ACQUIRE` 이벤트를 통해 카메라 재확인 또는 2D 폴백을 요청한다.

### Q-24. 완전 오프라인으로 동작합니까?

**답변 상태: Ready**

현재 연속 모션 추적은 단말에서 수행되지만 초기 절대 위치 확인은 service-assisted 방식이다. Venue Package를 앱에 동봉하거나 cache할 수 있어도 현재 전체 측위가 완전 오프라인인 것은 아니다. 온디바이스 절대 위치 확인은 향후 목표이며 현재 완료 기능으로 설명하지 않는다.

향후 온디바이스 포팅을 통해 오프라인 동작이 가능하도록 구성 후 내부 검증을 통해 판단 할 예정이다.

### Q-25. 네트워크가 끊기면 어떻게 됩니까?

**답변 상태: Decision Required**

이미 초기 위치가 확보된 짧은 구간에서는 단말 추적을 계속할 수 있지만 재획득이 필요한 시점에는 위치 확인이 제한된다. 재시도, cached static route, QR·고정 출발점 또는 안내 불가 화면 중 폴백 정책을 결정해야 한다.

### Q-26. 기압계나 자력계가 없는 단말도 지원합니까?

**답변 상태: Ready**

두 센서는 기본 필수 센서가 아니다. 
자력계가 없으면 해당 보정을 비활성화하고, 기압계가 없으면 자동 층 전환을 시각 위치 확인, 시작층 hint 또는 사용자 선택으로 보완한다.

### Q-27. SDK 크기와 배터리 사용량은 얼마입니까?

**답변 상태: Validation Required**

제품 전체 크기와 배터리·발열 기준은 아직 공식 측정 전이다. local AAR 크기는 모델, 추론 runtime, Venue Package와 선택 UI가 포함된 실제 앱 증가분을 의미하지 않는다. 제품 packaging 후 대표 단말에서 측정해야 한다.

## 8. 공간 데이터·서베이·Digital Twin

### Q-28. 측위 맵은 SDK에 포함해서 전달합니까?

**답변 상태: Ready**

SDK binary에 고정하지 않고 병원·건물·층별 Venue Package로 전달하는 것이 권장안이다. 
SDK와 공간 데이터를 분리하면 공간 변경 시 앱과 SDK를 다시 배포하지 않고 package만 검증·갱신할 수 있다.

### Q-29. Venue Package에는 무엇이 포함됩니까?

**답변 상태: Ready**

- 도면과 좌표 metadata
- 건물·층 식별정보
- POI와 경로 graph
- 벽·이동 가능 영역
- 위치 확인·보정용 runtime map
- package version, schema, checksum과 호환성 정보

내부 map 파일 구조와 구축 알고리즘은 외부 API로 노출하지 않는다.

### Q-30. Digital twin도 Venue Package에 포함됩니까?

**답변 상태: Decision Required**

3D mesh·model·texture는 Venue Package의 선택 layer 또는 별도 Package로 관리하는 방식을 제안한다. 파일 크기, update 주기와 renderer 책임이 측위 데이터와 다르므로 SDK binary에는 포함하지 않는다.

### Q-31. 도면·앵커·POI는 누가 만듭니까?

**답변 상태: Decision Required**

공간 데이터 원천 영역이 최신 도면·BIM·POI·출입정책과 최종 승인을 제공하고, SDK 범위가 현장 서베이·좌표 정합·runtime map·Venue Package 생성과 기술 QA를 담당하는 분담을 권장한다. 
Host App은 `venueId`와 `destinationId`를 업무 flow에 연결한다.

### Q-32. 병원 공간이 변경되면 누가 갱신합니까?

**답변 상태: Decision Required**

공간 변경 통보, 영향 분석, 재서베이 조건, package 재생성, 승인, 배포와 rollback 책임을 운영 RACI와 SLA로 정해야 한다. 
현재 공식 갱신 계약은 없다.

### Q-33. 모든 병원과 층의 맵이 준비되어 있습니까?

**답변 상태: Ready**

아니다. 일부 시험 venue 데이터와 구축 도구가 존재하지만 전체 병원·층의 승인 완료 package는 없다. 
최초 구축 범위와 원천자료, 현장 접근 일정이 확정되어야 구축 일정을 계산할 수 있다.

### Q-34. 맵을 앱 업데이트 없이 바꿀 수 있습니까?

**답변 상태: Decision Required**

제품 목표는 versioned Venue Package를 별도 저장소에서 준비·검증해 독립 갱신하는 것이다. 앱 동봉, SDK download 또는 혼합 방식 중 하나를 운영·보안 요구사항에 맞춰 결정해야 한다.

## 9. 단말 호환성과 폴백

### Q-35. 공식 지원 단말은 무엇입니까?

**답변 상태: Validation Required**

현재 공식 단말 목록은 없다. 실기기 PoC 기록은 Galaxy S22와 iPhone 14 Pro Max에 한정된다. 
Android API 24와 iOS 15.6 목표 범위, OEM·SoC·AR 지원 여부를 포함한 시험 matrix를 통과한 뒤 release별 지원표를 제공해야 한다.

### Q-36. 최소 지원 OS는 무엇입니까?

**답변 상태: Validation Required**

목표는 Android API 24와 iOS 15.6이다. Android core는 API 24지만 PoC 앱은 API 26이고, iOS PoC는 16.0이므로 최소 OS 실기기 검증 전에는 공식 지원으로 확정하지 않는다.

### Q-37. ARCore·ARKit 미지원 단말은 사용할 수 없습니까?

**답변 상태: Ready**

AR 안내는 사용할 수 없지만 Motion, camera와 위치 확인 조건을 충족하면 실시간 2D 안내를 제공할 수 있다. 실시간 측위 조건까지 부족하면 정적 2D 또는 지원 불가 화면으로 전환한다.

### Q-38. 카메라 권한을 거부해도 2D 위치 안내가 됩니까?

**답변 상태: Decision Required**

현재 구조에서는 초기 절대 위치 확인에 카메라가 필요하므로 단순히 AR만 끄고 실시간 블루닷을 제공한다고 보장할 수 없다. 
QR, 고정 출발점 또는 수동 위치 선택 같은 대체 앵커가 있으면 정적 경로나 제한적 안내를 제공할 수 있다.

### Q-39. SDK가 단말 tier를 결정합니까?

**답변 상태: Decision Required**

SDK가 OS, Motion, camera, AR, barometer, 권한과 Venue Package 상태를 평가해 capability를 반환하고 Host App이 최종 mode를 선택하는 방식을 권장한다. SDK가 최종 tier enum까지 반환할지는 API v0.1에서 결정한다.

## 10. 일정·검증·운영

### Q-40. 제품 SDK 완료 일정은 언제입니까?

**답변 상태: Decision Required**

현재 확정된 완료일은 없다. 배포 방식, API, UI module, 최초 venue 범위, 최소 OS, 운영 service와 acceptance 기준이 먼저 확정되어야 일정 산정이 가능하다.

일정은 최소 다음 milestone로 분리해야 한다.

1. API·책임 범위 동결
2. Maven·SPM packaging
3. 최초 Venue Package 구축
4. UI/UX 초안과 host 통합
5. 대표 단말·현장 검증
6. 보안·운영 검토와 release

### Q-41. UI/UX 설계는 언제 시작합니까?

**답변 상태: Decision Required**

SDK 구현이 끝난 뒤가 아니라 API v0.1을 동결하기 전에 시작해야 한다. 진입, 권한, 위치 확인, 2D, AR, 층 변경, 추적 저하, 재획득, 폴백과 도착 화면을 먼저 정의해야 callback과 state가 확정된다.
WBS상 화면 설계는 레몬헬스케어 담당으로 설정되어 있으므로 화면 세부 설계 일정과 업무 분장에 대해 구체적으로 협의해야 한다.

### Q-42. 현재 테스트는 어느 정도 완료됐습니까?

**답변 상태: Ready**

- core 단위 테스트 보고서: 138 tests, 0 failures, 3 ignored
- Android 앱 단위 테스트 보고서: 12 tests, 0 failures
- local Android release AAR 생성 가능
- iOS simulator arm64 framework link 가능
- Galaxy S22와 iPhone 14 Pro Max PoC 기록 존재

이는 제품 호환성·정확도·배터리·AR 성능 인증 완료를 의미하지 않는다.

### Q-43. 어떤 시험을 추가해야 합니까?

**답변 상태: Ready**

- API 24와 iOS 15.6 실기기
- 목표 Kotlin·AGP·compileSdk 통합
- 다기종 센서·카메라 차이
- 권한 거부·background·반복 session
- 네트워크 장애와 재획득
- AR FPS·발열·메모리
- 병원별 위치·층·경로 acceptance
- 장시간 배터리·resource 해제

### Q-44. 장애와 공간 갱신 지원은 어떻게 합니까?

**답변 상태: Decision Required**

SDK release 지원기간, severity, 응답시간, 필요한 진단정보, Venue Package 갱신 SLA와 rollback을 운영계약으로 정의해야 한다. 현재 공식 SLA(Service Level Agreement)는 없다.

### Q-45. 라이브러리 충돌 가능성은 없습니까?

**답변 상태: Validation Required**

현재 저장소의 Kotlin·AGP·compileSdk가 목표 Host App 환경과 다르고, Android·iOS 추론 runtime dependency도 존재한다. 
목표 조합에서 dependency graph, binary size, symbol, coroutine·serialization 호환성과 license를 검증해야 한다.

## 11. 유사 사례·기술 공개 범위

### Q-46. 유사 병원 적용 사례가 있습니까?

**답변 상태: Ready**

UCHealth, NHS Leicester, St. Olavs Hospital과 Quironsalud 등 공개 사례를 조사했다. 이 자료는 업계 구현 패턴을 검토하기 위한 외부 공개 사례이며 자체 수행 실적으로 표현하지 않는다.

### Q-47. 측위 알고리즘을 상세히 제공할 수 있습니까?

**답변 상태: Ready**

사용 센서, 초기 위치 확인, 연속 추적, 공간 제약, 상태와 공개 입출력은 제공할 수 있다. 
모델 구조, 학습 데이터, 특징량, 융합 수식, 내부 임계값, 위치 검색·맵 생성 알고리즘은 독자 기술로 SDK 내부에 유지한다.

## 12. AI 챗봇 SDK

### Q-48. AI 챗봇 SDK는 어떤 형태로 제공됩니까?

**답변 상태: Deferred**

> AI 챗봇 SDK의 제공 형태, 기능 범위 및 연동 방식은 전남대학교와 세부적으로 논의한 후 추후 상세 내용을 별도로 전달드릴 예정입니다. 현 단계의 Position SDK 기술자료 및 통합 범위에는 AI 챗봇 SDK를 포함하지 않습니다.

## 13. 현장에서 답변을 보류해야 하는 질문

다음 질문은 현재 즉답하지 않고 확정 조건을 설명해야 한다.

| 질문 | 답변 방식 |
|---|---|
| 모든 병원에서 정확도가 몇 m인가 | venue·단말 acceptance 후 공식 수치 제공 |
| SDK 완료일이 정확히 언제인가 | 범위·API·UI·venue·시험 결정 후 일정 산정 |
| 모든 Android·iPhone에서 동작하는가 | 공식 시험 matrix 완료 후 release별 지원표 제공 |
| AR 화면을 원하는 대로 전부 바꿀 수 있는가 | UI module 범위와 customization 계약 후 답변 |
| 카메라 없이도 실시간 위치가 항상 가능한가 | 대체 절대 앵커 설계 여부 확인 후 답변 |
| 완전 오프라인인가 | 현재는 아니며 온디바이스 절대 측위 완료 후 답변 |
| 이미지와 위치정보를 절대 저장하지 않는가 | 운영 보안·로그 정책 확정 후 공식화 |
| 전체 공간 구축 비용과 기간은 얼마인가 | 대상 층·면적·원천자료·현장조건 확인 후 산정 |

## 14. 회의 종료 시 확인할 답변

- [ ] SDK binary와 UI module의 제공 범위가 결정되었는가
- [ ] 최소 OS를 목표값과 공식 지원값으로 구분했는가
- [ ] AR 진입 request와 callback 검토 방식이 정해졌는가
- [ ] 권한 요청 책임이 확정되었는가
- [ ] 최초 venue·층·서베이 범위가 정해졌는가
- [ ] Venue Package와 digital twin 전달 방식이 정해졌는가
- [ ] 단말 tier와 폴백 UI 책임이 정해졌는가
- [ ] UI/UX 초안과 API freeze 일정이 정해졌는가
- [ ] 추가 검증자료와 다음 회의 입력물이 정해졌는가
- [ ] AI 챗봇이 후속 협의로 분리되었는가
