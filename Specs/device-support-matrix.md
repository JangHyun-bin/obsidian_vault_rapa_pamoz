---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
implements: ["[[0009-positioning-ondevice-magnetic-neural-fusion]]", "[[0010-compute-placement-ondevice-first-server-accelerator]]"]
version: v1
tags: [positioning, device-support, ios, android, ondevice]
related:
  - "[[indoor-positioning]]"
---

# 디바이스 지원 매트릭스 — 온디바이스 측위

> [[0009-positioning-ondevice-magnetic-neural-fusion]](알고리즘) + [[0010-compute-placement-ondevice-first-server-accelerator]](연산 배치)의 단말 적용 범위. **정확한 최소 지원 OS 컷오프는 호스트 앱 측 결정(SDK 사전문의 Q1.3) 대기 중** — 결정 오면 §3 컷오프 행만 끼우면 된다.

## 0. 두 부하를 분리해서 본다 (핵심 원리)

온디바이스 측위는 성격이 다른 두 연산으로 갈리고, 구형폰 가능성은 이 둘이 다르다:

| 부하 | 연산 위치 | 비용 결정 요인 | 구형폰 |
|---|---|---|---|
| **정상 추적** (시간의 99%) | 신경관성=NPU/GPU, PF/EKF=CPU | 수백 입자 + 작은 모델 | ✅ 광범위 가능 |
| **cold-start 글로벌 스윕** (1회성) | CPU(입자) 또는 서버 오프로드 | 수만 입자 / 대형 모델 | ⚠️ 하한을 정함 |

→ **구형폰이 버거운 건 cold-start 스윕뿐**이고, 그건 (a) NFC·GPS handoff로 우회하거나 (b) 서버로 오프로드하면 해소된다([[0010-compute-placement-ondevice-first-server-accelerator]]). 정상추적 자체는 가볍다.

## 1. 센서·연산 의존성 (지원 가능 여부를 가르는 하드웨어)

| 하드웨어 | 역할 | 없을 때 영향 | 가용 경계 |
|---|---|---|---|
| 자력계 (magnetometer) | 측위 코어(필수) | 측위 불가 | 모든 스마트폰 보유. 단 **품질 편차 큼**(0.04µT ~ 비정상 80–110µT) → 싸구려·구형은 noise floor↑ → 저변동 venue 비수렴 위험. **일회성 하드웨어 보정(왜곡행렬+오프셋) 필수** |
| IMU (가속도·자이로) | 신경관성/PDR(필수) | 측위 불가 | 모든 스마트폰 보유 |
| 기압계 (barometer) | 층 검출/추적 | 절대 층 판정에 GPS-입구·NFC 의존 | iPhone 6+ 보유; CMAbsoluteAltitude는 iPhone 12+. 일부 저가 Android·아주 구형폰 없음 |
| NPU (Neural Engine 등) | 신경관성 추론 가속 | GPU/CPU fallback(작동하나 느림·배터리↑) | iPhone A11(2017, iPhone 8/X)+; Android는 파편화 — 다수 저가/구형 없음 |
| NFC | cold-start 입구 앵커 | cold-start 즉시성 저하(보행 수렴) | iPhone 7+ (background read iPhone XS+); Android 대부분 보유 |
| GPS/GNSS | 입구 handoff seed | cold-start seed 약화 | 모든 스마트폰 보유 |

## 2. 단말군별 지원 매트릭스

| 단말군 | 칩/NPU | 자력계·기압계 | 정상추적 | cold-start (온디바이스) | cold-start (서버·NFC 보완) | 층 검출 | 권장 |
|---|---|---|---|---|---|---|---|
| **최신 iPhone** (12+/A14+) | ANE 강력 | 양호·기압계+절대고도 | ✅ 0.64–1.0m | ✅ 2–3만 입자 | — | ✅ 자기장+기압+NFC | 온디바이스 full |
| **중급 iPhone** (XS–11 / A11–A13) | ANE 보유 | 양호·기압계 | ✅ | △ 1.5–2만(발열 보수) | 서버/NFC로 가속 | ✅ (절대고도 X, 상대+GPS-입구) | 온디바이스 + NFC 권장 |
| **구형 iPhone** (<X, A10 이하) | ANE 없음(GPU/CPU) | 자력계 양호·기압계(6+) | ✅(추론 CPU fallback) | ❌ 어려움 | **서버 오프로드 / NFC 의존** | ✅ | NFC + 서버 가속 |
| **플래그십 Android** | NPU 보유 | 보통 양호·기압계 多 | ✅ | ✅ 1.5–2만 | — | ✅ (+기존 AP 시 WiFi cluster) | 온디바이스 full |
| **미드레인지 Android** | NPU 유무 혼재 | 편차·기압계 혼재 | ✅(자력계 양호 시) | △ 1–1.5만(발열 보수) | 서버/NFC | △ (기압계 없으면 GPS-입구/NFC) | NFC 권장 + 보정 필수 |
| **저가/구형 Android** | NPU 없음 多 | 자력계 편차 큼·기압계 없음 多 | △ (보정·자력계 품질 의존) | ❌ 온디바이스 곤란 | **서버 오프로드 / NFC 의존** | ❌ 기압계 없음 → NFC/GPS-입구 필수 | NFC + 서버 가속 + 하드웨어 보정 |

범례: ✅ 부담 없이 가능 / △ 조건부(파라미터 축소·보정·보완 필요) / ❌ 단독으로는 곤란(보완 필수)

## 3. 최소 지원 OS 컷오프 (결정 대기 — 오면 여기 채움)

| 항목 | 결정값 | 영향 |
|---|---|---|
| iOS 최소 버전 | _(미정 — Q1.3)_ | iOS 15+ : Nearby Interaction 등 가용 / iOS 14 미만 : 일부 제약 |
| Android 최소 API | _(미정 — Q1.3)_ | 예: API 26(8.0). NNAPI 가용성·권한 모델 영향 |
| 기압계 없는 기기 지원? | _(정책 미정)_ | 미지원 시 단순화 / 지원 시 NFC·GPS-입구로 층 판정 |
| NPU 없는 기기 지원? | _(정책 미정)_ | 미지원 시 단순화 / 지원 시 CPU fallback(느림·배터리↑) 허용 |

## 4. 함의 — 구형폰 전략 = NFC + 서버 가속

- 구형·저가 단말의 한계는 cold-start 스윕(연산)과 센서(기압계·자력계 품질)에서 온다.
- 두 가지로 거의 다 해소된다: **입구 NFC 1개**(비싼 균등-prior 스윕을 건너뛰고 위치+yaw+층 즉시 fix) + **서버 cold-start 가속**(스윕·대형모델 오프로드).
- 정상추적은 구형폰에서도 가볍게 돌므로, "어디까지 지원하나"의 실질 컷오프는 **자력계 품질 + 기압계 유무 + (cold-start를 NFC/서버로 보완할 수 있는가)** 로 환원된다.

## 5. v0 spike에서 확정할 값

- iPhone(세대별) thermal throttle 온셋 → 온디바이스 입자 예산 상한.
- 대표 저가 Android 자력계 noise floor 실측 → 보정 후 측위 가능 하한.
- 기압계 없는 대표 기기에서 NFC/GPS-입구만으로 층 판정 신뢰도.
