# SDK 포팅 사전 확인사항 답변서

> 문서 등급: CONFIDENTIAL - Integration Partner Use Only
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 문서 목적

본 문서는 SDK 포팅과 호스트 앱 통합 설계를 위해 사전 확인이 필요한 다음 5개 항목에 대한 현재 답변과 결정 필요사항을 정리한다.

1. SDK 제공 형태 및 최소 지원 OS
2. AR 안내 진입 파라미터 및 콜백 인터페이스
3. 카메라·위치·모션 센서 권한 요청 주체
4. 병원 공간 데이터의 구축·관리 주체
5. 단말 티어 및 AR 미지원 단말의 폴백 UI 책임

본 문서의 제공 목표와 API 초안은 현재 저장소와 PoC 구현을 기준으로 작성되었으며, 제품 패키지·공식 호환성·운영 책임은 검증과 협의 결과에 따라 변경될 수 있다.

## 2. 상태 요약

| 항목 | 현재 상태 | 핵심 답변 |
|---|---|---|
| SDK 제공 형태·최소 OS | 부분 확정·검증 필요 | Android Maven/AAR, iOS XCFramework/SPM 목표. API 24·iOS 15.6은 목표 최소 OS |
| AR 진입 API·콜백 | 제품 API 미확정 | `NavigationRequest`와 session stream 구조 제안 |
| 권한 요청 주체 | 확정 권장 | 호스트 앱이 요청하고 SDK가 필요 권한·capability·오류 반환 |
| 공간 데이터 책임 | 역할·운영 결정 필요 | 원천자료·승인과 서베이·runtime map 구축을 분리하고 Venue Package로 관리 |
| 단말 티어·폴백 UI | 정책·API 미확정 | SDK가 capability를 판정하고 호스트 앱이 최종 화면 선택 |

## 3. SDK 제공 형태 및 최소 지원 OS

### 3.1 공식 답변안

Android는 버전 관리가 가능한 Maven 기반 AAR 형태로, iOS는 XCFramework를 포함한 SPM Binary Package 형태로 제공하는 것을 목표로 한다.

현재 Android는 로컬 Release AAR 생성이 가능하며, iOS는 KMP 기반 정적 Framework 생성이 가능한 상태이다. Maven 저장소 게시와 XCFramework/SPM 제품 패키징은 추가 작업이 필요하다.

목표 최소 지원 OS는 Android API 24와 iOS 15.6이다. 다만 현재 PoC 앱은 Android API 26, iOS 16.0 기준으로 구성되어 있어, 목표 최소 OS는 실기기 및 통합 검증 후 공식 지원 범위로 확정할 예정이다.

### 3.2 현재 상태와 목표 구분

| 플랫폼 | 현재 가능한 항목 | 제품 제공 목표 | 남은 확인사항 |
|---|---|---|---|
| Android | local Release AAR 생성 | versioned Maven artifact/AAR | 게시 저장소·POM·접근 정책·API 24 실기기 검증 |
| iOS | local KMP static Framework 생성 | XCFramework + SPM Binary Target | device·simulator slice·SPM 설치·iOS 15.6 실기기 검증 |

### 3.3 답변 상태

제공 목표는 정해졌지만 제품 배포본과 최소 OS 공식 검증은 완료 전이다.

## 4. AR 안내 진입 파라미터 및 콜백 인터페이스

### 4.1 공식 답변안

AR 안내는 호스트 앱이 장소와 목적지 정보를 전달하여 내비게이션 세션을 생성하고, SDK가 위치·상태·이벤트·오류를 stream 또는 callback으로 반환하는 구조를 제안한다.

필수 입력값은 `venueId`와 `destinationId`이며, `floorId`와 안내 모드는 선택값으로 구성할 예정이다. 예약번호나 사용자·진료정보는 SDK에 직접 전달하지 않고, 호스트 앱에서 목적지 ID로 변환하는 방식을 권장한다.

```kotlin
NavigationRequest(
    venueId = "hospital-main",
    destinationId = "clinic-301",
    floorId = null,
    preferredMode = NavigationMode.AUTO,
)
```

호스트 앱은 내비게이션 session을 생성한 후 `start()`와 `stop()`으로 lifecycle을 제어하고 다음 결과를 구독한다.

