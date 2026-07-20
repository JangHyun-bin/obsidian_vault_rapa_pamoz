# 단말 호환성 테스트 현황 및 지원 단말 가이드

> 문서 등급: CONFIDENTIAL - Integration Partner Use Only
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 목적

본 문서는 Position SDK의 목표 최소 OS, 필요한 단말 capability, 현재 빌드·자동화 테스트 결과, 실기기 검증 범위 및 공식 지원 단말 확정 전 필요한 시험 항목을 정의한다.

현재 저장소에는 전체 단말군을 대상으로 한 공식 호환성 인증 결과가 없다. 따라서 본 문서는 다음 세 범위를 구분한다.

| 구분 | 의미 |
|---|---|
| Verified PoC | 기록이 남아 있는 특정 단말·현장의 기능 검증 |
| Support Target | 연동 요구사항으로 제시된 목표 최소 범위 |
| Official Support | release별 시험을 통과한 공식 지원 범위. 현재 미확정 |

특정 PoC 단말에서 동작했다는 사실은 같은 OS의 모든 단말에 대한 호환성 보장을 의미하지 않는다.

## 2. 요약

| 항목 | 현재 판단 |
|---|---|
| Android 목표 최소 OS | API 24 |
| Android 현재 core 설정 | minSdk 24 |
| Android 현재 PoC 앱 설정 | minSdk 26, compile/targetSdk 35 |
| iOS 목표 최소 OS | iOS 15.6 |
| iOS 현재 PoC 설정 | iOS 16.0 |
| Android 실기기 기록 | Galaxy S22 `SM-S901N`, OS 버전 미기록 |
| iOS 실기기 기록 | iPhone 14 Pro Max `iPhone15,3`, iOS 27 beta |
| 공식 지원 단말 목록 | 없음 |
| API 24 실기기 검증 | 미수행 |
| iOS 15.6 실기기·회귀 검증 | 미수행 |
| AR 미지원 폴백 | 2D PoC는 존재, 제품 capability API·책임 계약 미확정 |

## 3. 기본 지원 조건

### 3.1 실시간 2D 측위

실시간 2D 위치·경로 안내에는 다음 조건이 필요하다.

- 지원 OS 버전
- 가속도계와 자이로스코프
- 안정된 단말 자세 또는 회전벡터 제공
- 후면 카메라
- 카메라와 Motion 사용 권한
- 대상 venue의 유효한 Venue Package
- Current PoC 기준 위치 확인 서비스에 접근 가능한 네트워크
- 측위 추론을 실행할 수 있는 CPU·메모리 여유

### 3.2 AR 안내

AR 안내에는 실시간 2D 측위 조건에 더해 다음 capability가 필요하다.

- Android ARCore 또는 iOS ARKit 호환 단말
- AR camera session을 안정적으로 실행할 수 있는 GPU·메모리
- AR용 공간 정합 데이터
- 카메라 영상과 경로 overlay를 지속 렌더링할 수 있는 성능

LiDAR는 현재 런타임 측위와 AR 안내의 필수 조건이 아니다. LiDAR·RoomPlan은 공간 구축과 digital twin 조사 도구에서 사용할 수 있다.

### 3.3 선택적 보조 센서

| 센서·기능 | 필수 여부 | 미지원 시 처리 |
|---|---|---|
| 자력계 | 선택 | 자기장 보정 비활성화 |
| 기압계 | 선택 | 자동 층 전환 제한, 시작층·VPS·사용자 선택 활용 |
| BLE | 현재 기본 범위 아님 | BLE 보조 위치 비활성화 |
| Wi-Fi fingerprint | 런타임 기본 범위 아님 | 영향 없음 |
| LiDAR | 불필요 | 런타임 영향 없음 |

## 4. 권장 단말 티어

공식 단말 목록이 확정되기 전에는 모델명보다 런타임 capability로 분기하는 방식을 권장한다.

