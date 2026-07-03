---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
implements: ["[[0009-positioning-ondevice-magnetic-neural-fusion]]"]
version: v1
tags: [positioning, cold-start, global-localization, ondevice, nfc]
related:
  - "[[0009-positioning-ondevice-magnetic-neural-fusion]]"
  - "[[0010-compute-placement-ondevice-first-server-accelerator]]"
  - "[[indoor-positioning]]"
  - "[[positioning-sota-evidence]]"
  - "[[device-support-matrix]]"
---

# Cold Start / Global Localization — 살아있는 스펙

> 사용자가 venue 임의 지점에서 앱을 **처음 켠 순간** 절대 위치를 어떻게 획득하는가(robotics의 wake-up / kidnapped-robot 문제). 코퍼스 `indoor-positioning` 스펙이 다루지 않던 영역. 근거 수치는 [[positioning-sota-evidence]], 결정은 [[0009-positioning-ondevice-magnetic-neural-fusion]].

## 0. 핵심 결론

순수 SW(자기장+신경관성+EKF/PF)는 **흔한 cold-start**(입구 진입·warm-start·feature-rich venue)는 처리하지만, **deep-cold·구조적 대칭 venue·즉시-fix·iOS 전반**에서는 부족 → **입구 단일 passive NFC 1개**가 그 실패 꼬리를 O(1)에 제거. "SW를 최대한 밀되, 정보이론이 막는 곳에만 태그를 박는다."

## 1. 정직한 성능 약속 (3단계)

| 상태 | 조건 | 복도/단순 | 개방/대형 | 수렴 비용 |
|---|---|---|---|---|
| Cold-start | 외부 fix 없음 | 1.5–2.5m | 3–5m(비수렴 위험) | 폰 20–30m 보행 |
| Warm-start | NFC/GPS/last-known seed | 0.64–1.0m | 1.5–2.5m | 7–12m |
| 수렴 후 | EKF/PF 수렴 | <1m | 1–2.5m | 지속 |

⚠️ 인용 SOTA(IDF-MFL 0.085m, MagHT 0.16m/12m)는 **LiDAR/VIO 로봇 천장**이지 폰 약속 아님. **폰 PDR cold-start 수렴거리 직접 측정 = 문헌 0건** → 20–30m는 v0 측정 대상(medium-confidence). 근거 [[positioning-sota-evidence]].

## 2. Cold-Start Cascade (우선순위, 첫 성공에서 정지)

| Step | 트리거/조건 | seed | 비고 |
|---|---|---|---|
| 0. NFC 입구 태그 | 태그 read | 1m σ, 300–500 입자 | 위치+yaw+층 즉시 fix. *최고 ROI* |
| 1. Last-known | age<120s AND acc<30m | σ15m, 2–5k 입자 | iOS significant-updates 등록 필수 |
| 2. GPS 입구 handoff | sumCNR25>200 AND hAcc<15m | σ8m, 5k 입자 | 흔한 경우 주력. 입구 seed ~30m |
| 3. WiFi cluster [Android only] | 기존 AP 존재 | σ8m, 8–10k 입자 | iOS 봉쇄로 skip |
| 4. Barometer 층 prior | 층 판정 가능 | 검색공간 1/N층 | 절대 층은 GPS-입구/NFC/자기장분류기 |
| 5. True cold start | 위 전부 실패 | 균등 prior, Cluster-MCL K=4–6 + escape 1, A16+ 2–3만 / 미드 Android 1–1.5만 | 학습형 place-recognition이 첫 ~12m로 seed → KLD-sampling |

**Mode-switch (global→local)**: 지배 cluster weight >80% **AND** 7–12m 보행(폰 현실 20–30m). 공분산 trace<5m²는 결과지 독립 gate 아님. (임계값은 엔지니어링 구성치 — v0 보정)

## 3. Perceptual Aliasing — 앵커 필요성의 수학적 근거

- 대칭/반복 layout(동일 복도·주차장 기둥 그리드·atrium)은 전 modality 공통 지배적 실패 모드.
- **영구 비수렴 경계: 공간 자기상관 길이 ≥ 구별특징 간격** → 관측 시퀀스가 주기 L로 반복, 보행 무한대로도 해소 불가. 필터 실패가 아니라 정보이론적 불가능.
- 해법 위계: 궤적문맥(대칭 입구서 실패) < multi-hypothesis PF(구별특징 있어야) < **단일 물리 앵커(O(1))**. 카메라도 탈출구 아님(VPR R@1 34–36%).
- → Cluster-MCL은 해소 가능한 다수를, NFC 앵커는 해소 불가능한 주기적 소수를 처리(상보).

## 4. 절대 층(f0) 판정

우선순위: **GPS-입구(>93%, 지상 단일입구) ≈ NFC(층 carry 100%) > 자기장 층 분류기(폰 입증 87–89%) > barometer(상대 추적만)**. barometer 단독 절대 층 불가(기기간 1.2hPa 차이), 층-변화 검출은 99.5%. 맵 = 층별 2D GP + 층 분류용 per-floor 서명 + 전이구역 3D seam.

## 5. 플랫폼 분기

- **iOS**: multi-AP Wi-Fi 봉쇄(NEHotspotNetwork=연결 SSID만) → cold-start 비-보행 경로가 NFC뿐 → **NFC 강권장**.
- **Android**: 기존 AP 있으면 WiFi cluster로 부분 대체 → NFC 선택.

## 6. 검증 — v0에서 측정 (→ [[v0-acceptance-gate]])

폰 PDR 수렴거리 직접 측정 / 강철건물 자기장 ℓ_SE(z) / iPhone thermal·입자예산 / 대칭 venue 비수렴 재현. cold-start gate: 60초 내 median 2D <3m, NFC seed 시 즉시 <2m.
