---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
implements: ["[[0003-positioning-fusion-algorithm]]", "[[0004-backend-onpremise-hospital]]", "[[0009-positioning-ondevice-magnetic-neural-fusion]]", "[[0010-compute-placement-ondevice-first-server-accelerator]]"]
version: v2
tags: [positioning, indoor, ble, geomagnetic, ios, android]
---

# Camera-free iOS/Android 실내 측위 — 살아있는 스펙

본 스펙은 카메라를 사용하지 않는 cross-platform 실내 측위 엔진의 현재 합의 구조. v2 부터 [[0009-positioning-ondevice-magnetic-neural-fusion]] (알고리즘 갱신) · [[0010-compute-placement-ondevice-first-server-accelerator]] (연산 배치 갱신) 반영. 0003·0004 는 superseded 상태이며 본 스펙의 v1 구현 근거로만 참조.

*원본 아카이브: [[_raw/camera_free_indoor_localization_research_roadmap]] (full roadmap)*
*보조 자료: [[_raw/paper_matrix.ko]] (paper matrix 한국어)*

---

## 0. 최종 결론 (v2 — 2026-05-29 갱신)

```text
Camera-free, cross-platform, ON-DEVICE-first
  = Geomagnetic Fingerprint (GP)        [코어]
  + Neural-Inertial (EqNIO/RoNIN) + PDR [코어]
  + EKF / Floor-plan Particle Filter    [코어]
  + Barometer Floor Detection           [상대 층]
  + 단일 입구 NFC anchor (cold-start)    [narrow exception]
  (BLE/iBeacon = 선택, 기존 보유 venue만 opportunistic; QR = 런타임 제외)
```

**ARKit/ARCore, VPS, Visual SLAM, QR, AprilTag는 사용자 UX 기준에서 제외**. QR 은 카메라 미사용 제약상 런타임 측위에서 완전 제외(비교/디버그용만). 다만 운영자용 calibration / 내부 survey tool에서는 선택적으로 사용 가능. 근거 수치는 [[positioning-sota-evidence]].

> v1 (deprecated): `BLE/iBeacon + Geomagnetic + IMU/PDR + Barometer + Floor-plan PF`. BLE 비콘 50~100개 신규 설치 전제. [[0009-positioning-ondevice-magnetic-neural-fusion]] 로 갱신됨.

## 1. 제약조건 — 왜 이 조합인가

| 제약 | 기술적 의미 |
|---|---|
| iOS와 Android 모두 지원 | Android-only Wi-Fi RTT, 기기 의존 UWB를 메인으로 쓰면 안 됨 |
| 사용자가 카메라 안 씀 | VPS, Visual SLAM, QR, AprilTag, AR 기반 측위 제외 |
| 병원/전시/문화공간 | 복잡 평면도, 다층, 사람 밀집, 금속 구조물, 장비 배치 변화 고려 |
| 설치비 제약 | Dense UWB anchor, 고가 locator 인프라는 방문객용으로 부적합 |
| 제품화 가능 | BLE 단독·geomagnetic 단독·PDR 단독은 위험 |
| 연구성 | sensor fusion, floor-plan constraint, continual calibration, magnetic fingerprinting 강세 |

## 2. 아키텍처 (6 컴포넌트 + Sensor Fusion)

```text
1. IMU/PDR
   - accelerometer, gyroscope, step detection, stride estimation, heading

2. Geomagnetic Fingerprint
   - magnetometer x/y/z, magnetic norm |B|, magnetic gradient, sequence matching

3. BLE/iBeacon
   - zone detection, proximity likelihood, coarse correction, beacon placement opt.

4. Barometer
   - floor change detection, elevator/stair transition hint

5. Floor Plan Constraint
   - walkable graph, wall constraint, corridor snapping, node/edge map matching

6. Sensor Fusion
   - Particle Filter (1st), EKF/UKF (2nd), Factor Graph (later)
```

옵션 reset 채널 (non-camera): NFC / kiosk / BLE anchor / manual confirmation.

### v2 추가 (2026-05-29)

