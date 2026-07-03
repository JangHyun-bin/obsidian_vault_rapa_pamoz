---
id: "0003"
type: decision
status: superseded
date: 2026-05-14
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: "[[0009-positioning-ondevice-magnetic-neural-fusion]]"
related_specs: ["[[r-and-r]]"]
related_meetings: ["[[2026-05-14-개발협의-아젠다-v2]]"]
tags: [positioning, ios, android, algorithm]
---

# 0003 — 측위 알고리즘 = 지자기·BLE·QR·PDR 융합 (iOS는 BLE+IMU+QR 중심)

## 컨텍스트

실내 측위 알고리즘의 입력 채널을 결정해야 했음. iOS의 WiFi 스캔 제약(NEHotspotHelper API entitlement 사실상 의료 앱 승인 불가)으로 OS 간 입력 채널이 달라야 함.

## 옵션

- A. **WiFi 핑거프린팅 위주** — 정확도 ↑, iOS 불가
- B. **BLE 비콘 + IMU + QR 앵커 위주** — OS 무관, 비콘 배치 밀도 필요
- C. **지자기 + BLE + QR + PDR 융합** — 다중 입력으로 robust, 알고리즘 복잡도 ↑

OS별 분기:
- Android: A/C 가능
- iOS: B/C만 가능

## 결정

**C. 융합 알고리즘 채택 (Res-Transformer-LSTM 기반)**:

| 입력 채널 | Android | iOS |
|---|---|---|
| **지자기 (Magnetic)** | ✓ | ✓ |
| **BLE 5.1 비콘 (RSSI/AoA)** | ✓ | ✓ |
| **QR 앵커** | ✓ | ✓ |
| **PDR (가속도·자이로)** | ✓ | ✓ |
| **WiFi RTT/RSSI** | ✓ (12+) | ✗ (entitlement 불가) |

**iOS 측위 정확도는 구조적으로 Android 대비 낮을 수 있음 → 비콘 배치 밀도를 iOS 기준으로 산정**.

DL 측위 모델의 입력 차원이 OS별 상이 → 모델 가중치 별도, 모델 아키텍처는 공유.

## 근거

- iOS WiFi 스캔 제약은 사업 전체 KPI에 영향 — 컨소시엄 차원의 공식 인지 필요 (아젠다 v2 C-1 권장 사항)
- 지자기·BLE·QR·PDR 4채널 융합으로 단일 채널 누락 시에도 동작 (EKF/Particle Filter, IMU dead reckoning, QR 앵커 보정)
- KPI: 1차년도 ±2.5m, 2차년도 ±1.5m (공인)

## 결과

- 긍정: OS 양쪽 지원, robustness ↑
- 부정/리스크: iOS 정확도 KPI 별도 기준 수립 필요, BLE 비콘 50~100개소 + AoA 10~20개소 설치 부담 (파모즈 현장 인프라 구축 작업)
- 영향받는 스펙: [[r-and-r]] (현장 인프라 작업 표)

## 변경 이력

- 2026-05-14: 아젠다 v2 C-1에서 iOS 제약 + B/C 옵션 검토
- 2026-05-14: 본 ADR — 융합 알고리즘 채택, OS별 입력 채널 명시
