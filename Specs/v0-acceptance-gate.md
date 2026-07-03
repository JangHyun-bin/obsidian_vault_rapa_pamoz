---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
implements: ["[[0009-positioning-ondevice-magnetic-neural-fusion]]", "[[0010-compute-placement-ondevice-first-server-accelerator]]"]
version: v1
tags: [positioning, v0, validation, acceptance-gate, spike]
related:
  - "[[cold-start-global-localization]]"
  - "[[device-support-matrix]]"
---

# v0 Feasibility Spike & Acceptance Gate — 측위

> 1차년도 7개월 압축 일정에서 v1 sprint 진입 전 **반드시 통과해야 할 검증**. 본편/cold-start deep-research가 medium-confidence로 남긴 값들을 직접 측정으로 확정한다. skip 금지.

## 0. 왜 필요한가

deep-research 결론 중 일부는 폰으로 직접 측정된 적 없는 추정치다(특히 cold-start 수렴거리 = 문헌 0건). v1 정확도 commitment를 데이터로 받치려면 4–6주 spike로 핵심 미지수를 먼저 닫아야 한다. confidence-propagation 경고: 측정 없이 v1 진입 시 KPI가 3m 이상으로 떨어질 ~30–50% 확률.

## 1. v0 spike 측정 항목 (4–6주)

| # | 측정 | 방법 | 통과 기준 |
|---|---|---|---|
| 1 | EqNIO/신경관성 @100Hz iPhone ATE | iPhone 12+ 보행 ~20분, ARKit-anchored/Vicon GT 비교 | ATE ≤ 3.0 m/분 (RoNIN-ResNet 기준점) |
| 2 | **폰 PDR cold-start 수렴거리** | VIO 아닌 폰 PDR로 자기장 global-loc 실행, 수렴거리·최종정확도 동시 측정 | 20–30m 추정 검증(문헌 0건 gap) |
| 3 | 강철건물 자기장 ℓ_SE(z) | 동일 (x,y) 다층 측정 | 인접 층 구별성·연속 보간 가능성 |
| 4 | iPhone thermal·입자예산 | 20–30k 입자 PF 60초 지속 | throttle 없음 → 온디바이스 budget 확정 |
| 5 | cross-device 자기 보정 | 대표 기기군 자력계 noise floor 실측 | 보정 후 측위 가능 하한 |
| 6 | GP 자기장 지도 builder + 측량 SOP | boustrophedon ≤1.5m row spacing 도구화 | 1000m² test venue 측량 완료 |
| 7 | NFC seed 수렴 | 입구 태그 후 belief collapse | 즉시 1–2m Gaussian 확인 |
| 8 | 대칭 venue 비수렴 재현 | 주기적 layout서 무앵커 실행 | 비수렴 경계 검증 + NFC 시 즉시 수렴 |

## 2. v0 Acceptance Gate (전부 통과해야 v1)

| 항목 | 게이트 기준 |
|---|---|
| Cold-start 수렴 시간 | 보행 60초 이내 median 2D 오차 < 3m |
| Local 추적 정확도 | 90th percentile < 5m, 수렴 후 median < 1m(복도) |
| GPS→실내 handover 지연 | < 4초 (80th percentile) |
| 절대 층 판정 | 자기장 분류기 단독 ≥ 87%, GPS-입구 시 ≥ 93% |
| NFC fix | tap 시 1–2m collapse, iOS 백그라운드 알림-탭 완료율 측정 |
| iPhone thermal | 20–30k 입자 PF 60초 지속 throttle 없음 |

## 3. 최우선 3건 (이게 hedge를 confidence로 바꾼다)

1. **폰 PDR cold-start 수렴거리**(측정항목 2) — 가장 attackable한 load-bearing 수치.
2. **자기장 ℓ_SE(z)**(3) — 층 분리도가 venue별로 흔들릴 수 있음.
3. **iPhone thermal 온셋**(4) — 온디바이스 입자 예산 상한 결정([[0010-compute-placement-ondevice-first-server-accelerator]] 분담 경계).

결과에 따라 medium→high 상향하거나, NFC/서버 의존도를 높이는 방향으로 [[0009-positioning-ondevice-magnetic-neural-fusion]]·[[0010-compute-placement-ondevice-first-server-accelerator]]를 조정.