| Tier | 조건 | SDK 제공 기능 | 호스트 앱 처리 |
|---|---|---|---|
| A - AR | 지원 OS, Motion, camera, position fix, AR 지원 | 실시간 위치, 2D, AR | AR 또는 2D 선택 |
| B - Live 2D | 지원 OS, Motion, camera, AR 미지원 또는 제한 | 실시간 위치, 2D | 2D 지도·블루닷·경로 |
| C - Static 2D | 실시간 측위 필수 조건 일부 부족 | 지도·정적 경로 데이터 | QR·지정 출발점 기반 안내 |
| Unsupported | 최소 OS 또는 필수 capability 미충족 | session 시작 불가 | 지원 불가 또는 대체 안내 |

단말 모델 allowlist만 사용하면 같은 모델의 OS·권한·센서 상태 차이를 반영하기 어렵다. SDK가 runtime capability를 반환하고 호스트 앱이 화면을 선택해야 한다.

## 5. 플랫폼별 목표와 현재 차이

### 5.1 Android

| 항목 | 현재 저장소 | 통합 목표 | 상태 |
|---|---|---|---|
| 최소 OS | core API 24, PoC 앱 API 26 | API 24 | API 24 실기기 미검증 |
| compileSdk | 35 | 36 | 미검증 |
| Kotlin | 2.0.21 | 2.3.x | 미검증 |
| AGP | 8.7 | 9.x | 미검증 |
| JVM | 17 | 호스트 조합 확인 | 검토 필요 |
| 배포 | local AAR | Maven artifact | 미완성 |
| AR 선언 | optional | optional + capability 분기 | PoC 적용 |

현재 PoC manifest에는 카메라·인터넷 외에 위치·Wi-Fi 조사 권한도 포함되어 있다. 이는 survey 기능을 포함한 데모 앱 설정이며, 제품 SDK의 기본 권한 요구사항으로 그대로 사용하지 않는다.

Android 12 이상에서 현재와 같은 고주기 센서 입력을 사용할 경우 관련 normal permission과 OS 동작 제한을 검토해야 한다. 최종 sampling 정책과 manifest 병합 결과는 제품 build에서 고정한다.

### 5.2 iOS

| 항목 | 현재 저장소 | 통합 목표 | 상태 |
|---|---|---|---|
| deployment target | iOS 16.0 | iOS 15.6 | 15.6 미검증 |
| device architecture | local arm64 framework 경로 | XCFramework arm64 | 부분 가능 |
| simulator | arm64 framework 링크 성공 | arm64 + x86_64 또는 지원 범위 명시 | 미완성 |
| 배포 | local framework·PoC dependency | SPM binary target | 미완성 |
| Motion | Swift PoC host 연결 | SDK adapter 내부 | 이관 필요 |
| Camera | Swift PoC host 연결 | SDK 또는 선택 UI module | 이관 필요 |

현재 PoC의 local network 및 임의 network load 허용 설정은 개발용 위치 확인 서비스에 접근하기 위한 것이다. 운영 endpoint에서는 TLS, 허용 domain과 보안 정책을 별도로 적용해야 한다.

## 6. 자동화 테스트와 빌드 결과

2026-07-13 현재 워크트리와 로컬 개발환경에서 확인한 결과이다.

| 검사 | 결과 | 범위와 해석 |
|---|---|---|
| `:core-positioning:testDebugUnitTest` | 성공 | 보고서 138 tests, 0 failures, 3 ignored |
| `:android-app:testDebugUnitTest` | 성공 | 보고서 12 tests, 0 failures |
| `:core-positioning:assembleRelease` | 성공 | local release AAR 생성 가능 |
| `linkDebugFrameworkIosSimulatorArm64` | 성공 | Apple Silicon simulator용 KMP framework 링크 가능 |
| iOS generic simulator 앱 build | 기존 실패 기록 | arm64 framework와 x86_64 simulator architecture 불일치 |

### 6.1 자동화 테스트가 검증하는 범위

- session start·stop과 위치 결과 방출
- 위치 상태 전환과 절대 위치 보정
- 공간 제약과 좌표 변환
- 층 추정 로직
- 경로 그래프와 navigation 계산
- Android venue 데이터 파싱
- 위치 확인 client 응답 파싱
- 일부 실제 수집 데이터 replay

### 6.2 자동화 테스트가 검증하지 않는 범위

