---
type: spec
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
implements: []
version: v1
tags: [push, notification, lemon, api]
---

# 푸시서비스 (전남대학교병원 PUSH API)

전남대학교병원 환자앱 푸시 알림 발송 API 명세. 레몬헬스케어 API 서버 경유 (FCM/APNS 백엔드는 레몬케어 책임). 본 사업의 AI Proactive 안내·검사실 도착 알림 등이 이 API를 통해 발송됨.

*원본 아카이브: [[_raw/전남대학교병원_푸시서비스_개발가이드]]*

---

## 1. 엔드포인트

| 환경 | URL |
|---|---|
| 개발 | `https://common-dev.lemonhc.com:8001/mobile-ui/user/api/push/v1` |
| 운영 | `https://common-ui.lemonhc.com/mobile-ui/user/api/push/v1` |

- Method: `POST`
- 인증: `accKey` (전남대학교병원: `7f3ccb16-9efb-5adc-b48c-f87d4b38aefd`, 개발/운영 동일)

## 2. Request

| 필드 | 설명 | 필수 | 예시 |
|---|---|---|---|
| `hospitalCd` | 요양기관번호 | ✓ | `36100013` |
| `appDeploymentType` | 앱 배포 타입 | ✓ | `IN_HOUSE`(개발) / `APP_STORE`(운영) |
| `patientId` | 환자번호 | ✓ | `00000001` |
| `text` | 푸시 메시지 본문 | ✓ | `홍길동님, 진료 대기 5번입니다.` |
| `uri` | 메뉴키값 URI | - | 푸시 클릭 시 이동 경로 (없으면 단순 알림) |

### 예시

**단순 알림:**
```json
{
  "hospitalCd": "36100013",
  "appDeploymentType": "IN_HOUSE",
  "patientId": "00000001",
  "text": "홍길동님, 환영합니다."
}
```

**메뉴 이동:**
```json
{
  "hospitalCd": "36100013",
  "appDeploymentType": "IN_HOUSE",
  "patientId": "00000001",
  "text": "홍길동님 이제 곧 진료 차례입니다. OO과에 대기하여 주세요.",
  "uri": "menu.내일정"
}
```

## 3. Response

```json
{
  "elapsedTime": 0,
  "status": "OK",
  "errors": [],
  "message": "",
  "timestamp": "2018-10-28 23:57:48",
  "bodyType": "ARRAY",
  "body": {
    "createDate": "2018-10-28 23:57:48",
    "failure": 0,
    "multicastId": "d50c33ec-dac1-11e8-8daf-0242f51e8137",
    "results": "[{message_id=0:1540738692533414%e0e2eecae0e2eeca}]",
    "success": 1
  }
}
```

## 4. 메시지 시나리오 (병원 가이드)

| 구분 | 예문 | 이동 메뉴 |
|---|---|---|
| 예약안내 | 진료예약일은 XX월XX일 입니다 | `menu.내일정` |
| 진료도착확인 | OO과에 접수되었습니다 | — |
| 진료대기순서 | 대기순번 3번째 / 대기시간 길 때 편의시설 안내 | `menu.내일정` / `menu.편의시설` |
| 입원안내 | 환자의 빠른 회복을 기원합니다 | `menu.입원생활안내` |
| 수납안내 | 진료 완료, 모바일 결제 가능 | `menu.진료비결제` |
| 조제안내 | 원내 1층외래약국 / 원외약국 위치 | `menu.내일정` / `menu.전자처방전달` |
| 검사일정안내 | XX시 방사선 검사 예정 | `menu.검사일정조회` |
| 진료면담 | 치료 후 면담, OOOO으로 | `menu.내일정` |

## 5. 페이지 이동 URI 카탈로그

`menu.홈`, `menu.외래`, `menu.입원`, `menu.건강검진`, `menu.안내`, `menu.간편예약`, `menu.간편검진예약`, `menu.건강수첩`, `menu.검사결과조회`, `menu.검사일정조회`, `menu.검진결과조회`, `menu.검진절차안내`, `menu.검진프로그램`, `menu.병원안내도`, `menu.내번호표`, `menu.내일정`, `menu.대리결제`, `menu.대사증후군관리`, `menu.도움요청`, `menu.문진표작성`, `menu.전자처방전달`, `menu.진료비결제`, `menu.편의시설`, `menu.입원생활안내` ...

전체 카탈로그는 _raw 원본 표 4번 참조.

## 6. 본 사업과의 통합

- AI Proactive 안내 (진료실 도착·차례 도래·검사 일정) → 이 API로 push
- 푸시 발송 트리거: 측위 백엔드 ([[0004-backend-onpremise-hospital]]) 가 "체크포인트 도달" 이벤트 발행 → AI 기능 서버가 메시지 생성 → 본 API로 발송
- 책임 분담: 푸시 발송 = 레몬헬스케어 ([[0006-qab-gateway-only]] 백엔드 통합 포인트), 메시지 생성·트리거 = 파모즈

## 7. 미해결 / 후속

- 본 사업용 신규 메시지 패턴 (위치기반·AR 길안내 관련) 메뉴 URI 추가 협의
- `appDeploymentType` 의 `IN_HOUSE`/`APP_STORE` 외 추가 배포 채널 (TestFlight, Internal Testing) 처리 방식
- Rate Limit 명세 부재 — [[domain/sdk-개발-사전문의]] Q7.2 답변 필요
- SLA / 장애 fallback 명세 부재 — Q7.3, Q7.4 답변 필요
