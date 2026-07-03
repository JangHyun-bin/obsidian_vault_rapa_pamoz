---
type: evidence
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
date: 2026-05-29
tags: [positioning, evidence, sota, citation, benchmark]
related:
  - "[[0009-positioning-ondevice-magnetic-neural-fusion]]"
  - "[[0010-compute-placement-ondevice-first-server-accelerator]]"
  - "[[cold-start-global-localization]]"
  - "[[indoor-positioning]]"
---

# 측위 SOTA 근거 — 정량 evidence digest

> 코퍼스 ADR/스펙이 인용할 **외부 연구 근거·정량 수치**. 코퍼스엔 결정만 있고 문헌 evidence가 없어 이 노트로 보완. 전체 근거 볼트(수백 노트, citation 포함)는 파모즈 deep-research 레포에 보관 — 본 노트는 의사결정에 쓰인 핵심 수치만 증류.
>
> **근거 아카이브(전체):** GitHub `JangHyun-bin/hyperresearch_rapa_positioning` — `research/notes/final_report_iphone-indoor-positioning-*.md`, `research/notes/final_report_cold-start-global-localization-*.md` 및 원천 노트.

## 1. 로봇 천장 vs 폰 현실 (category error 분리)

| 시스템 | 정확도 | 수렴 | 플랫폼 — caveat |
|---|---|---|---|
| IDF-MFL (NTU 2024) | ATE 0.085m (4환경) | 10ms/step | Husky 로봇 + 7-자력계 array + LiDAR(FAST-LIO2). 지도도 LiDAR SLAM |
| MagHT (CEA 2023) | 0.16m 복도/0.21m atrium, recall 89%/97% | 12m, 4.6ms | 헬멧 4카메라 VIO(12m당 0.09m 표류) |
| magnetic-assisted-init (2019) | 88% 초기화 | 6.6s | LiDAR(Cartographer) 의존 |

→ **전부 LiDAR/VIO 오도메트리. 폰 PDR은 5–10배 열화(RoNIN ~3.7%/거리). 폰 약속으로 쓰면 안 됨.**

## 2. 폰 실측 (전부 tracking, 초기위치 주어짐)

| 시스템 | 정확도 | 비고 |
|---|---|---|
| Kuang 2018 (Pixel2/P10) | 0.64m 복도 / 1.87m 로비 / 2.34m 몰 | 매칭율 94.69%→88.01%; cold-start는 "타 방법 의존" 명시 |
| Kuang 2022 | ±0.83m office | tracking |
| MSTL (Zhang 2021) | 0.75–1.04m | 폰 자기장 tracking |
| LiMag (Wang 2018) | 개방 2.99m / fusion 1.55m | 개방공간 자기-only 한계 |
| Rose 2026 MagPie | 0.2–2m MAE | 폰 핸드헬드 CNN **회귀 cold-start**(시작점 불필요) — 단일-shot, per-building 학습, 시퀀스 수렴 실험 아님 |

→ **정직한 폰 3단계**: cold-start 1.5–2.5m(복도)/3–5m(개방), 20–30m 보행; warm 0.64–1.0m; 수렴 후 <1m.

## 3. Cold-start 실패율 · 신경관성 drift

- NILoc deep-cold SR@2m: **44.8%(최악 건물 A)** / 73.1%(B) / 80.5%(C) — IMU-only, 폰서 측정된 유일 cold-start 벤치마크. 44.8%는 보수 하한.
- RoNIN raw: 50–100m/분 발산; best RTE 2.67m/분(≈3.7%). 자이로 heading 비관측.

## 4. 단일 passive 앵커 효과 (폰 실측)

- Tian 2015 HILN(iPhone 5s): PDR-only 1062m서 22.08m(2.04% TTD) → 4 SRP/NFC reset 1.84m(0.17%) → +PF 1.36m(0.13%). **앵커 reset이 지배 이득, map-matching은 marginal.**
- Gu 2016: 단일 앵커 재방문 1회 → heading −86%(0.14→0.02rad), 위치 −48%(2.56→1.34m). **재방문 0회 = 개선 0**(cold-start가 바로 이 상태).
- 밀도 아닌 **리셋 횟수**가 결정: 4 SRP(2550m²) ≈ 71 RFID(2400m²). cold-start엔 입구 1개가 한계효용 정점.
- NFC vs QR: QR 0.64m/35m이나 **카메라 필요 → 제외**. NFC passive·무전원·~$0.20·RSSI 모호성 0.

## 5. 층 판정

- barometer: 기기간 절대압 1.2hPa(≈4층) 차이 → 절대 층 불가; 층-변화 검출 99.5%.
- 자기장 층 분류(폰 입증): Ashraf 2019 단독 87–89%(S8 89.24%) — barometer 86.4%·WiFi 78.1% 능가. per-floor fingerprint 분류(연속 3D 보간 아님).
- GPS 입구 감지 >93%(지상 단일입구); De Cock Viterbi 99.1%(층당 WiFi AP 2개, Android).

## 6. SW 수렴 기법 핵심

- Cluster-MCL: 대칭 환경 표준 MCL 0% → Cluster-MCL 100%.
- KLD-sampling: 고정 50k = 평균 ~3k(16.7배), 오차 44cm(KLD) vs 79/114.
- 순수 자기장 PF는 폰서 비현실(6400입자 12m = 46초). → 학습형 place-recognition(MagHT류)이 seed.
- NILoc 배제: 건물별 53시간/3–4 GPU-day 학습 + 전이 미입증, TCN 제거 시 44.8%→3.6%.

## 7. 플랫폼·연산

- iOS NEHotspotNetwork = 연결 SSID만 → multi-AP WiFi 가속 전부 불가(K-means cluster 51%↓ 등 Android 전용).
- 입자 compute(A17급): 10k≈100–500Hz / 50k 2–3Hz / 100k≈1Hz. PF는 CPU-bound, 신경관성은 NPU/GPU(Core ML/NNAPI).
