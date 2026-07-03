---
id: "0010"
type: decision
status: proposed
date: 2026-05-29
deciders: ["[[FAMOZ]]"]
supersedes: "[[0004-backend-onpremise-hospital]]"
superseded_by: null
related_specs: ["[[indoor-positioning]]", "[[cold-start-global-localization]]", "[[device-support-matrix]]", "[[v0-acceptance-gate]]"]
related_meetings: []
tags: [positioning, infrastructure, ondevice, gpu, phi, architecture]
---

# 0010 — 측위 연산 배치 갱신 = 온디바이스 우선 + 서버 accelerator (thin-client 폐기)

## 컨텍스트

[[0004-backend-onpremise-hospital]]은 측위 백엔드(센서 스트림 게이트웨이 + DL 측위 추론서버 Res-Transformer-LSTM + EKF/Particle Filter 융합엔진)를 **병원 온프레미스 GPU에 두는 thin-client** 구조를 제안했다 — 폰은 센서를 스트리밍하고 서버가 측위 전부를 수행.

deep-research 결론은 이 가정을 재검토하게 한다: 정상추적 정확도는 **연산이 아니라 센서 정보량·지도 해상도·IMU drift가 결정**(GPU-bound 아님)하며, 온디바이스 EKF/PF가 복도 sub-meter를 실시간(A17급 1만 입자 ≈ 100–500Hz)으로 낸다. thin-client는 (a) 네트워크 의존(망 장애 시 측위 정지), (b) 1–5Hz 왕복 지연(보행 내비 UX 악화), (c) raw 센서·위치 상시 스트리밍 → PHI 노출 표면 확대라는 비용을 다시 끌고 온다 — 0004가 온프레미스로 회피하려던 지연·PHI 문제를 구조 자체가 재유발.

## 옵션

- A. **0004 유지** — 서버 thin-client (게이트웨이 + DL 추론 + EKF/PF 전부 서버).
- B. **완전 온디바이스** — 서버 없음. 인프라 0이나 지도빌드·대형모델·구형폰 cold-start 대응 수단 없음.
- C. **온디바이스 코어 + 서버 accelerator** — 정상추적은 폰, 서버는 학습·cold-start 가속·drift에 한정. graceful degradation.

## 결정 (proposed)

**C. 온디바이스 우선 + 서버 accelerator (thin-client 폐기)**:

**온디바이스 (폰)**:
- 정상추적 EKF/Particle Filter — **1차 KPI(±2.5m) 담당**, 저지연, **오프라인 동작 가능**
- 신경관성(EqNIO/RoNIN) 추론 — NPU/GPU (iOS Core ML→ANE, Android NNAPI/TFLite). PF/EKF·자기장 likelihood는 CPU(SIMD/멀티코어)
- cold-start cascade(NFC/GPS/last-known/barometer/PF) 온디바이스 수행

**서버 (병원 온프레미스 GPU — 0004의 인프라 유지, 용도 재정의)**:
- ① 자기장 GP 지도 빌드 + per-venue 학습형 place-recognition 학습·재학습(오프라인)
- ② cold-start 글로벌-loc 가속(선택·1회성) — 구형/저가폰에서 특히 유용(수만 입자 스윕·대형모델 오프로드)
- ③ 대형 모델 주기적 refine, map staleness drift 감지, cross-device 자기 보정 집계

**철칙 — graceful degradation**: 서버가 없어도 폰 단독으로 측위가 돌아야 한다. 서버는 *accelerator*이지 *hard dependency*가 아니다.

**PHI**: 온디바이스 우선이라 raw 센서·위치 상시 스트리밍 불필요 → PHI 노출 표면 축소. 서버↔폰 통신은 지도/모델 배포 + 익명·집계 통계 위주로 제한.

## 근거

- 정상추적 정확도는 GPU-bound가 아니다 — 1.5m KPI에 서버가 더하는 정확도 ≈ 0. (서버는 학습·cold-start 가속·발열 완화라는 *간접* 경로로만 여건 개선.)
- 정보이론적 한계(대칭 venue 영구 비수렴)는 서버로 못 푼다 — [[0009-positioning-ondevice-magnetic-neural-fusion]]의 NFC 앵커가 해결.
- 1–5Hz 왕복 지연 회피 + 망 장애 시 측위 지속(오프라인) — 보행 내비 UX 신뢰성.
- raw 센서·위치 스트리밍 최소화로 PHI 표면↓ ([[0008-lbs-notification-by-lemon]] 위치정보 규제와 정합).
- 구형/저가폰은 온디바이스 cold-start 스윕이 버거움 → 서버 오프로드가 정확히 그 케이스를 보완.

## 결과

- 긍정: 저지연·오프라인 가능·PHI 표면↓·구형폰 대응(서버 오프로드)·온프레미스 GPU 투자 유지(용도 전환).
- 부정/리스크:
  - 서버↔폰 모델·지도 버전 동기화·배포 관리 필요.
  - cold-start 서버 오프로드 사용 시 네트워크 폴백(서버 불가 → 온디바이스 스윕) 설계 필수.
  - 온프레미스 GPU 자원 산정 = 실시간 추론용이 아니라 **학습+가속용**으로 재산정(0004의 "측위용 GPU 별도·산정 누락" 항목 갱신).
- 영향받는 스펙: [[0004-backend-onpremise-hospital]] (supersede), [[r-and-r]] (현장 인프라·서버 운영), [[0009-positioning-ondevice-magnetic-neural-fusion]] (알고리즘 연동).
- 미해결: 온프레미스 GPU 사양(학습/가속용) 산정; 서버 가속 API 계약(어떤 작업을 언제 오프로드); v0 spike의 iPhone thermal·입자예산 측정으로 온디바이스 budget 확정.

## 변경 이력

- 2026-05-29: deep-research 결론(정상추적 sensor-bound·온디바이스 sub-meter, thin-client의 지연·PHI 비용) 반영 — 온디바이스 우선 + 서버 accelerator로 전환. [[0004-backend-onpremise-hospital]] supersede 제안 (proposed).
- accepted 전환 조건: 컨소시엄 합의 + [[0009-positioning-ondevice-magnetic-neural-fusion]] 동반 합의 + 온프레미스 GPU 용도 재산정 합의.
