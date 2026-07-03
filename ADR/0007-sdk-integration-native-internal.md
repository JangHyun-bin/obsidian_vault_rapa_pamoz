---
id: 0007
type: decision
status: proposed
date: 2026-05-26
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: null
related_specs: ["[[r-and-r]]"]
related_meetings: ["[[2026-05-14-개발협의-아젠다-v2]]"]
tags: [sdk, mobile, integration, ios, android]
---

# 0007 — SDK 통합 모델 = 내부 SDK (Native xcframework + aar)

## 컨텍스트

본 사업의 측위·AR 길안내 기능을 레몬케어 앱에 어떻게 통합할지 모델 결정. 아젠다 v2 C-2에서 4가지 옵션 검토 후 파모즈 권장안 도출. SDK 사전문의(Q1.1, ★★★)에서 레몬케어 측 공식 답변 대기 중.

## 옵션

| 옵션 | 설명 | 적합도 |
|---|---|---|
| A. **내부 SDK** | 레몬케어 앱 빌드 시 dependency 포함. 단일 앱 바이너리 | ★ 권장 |
| B. **별도 앱** | "스마트 병원 동행" 별도 앱, deeplink 호출 | 비권장 |
| C. **WebView** | 레몬케어 앱 내 WebView | 불가 (BLE·AR 제약) |
| D. **Mini App** | 슈퍼앱 mini app | 레몬 인프라 미정 |

## 결정 (proposed)

**A. 내부 SDK**:

- **앱 owner — 레몬헬스케어** (메인 앱 코드베이스, 인증/결제/푸시 인프라)
- **SDK provider — 파모즈** (측위·AI 챗봇 SDK 및 백엔드)
- **통합 방식** — `.xcframework`(iOS) + `.aar`(Android) 형태로 SDK 제공, 레몬헬스케어가 자사 앱에 의존성 추가

OS별 네이티브 SDK 별도 개발:
- 센서 수집(BLE/IMU/WiFi/카메라), 권한 요청, 백그라운드 동작, 온디바이스 추론(Core ML/TFLite), 챗봇 UI(SwiftUI/Jetpack Compose) — OS별 분리 필수
- 공유 가능: 백엔드 API 스펙(OpenAPI 단일), 모델 아키텍처, 학습 파이프라인, 데이터 스키마

빌드·사이닝:
- iOS: Apple Developer Program 계정은 레몬케어 보유 그대로 사용. 파모즈는 사이닝 미관여
- iOS: Privacy Manifest(iOS 17+) 필수, 권한 키 명세 사전 전달
- Android: AAR 배포, AndroidManifest 권한 + ProGuard rules 명세서 사전 전달

배포 채널: 사내 Maven 저장소 또는 GitHub Packages. Semantic Versioning 엄격 적용.

## 근거

- 1,300만 가입자(레몬케어 앱)가 추가 설치 없이 즉시 사용 가능 → 사용자 마찰 최소
- 네이티브 기능 자유 (BLE 5.1 AoA, ARKit/ARCore, UWB Nearby Interaction)
- 환자 인증 자연스러움 (레몬케어 SSO 활용)
- WebView/Flutter는 BLE·AR 제약 또는 빌드 방식 차이로 비권장 (Q1.2 호스트 앱 기술 스택 확인 대기)
- iOS·Android는 센서 접근 API·권한 모델·백그라운드 동작 정책이 근본적으로 달라 OS별 네이티브 SDK 분리 필수 (아젠다 v2 C-3)

## 결과

- 긍정: 사용자 마찰 0, 네이티브 기능 최대 활용
- 부정/리스크:
  - 의존성 충돌 가능성 (Q4.1 — 레몬 앱이 현재 사용 중인 라이브러리 dependency 리스트 공유 필요)
  - SDK 사이즈 증가 (측위 ~3-8MB + AR ~5-15MB + 3D ~10-30MB 추정)
  - 레몬 앱 안정성에 영향 가능 → 사전 검증 필수
- 영향받는 스펙: [[r-and-r]]
- 미해결: SDK 사전문의 40개 답변 (특히 Q1.1, Q1.2, Q4.1, Q5.1)

## 변경 이력

- 2026-05-14: 아젠다 v2 C-2 SDK 통합 모델 비교 + 파모즈 권장안
- 2026-05-26: SDK 사전문의 v1.0 발송 (Q1.1 ★★★) — 본 ADR (proposed)
- accepted 전환 조건: 레몬케어 측 Q1.1, Q1.2 공식 답변 + 호스트 앱 기술 스택 확인