- **연산 배치**: 정상추적 EKF/PF 는 **온디바이스**, 서버는 지도빌드·cold-start 가속·drift 감지의 *accelerator* (graceful degradation — 서버 없어도 폰 단독 가능). → [[0010-compute-placement-ondevice-first-server-accelerator]]
- **Cold-Start Cascade** (신규 컴포넌트): NFC > last-known > GPS 입구 handoff > [Android only] WiFi cluster > barometer 층 prior > 학습형 place-recognition seed → Cluster-MCL + KLD-sampling. 첫 성공에서 정지. → [[cold-start-global-localization]]
- **단일 입구 NFC 앵커**: 정보이론적 비수렴(대칭 venue·cold-start) 해결용. iOS 사실상 필수, Android 권장.
- **신경관성 (EqNIO/RoNIN-class)**: PDR 갱신 — 절대(자기장) × 상대(관성)의 상대 변위 추정. NPU/GPU 추론.

상세 분리 스펙:
- 정량 성능·SOTA 근거 → [[positioning-sota-evidence]]
- Cold-start 절차·aliasing·층 판정 → [[cold-start-global-localization]]
- 단말군별 지원 매트릭스 → [[device-support-matrix]]
- v0 spike·acceptance gate → [[v0-acceptance-gate]]

## 3. 제품 정의

> 사용자 카메라 없이, 스마트폰 내장 센서와 BLE/지자기/floor-map prior를 결합해 실내 위치를 추정하는 cross-platform indoor positioning engine.

## 4. 핵심 키워드 분야

연구 방향 (paper_matrix 참고):
- Indoor Positioning / Indoor Localization
- Sensor Fusion
- Geomagnetic Fingerprinting
- Particle Filter on Floor-plan Graph
- BLE Proximity Models
- PDR Calibration
- Cross-platform Mobile Sensor Standardization

## 5. KPI 매핑

| 차수 | 정확도 KPI | 비고 |
|---|---|---|
| 1차년도 | ±2.5m | iOS·Android 분리 측정 (iOS는 구조적으로 낮을 수 있음) |
| 2차년도 | ±1.5m (공인) | 비콘 밀도 + 알고리즘 개선 |

## 6. 현장 인프라 의존

본 스펙의 구현은 [[r-and-r]] 의 "현장 인프라 구축 작업" 5종 완수 가정:
1. LiDAR 스캔 (파일럿 3개 동선)
2. 지자기 핑거프린팅 DB 구축
3. QR 앵커 설치 50~100개소 (운영자용 보정)
4. BLE 5.1 AoA 설치 10~20개소
5. 측위 테스트 (30+ 포인트)

## 7. 미해결 / 후속

- (유지) iOS·Android 모델 분포 (UWB chip, BLE 5.1 지원) — [[domain/sdk-개발-사전문의]] Q8.5
- (v2 갱신) 모델 가중치 = **온디바이스 경량 모델 + (선택) 서버 대형 모델** 분담으로 재정의. OS별 별도 학습 여부는 경량 모델 한정 결정.
- (유지) Floor Plan 자동 추출 vs 수동 입력 (LiDAR 후처리 파이프라인)
- (v2 신규) **폰 PDR cold-start 수렴거리 = 직접 측정 0건** → [[v0-acceptance-gate]] 측정항목 2 (1순위).
- (v2 신규) BLE 제거에 따른 저변동 venue 비수렴 → NFC 보완 범위 venue 별 확정 필요.

## 변경 이력

- 2026-05-29 (v2): deep-research 2건(camera-free 측위 본편 + cold-start/global-localization) 반영 — 온디바이스 우선, BLE/QR 선택화, 단일 입구 NFC, Cold-Start Cascade 추가. [[0009-positioning-ondevice-magnetic-neural-fusion]]·[[0010-compute-placement-ondevice-first-server-accelerator]] 정합. 분리 스펙: [[cold-start-global-localization]], [[positioning-sota-evidence]], [[device-support-matrix]], [[v0-acceptance-gate]].
- 2026-05-14 (v1): 초기 합의 구조 — 5채널 융합 (BLE/iBeacon + Geomagnetic + IMU/PDR + Barometer + Floor-plan PF). [[0003-positioning-fusion-algorithm]] · [[0004-backend-onpremise-hospital]] 기준.