| 출력 구분 | 주요 내용 |
|---|---|
| 위치 | `x`, `y`, `floorId`, `heading`, `accuracy`, `timestamp` |
| 상태 | 초기화, 위치 확인, 추적, 신뢰도 저하, 재획득, 종료 |
| 이벤트 | 경로 이탈, 층 변경, 재촬영 필요, 목적지 도착 |
| 오류 | 권한 없음, 단말 미지원, 공간 데이터 없음, 네트워크 오류, 초기 위치 확인 실패 |

### 4.2 현재 구현과 제품 API 구분

현재 코어에는 시작·종료·초기 위치 설정과 위치 Flow가 존재한다. 위 `NavigationRequest`, session lifecycle과 통합 callback 계약은 제품용 API 초안이며 회의 후 확정이 필요하다.

### 4.3 답변 상태

내부 데이터 모델 일부는 존재하지만 호스트 연동용 AR 내비게이션 API는 미확정이다.

## 5. 카메라·위치·모션 센서 권한 요청 주체

### 5.1 공식 답변안

권한 안내 화면과 OS 권한 요청은 호스트 앱이 담당하고, SDK는 현재 기능에 필요한 권한과 capability 상태를 반환하는 구조를 권장한다. SDK가 임의 시점에 직접 권한 팝업을 표시하지 않는다.

권한이 없거나 거부된 경우 SDK는 구조화된 오류 또는 사용 가능한 대체 안내 모드를 반환하고, 설정 이동·재요청·폴백 화면은 호스트 앱이 처리한다.

### 5.2 권장 책임 범위

| 구분 | 책임 |
|---|---|
| 호스트 앱 | 권한 사전 설명, OS 권한 요청, 거부·영구거부 처리 |
| SDK | 필요 권한 목록, 권한 누락 상태, 단말 capability와 typed error 제공 |
| 호스트 앱 | 설정 이동, 재요청, 2D·정적 안내 화면 선택 |
| 측위 SDK 범위 제외 | 푸시 권한과 알림 정책 |

위치 권한은 모든 측위 모드에서 항상 필요한 것은 아니며, BLE·Wi-Fi 보조 기능 또는 플랫폼 정책에 따라 필요 여부를 구분한다. 현재 PoC의 survey 관련 권한을 제품 SDK의 기본 권한으로 그대로 적용하지 않는다.

### 5.3 답변 상태

현재 PoC 구현과 권장안이 일치하므로 호스트 앱 요청 방식으로 확정하는 것을 권장한다.

## 6. 병원 공간 데이터 구축·관리 주체

### 6.1 공식 답변안

병원별 도면·POI·앵커·측위 맵·경로 데이터는 SDK binary에 고정하지 않고, 병원·건물·층별로 버전 관리되는 `Venue Package` 형태로 분리하여 제공하는 것을 권장한다.

공간 데이터 원천자료 제공과 최종 승인은 공간 데이터 보유 영역에서 담당하고, 현장 서베이·좌표 정합·측위용 runtime map 생성·기술 검증은 SDK 구축 범위에서 담당하는 역할 분담을 제안한다.

### 6.2 권장 역할 분담

| 구분 | 주요 책임 |
|---|---|
| 공간 데이터 보유 영역 | 최신 도면·BIM·POI·출입정책 제공 및 최종 승인 |
| SDK 구축 범위 | 현장 서베이, 좌표 정합, 앵커·측위 맵·경로 graph 생성, 정확도 검증 |
| 호스트 앱 | `venueId`, `destinationId`를 예약·진료 flow와 연결 |
| 공동 결정 | 공간 변경 통보, 재서베이 조건, package 배포·rollback, 갱신 SLA |

Digital Twin의 3D model·mesh·texture는 파일 크기와 갱신 주기가 다르므로 Venue Package의 선택 layer 또는 별도 Digital Twin Package로 관리하는 것이 적절하다. SDK binary에는 고정 포함하지 않는다.

### 6.3 답변 상태

구축 기술과 도구는 존재하지만 원천자료·승인·운영 갱신에 관한 최종 RACI와 SLA는 미확정이다.

