---
id: "0009"
type: decision
status: proposed
date: 2026-05-29
deciders: ["[[FAMOZ]]"]
supersedes: "[[0003-positioning-fusion-algorithm]]"
superseded_by: null
related_specs: ["[[indoor-positioning]]", "[[cold-start-global-localization]]", "[[device-support-matrix]]", "[[v0-acceptance-gate]]"]
related_meetings: []
tags: [positioning, ios, android, algorithm, ondevice, nfc]
---

# 0009 — 측위 알고리즘 갱신 = 자기장+신경관성+EKF/PF 온디바이스 코어 (BLE/QR 선택화, 단일 입구 NFC 앵커)

## 컨텍스트

[[0003-positioning-fusion-algorithm]]은 지자기+BLE 5.1 비콘+QR+PDR 4채널 융합(Res-Transformer-LSTM)을 채택하고 BLE 비콘 50~100개소·AoA 10~20개소 설치를 전제했다. 이후 파모즈 측 deep-research 2건이 그 전제를 재검토하게 했다:

- **본편(iPhone/cross-platform camera-free 측위)** — 자기장 fingerprint(GP) + 신경관성(EqNIO/RoNIN-class) + EKF/Particle Filter만으로 정상추적 복도 sub-meter 달성 가능. 외부 센서(BLE 비콘·Wi-Fi FTM·UWB)는 cross-platform 비대칭(iOS Wi-Fi 봉쇄, UWB 기기 의존)과 venue가 한 플랫폼만 위해 하드웨어를 설치하지 않는 현실상 신규 설치가 비효율.
- **cold-start / global localization** — "켜자마자"의 절대 위치는 자기장 sequence라 보행이 필요하고, 구조적 대칭 venue는 정보이론적으로 영구 비수렴. 단일 passive 입구 NFC 1개가 이 실패 꼬리를 거의 무료로($0.20, 무전원, 카메라 불필요) 제거.

즉 0003의 BLE/QR 핵심 가정과 외부 인프라 부담을 갱신할 근거가 생겼다. 카메라 런타임 미사용 제약상 QR은 런타임 측위에 쓸 수 없다(0003의 QR 앵커 항목과 충돌).

## 옵션

- A. **0003 유지** — 자기장+BLE+QR+PDR, BLE 비콘 신규 설치. iOS도 BLE로 정확도 보강.
- B. **자기장+신경관성 온디바이스 코어, BLE/QR 완전 제거** — 인프라 0, 그러나 저변동 venue·cold-start 보완책 없음.
- C. **자기장+신경관성 코어 + BLE/QR 선택화 + 단일 입구 NFC** — 코어는 인프라 없는 SW, 외부 센서는 venue 보유 시에만 opportunistic, cold-start 꼬리는 NFC 1개로 방어.

## 결정 (proposed)

**C. 자기장+신경관성 온디바이스 코어 + BLE/QR 선택화 + 단일 입구 NFC 앵커**:

| 요소 | 1차년도 기본 | 비고 |
|---|---|---|
| 지자기 fingerprint (GP map) | ✓ 코어 | 층별 2D GP + 층 분류 per-floor 서명 + 전이구역 3D seam |
| 신경관성 (EqNIO/RoNIN-class) | ✓ 코어 | 상대 변위; NPU/GPU 추론 |
| EKF / Particle Filter 융합 | ✓ 코어 | 절대(자기장)×상대(관성) 결합 |
| 카메라 (런타임 측위) | ✗ | 미사용 유지 (AR 표시 오버레이는 별개) |
| BLE 5.1 비콘 | △ 선택 | **1차 신규 설치 안 함.** 기존 보유 venue에서만 opportunistic 보강 |
| QR 앵커 | ✗ 런타임 | 카메라 제약 → 비교/디버그용만 |
| 단일 입구 NFC | ✓ narrow exception | cold-start(deep-cold·대칭·다입구/지하·iOS)에서 위치+yaw+층 동시 fix |

**Cold-start cascade (첫 성공에서 정지)**: NFC(있으면 즉시 1–2m) > last-known(<120s) > GPS 입구 handoff(~30m+층) > [Android only] WiFi cluster > barometer 층 prior > 학습형 place-recognition seed → Cluster-MCL + KLD-sampling 수렴.

**OS 분기**: iOS는 multi-AP Wi-Fi 봉쇄로 cold-start 비-보행 경로가 NFC뿐 → **입구 NFC 강권장(사실상 필수)**. Android는 기존 AP 있으면 WiFi cluster로 부분 대체 → NFC 선택.

## 근거

- 정상추적은 sensor/map-bound이며 폰으로 복도 0.64–1.0m 달성(본편). 외부 비콘 없이 1차 KPI(±2.5m)에 여유.
- 정직한 폰 숫자 3단계: cold-start 1.5–2.5m(복도, 20–30m 보행)/3–5m(개방), warm-start 0.64–1.0m, 수렴 후 <1m. **인용되는 SOTA(IDF-MFL 0.085m, MagHT 0.16m/12m)는 LiDAR/VIO 로봇 천장이지 폰 약속 아님.**
- 구조적 대칭 venue 영구 비수렴은 알고리즘으로 못 풀고 **단일 물리 앵커가 유일한 O(1) 해법** → NFC 1개.
- BLE 비콘 50~100개 설치·유지보수 부담 회피(전남대병원 비콘 폐기 이력 참조). NFC는 passive·무전원·약 500원/개.
- 카메라 미사용 제약(0003 컨텍스트의 의료 앱 제약과 동일 선상)상 QR 런타임 측위 불가.

## 결과

- 긍정: 외부 인프라 최소·OS 무관·유지비↓·NFC 단가 미미. iOS/Android 단일 코어.
- 부정/리스크:
  - "켜자마자 즉시" 정확도는 NFC/GPS/last-known 외부 fix 의존 — 없으면 20–30m 보행.
  - **폰 PDR cold-start 수렴거리는 직접 측정 0건** → v0 spike 1순위 측정(20–30m 추정 검증).
  - BLE 제거로 저변동·개방 venue 비수렴 위험 → 해당 venue는 NFC 또는 (보유 시) BLE 보강.
  - KPI: 1차 ±2.5m / 2차 ±1.5m 유지 — iOS 정확도 별도 기준은 0003 대비 완화(BLE 의존 제거).
- 영향받는 스펙: [[0003-positioning-fusion-algorithm]] (supersede), [[r-and-r]] (현장 인프라 — BLE 설치작업 대폭 축소, NFC 입구 태그 부착으로 대체), [[0010-compute-placement-ondevice-first-server-accelerator]] (연산 배치 연동).
- 미해결: 호스트 앱 기술 스택 확정([[0007-sdk-integration-native-internal]] Q1.2) 후 SDK 측위 모듈 구조 확정; 최소 지원 OS(Q1.3) → 디바이스 지원 매트릭스 컷오프; v0 spike 측정값 반영.

## 변경 이력

- 2026-05-29: deep-research 2건(camera-free 측위 본편 + cold-start/global-localization) 결론 반영 — 온디바이스 코어 + BLE/QR 선택화 + 단일 입구 NFC. [[0003-positioning-fusion-algorithm]] supersede 제안 (proposed).
- accepted 전환 조건: 컨소시엄 합의 + [[0010-compute-placement-ondevice-first-server-accelerator]] 동반 합의 + v0 spike 수렴거리 측정.