- 모든 Android OEM 센서 특성
- Android API 24 실제 단말 동작
- iOS 15.6 실제 단말 동작
- 카메라 권한·영구거부 전체 사용자 흐름
- 실제 네트워크 지연·손실·서비스 장애
- 장시간 배터리·발열·메모리
- background·foreground 반복과 프로세스 복구
- ARCore·ARKit 전체 지원 단말
- 모든 병원·층·조도·군중 조건의 정확도

3개의 ignored 코어 테스트에는 일부 실제 데이터 fixture에 의존하는 replay가 포함된다. 자동화 테스트 성공을 전체 정확도 검증 완료로 해석하지 않는다.

## 7. 실기기 PoC 검증 기록

### 7.1 Galaxy S22

| 항목 | 내용 |
|---|---|
| 모델 | Galaxy S22 `SM-S901N` |
| OS | 저장소 기록에 명시되지 않음 |
| 현장 | 병원 외래 시험구역 및 계단 1↔2층 |
| 확인 내용 | Android 센서 수집, server-assisted 위치 확인·보행 PoC, 기압 기반 층 전환 |
| 층 전환 기록 | 1 → 2 → 1, 해당 시험에서 불필요한 층 떨림 미관찰 |
| 제한 | 단일 모델·제한된 현장·동선이며 배터리와 장시간 안정성 미측정 |

### 7.2 iPhone 14 Pro Max

| 항목 | 내용 |
|---|---|
| 모델 | iPhone 14 Pro Max `iPhone15,3` |
| OS | iOS 27 beta 기록 |
| 확인 내용 | CoreMotion 입력, 단말 내 연속 이동 추론, 카메라 1회 촬영, server-assisted 위치 확인, KMP 엔진 연결 |
| 공간 조사 | ARKit·RoomPlan 기반 조사 데이터 기록에 사용 |
| 제한 | 목표 최소 버전 iOS 15.6과 조건이 다르며 비 beta OS 회귀 결과가 아님 |

### 7.3 해석 제한

- 두 단말 기록은 PoC 기능 가능성을 확인한 것이며 공식 인증 결과가 아니다.
- Android와 iOS 사이의 동일 경로·동일 조건 정량 비교는 완료되지 않았다.
- 군중, 가림, 저조도 및 공간 변경 조건의 시각 위치 확인 견고화는 진행 중이다.
- AR 경로 안내의 단말별 FPS와 발열 시험은 완료되지 않았다.

## 8. 현재 지원 여부 판정 초안

제품 SDK의 `capabilities()`는 최소 다음 항목을 확인해야 한다.

```text
OS version
Motion sensor availability
Device attitude / rotation availability
Rear camera availability
Camera permission state
Motion permission state
Position fix service reachability
Venue Package readiness
AR framework support
Barometer availability
```

### 8.1 판정 예시

| 조건 | 판정 |
|---|---|
| Motion·camera·venue 준비, AR 지원 | Tier A |
| Motion·camera·venue 준비, AR 미지원 | Tier B |
| Motion 또는 camera 미지원, 정적 지도 사용 가능 | Tier C |
| 최소 OS 미충족 또는 venue 데이터 없음 | Unsupported 또는 준비 오류 |

네트워크 일시 장애는 단말 미지원으로 분류하지 않고 recoverable error로 반환해야 한다.

## 9. 권한별 폴백

| 상황 | SDK 상태·오류 | 권장 폴백 |
|---|---|---|
| Camera 최초 거부 | `PERMISSION_REQUIRED` | 권한 설명 후 재요청 또는 정적 2D |
| Camera 영구거부 | `PERMISSION_REQUIRED` | 설정 이동 또는 정적 2D |
| Motion 사용 불가 | `UNSUPPORTED_DEVICE` | 정적 2D·텍스트 안내 |
| AR 미지원 | AR capability `UNAVAILABLE` | 실시간 2D |
| 기압계 없음 | floor capability 제한 | 시작층·VPS·사용자 선택 |
| 위치 확인 서비스 장애 | recoverable position-fix error | 재시도, QR 시작점 또는 정적 2D |
| Venue Package 없음·손상 | venue error | 다운로드·재검증 후 시작 |

## 10. 공식 지원 전 필수 시험 매트릭스

### 10.1 Android