## 7. 단말 티어 및 AR 미지원 단말 폴백 UI

### 7.1 공식 답변안

SDK가 OS 버전, 카메라, 모션 센서, AR 지원 여부, 권한 및 공간 데이터 준비 상태를 확인하여 사용 가능한 기능을 반환하고, 호스트 앱이 해당 결과에 따라 최종 화면을 선택하는 구조를 권장한다.

### 7.2 제안 단말 티어

| 티어 | 사용 가능 기능 | 폴백 |
|---|---|---|
| Tier A | AR 안내 + 실시간 2D | 정상 AR 안내 |
| Tier B | 실시간 측위 + 2D 안내 | 2D 블루닷·경로 안내 |
| Tier C | 실시간 측위 제한 | 정적 지도·경로 안내 |
| Unsupported | 필수 조건 미충족 | 지원 불가 또는 대체 안내 |

### 7.3 책임 범위

| 구분 | 책임 |
|---|---|
| SDK | 단말 capability 판정, 사용 가능한 mode와 오류 반환 |
| 호스트 앱 | AR·2D·정적 안내 화면 선택과 화면 전환 |
| 최종 폴백 UI | 호스트 앱의 디자인 시스템으로 구성 |
| 선택 UI module | 기본 2D·AR 화면이 필요한 경우 별도 범위로 협의 |

현재 2D 도면과 AR PoC 화면은 있으나, 공식 단말 티어표와 외부 공개용 capability API는 아직 확정되지 않았다.

카메라 권한이 거부된 경우 초기 절대 위치를 확인할 수 없으므로 실시간 블루닷 안내를 항상 보장할 수 없다. QR, 고정 출발점 또는 수동 위치 선택 같은 대체 기준점이 제공되면 정적 경로나 제한적 2D 안내를 구성할 수 있다.

### 7.4 답변 상태

권장 구조는 제시 가능하지만 티어 판정 기준, 공식 지원 단말, 선택 UI module과 최종 폴백 UI 책임은 회의에서 확정해야 한다.

## 8. 회의 결정 필요사항

| ID | 결정 항목 | 권장 기본안 |
|---|---|---|
| D-01 | Android 배포 방식 | private Maven을 통한 AAR 제공 |
| D-02 | iOS 배포 방식 | XCFramework를 포함한 SPM Binary Package 제공 |
| D-03 | 최소 OS 확정 조건 | API 24·iOS 15.6 실기기 및 호스트 통합 검증 |
| D-04 | AR 진입 API | `NavigationRequest` + session stream |
| D-05 | 권한 요청 주체 | 호스트 앱 요청, SDK 상태·오류 반환 |
| D-06 | 공간 데이터 역할 | 원천자료·승인과 서베이·runtime map 구축 분리 |
| D-07 | 공간 데이터 전달 | versioned Venue Package |
| D-08 | Digital Twin 전달 | 선택 layer 또는 별도 package |
| D-09 | 단말 분기 | SDK capability 판정, 호스트 앱 mode 선택 |
| D-10 | 폴백 UI | 호스트 앱 최종 책임, SDK UI는 선택 module |

## 9. 종합 답변

Android는 Maven을 통한 AAR, iOS는 XCFramework를 포함한 SPM Binary Package 제공을 목표로 하며, 목표 최소 OS는 Android API 24와 iOS 15.6이다. 현재 목표 최소 OS의 실기기 검증과 제품 배포 package 구성은 완료 전이다.

안내 진입은 `venueId`, 목적지와 선호 mode를 전달해 session을 생성하고 위치·상태·이벤트·오류 stream을 구독하는 구조를 제안한다. 권한 설명과 OS 권한 요청은 호스트 앱이 담당하고 SDK는 필요한 권한과 capability를 반환한다.

병원별 도면·POI·앵커·측위 맵과 Digital Twin은 SDK binary에 고정하지 않고 versioned Venue Package 또는 별도 data layer로 구축·검수·갱신한다. SDK는 AR·실시간 2D·정적 2D capability를 판정하고, 최종 폴백 화면과 업무 flow는 호스트 앱이 소유하는 구조를 기본안으로 한다. 선택적인 기본 2D·AR UI module 제공 범위는 별도 협의가 필요하다.
