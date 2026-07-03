---
id: "0004"
type: decision
status: superseded
date: 2026-05-14
deciders: ["[[FAMOZ]]"]
supersedes: null
superseded_by: "[[0010-compute-placement-ondevice-first-server-accelerator]]"
related_specs: ["[[r-and-r]]"]
related_meetings: ["[[2026-05-14-개발협의-아젠다-v2]]", "[[2026-05-18-스마트병원-AI-회의록]]"]
tags: [infrastructure, phi, gpu, positioning]
---

# 0004 — 측위 백엔드 + GPU 배치 = 병원 온프레미스 (제안)

## 컨텍스트

레몬헬스케어 안은 측위 관련 서버를 네이버 클라우드에 배치하는 구조. 클라우드 GPU LLM도 1안(본 과제 수행기)에서 각 병원 내부 온프레미스 GPU, 2안에서 클라우드 또는 외부 API(예: Google API)로 제시. 파모즈 검토 의견은 의료법·PHI 관점에서 방향성 재검토 필요.

5-18 회의에서 병원이 온프레미스 설치를 *선호*하나 구체 범위 미확정. AI 서버 연내 도입 예정. GPU 견적: RTX Pro 6000 ≈ 1,600만원, RTX 5090 데스크탑 ≈ 800만원.

## 옵션

**GPU 전략:**
- α. **레몬 1안 → 클라우드 (네이버 또는 외부 API)**
- β. **온프레미스 분산 (병원별 GPU)**
- γ. **네이버 클라우드 공동 GPU 풀 (다수 병원 공유)** — 1차년도, 비용 효율

**측위 백엔드:**
- A. **네이버 클라우드 배치** (레몬 안)
- B. **병원 온프레미스/DMZ 배치** (파모즈 제안)

## 결정 (proposed)

**β/γ + B 조합 — 측위 백엔드 + sLLM 모두 병원 온프레미스 또는 DMZ**:

측위 백엔드 권장 구성:
- 센서 스트림 수신 게이트웨이 (WiFi/BLE/IMU 스트림, 윈도우 버퍼링)
- DL 측위 추론 서버 (Res-Transformer-LSTM, GPU 기반)
- 융합·필터 엔진 (EKF/Particle Filter, IMU dead reckoning, QR 앵커 보정)
- 측위 DB (핑거프린팅, 비콘 좌표, 실내지도, POI)
- 위치 이벤트 Pub/Sub (MQTT 또는 WebSocket)

## 근거

- **측위 인프라(WiFi AP, BLE 비콘, 핑거프린팅 맵)는 병원 건물 자산이며 본질적으로 병원 종속적**
- 환자 위치 데이터는 의료기록 결합 시 PHI에 준하는 민감 정보
- 1–5Hz 실시간 처리를 위해 클라우드 라운드트립 지연 회피
- 외부 API(Google) 사용은 의료법 제28조의8(개인정보 국외 이전) 사실상 적용 불가 — [[0008-lbs-notification-by-lemon]] 의 분석과 연결

## 결과

- 긍정: PHI 안전, 지연 최소, 데이터 주권
- 부정/리스크: 병원별 GPU 자원 산정 필요 (현재 구성도에 누락), 측위용 GPU 별도, 원격 관리 채널 필요 (QAB와 별도)
- 영향받는 스펙: [[r-and-r]] (현장 인프라)
- 미해결: 1안/2안 방향성 컨소시엄 합의, 외부 API 활용 가능 여부에 대한 법무 자문 결과 반영, 측위용 GPU 자원 산정

## 변경 이력

- 2026-05-14: 아젠다 v2 B-1, B-3에서 클라우드 vs 온프레미스 검토
- 2026-05-14: 본 ADR — 온프레미스 제안 (proposed)
- 2026-05-18: 회의에서 병원 측 온프레미스 선호 확인 (범위 미확정) — proposed 유지