- API 24 실제 단말
- 지원 범위의 중간·최신 Android 버전
- Samsung 계열 최소 2개 성능 등급
- Google 계열 또는 AOSP 기준 단말
- 서로 다른 SoC·센서 vendor 단말
- ARCore 지원·미지원 단말
- 기압계 탑재·미탑재 단말
- 64-bit ABI와 Maven dependency 소비 build

### 10.2 iOS

- iOS 15.6을 실행하는 최소 지원 후보 단말
- 지원 범위의 중간·최신 iOS 버전
- AR 지원 비 LiDAR 단말
- LiDAR 탑재 단말
- device arm64 release build
- Apple Silicon simulator
- 지원하기로 결정한 경우 Intel simulator
- SPM clean checkout·checksum·archive build

### 10.3 공통 시나리오

1. 최초 설치와 정상 권한 허용
2. 권한 거부·영구거부·설정 복귀
3. Venue Package 없음·손상·버전 불일치
4. 초기 위치 확인 성공·실패·재시도
5. 정상 보행과 방향 전환
6. 계단·엘리베이터 층 이동
7. 경로 이탈과 재경로
8. 추적 품질 저하와 재획득
9. AR 미지원 시 2D 폴백
10. 네트워크 단절·지연·복구
11. background·foreground 반복
12. session 반복 생성·중지와 자원 해제
13. 30분 이상 배터리·발열·메모리 관찰
14. 저조도·역광·군중·가림 조건

## 11. 공식 지원 판정 기준 초안

각 단말·OS 조합은 다음 조건을 모두 충족해야 지원 목록에 포함한다.

- SDK 설치와 release build 성공
- 앱 시작·종료·재시작 시 crash 없음
- 필수 센서와 카메라 capability 정상 판정
- 권한 상태별 예상 오류와 폴백 동작
- 대표 venue에서 초기 위치 확인과 연속 추적 성공
- 메모리 누수나 지속적인 센서·카메라 점유 없음
- 합의된 배터리·발열 기준 충족
- 합의된 위치·층·재획득 acceptance 기준 충족
- 알려진 제한과 미지원 기능을 release notes에 기록

정량 합격값은 대표 단말, venue와 동선을 고정한 acceptance plan에서 별도로 확정한다.

## 12. 릴리스별 지원표 템플릿

공식 SDK release에는 다음 형태의 표를 함께 제공한다.

| SDK 버전 | 플랫폼 | OS 범위 | 검증 단말 | 지원 Tier | 제한사항 |
|---|---|---|---|---|---|
| 0.x | Android | TBD | TBD | TBD | PoC |
| 0.x | iOS | TBD | TBD | TBD | PoC |

목표 OS만 기재하고 검증 단말과 제한사항을 비워두는 방식은 피한다.

## 13. 알려진 호환성 위험

- 현재 Android 도구체인과 목표 호스트 Kotlin·AGP·compileSdk 버전이 다르다.
- 현재 iOS deployment target이 목표 iOS 15.6보다 높다.
- XCFramework/SPM과 전체 simulator architecture가 준비되지 않았다.
- 현재 Xcode 버전은 사용 중인 Kotlin Gradle Plugin의 공식 확인 범위보다 높다는 경고가 발생한다.
- 단말별 IMU·자력계·기압계 품질 차이에 대한 보정 기준이 확정되지 않았다.
- 모델 파일의 제품 패키징, checksum, 라이선스 및 업데이트 정책이 미확정이다.
- local AAR 크기는 모델·추론 runtime·Venue Package를 포함한 실제 앱 증가분을 의미하지 않는다.
- AR·카메라·추론 동시 실행 시 저사양 단말 성능 자료가 없다.

## 14. 결정 필요사항

| 항목 | 필요한 결정 |
|---|---|
| 최소 OS | Android API 24·iOS 15.6을 실제 제품 기준으로 확정할지 |
| Android 단말군 | OEM·SoC·OS별 필수 시험 조합 |
| iOS 단말군 | 최소 하드웨어와 simulator architecture 범위 |
| AR Tier | ARCore·ARKit 지원 판정과 목표 FPS |
| 성능 기준 | 초기 위치 확인 시간, 위치·층 정확도, 배터리·발열 |
| 폴백 책임 | SDK 상태 제공과 호스트 UI 구현 범위 |
| 지원 정책 | release별 지원 기간과 제외 단말 공지 방식 |
