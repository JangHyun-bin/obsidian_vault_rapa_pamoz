# 실내측위·AR 내비게이션 유사 프로젝트 레퍼런스 조사

> 문서 등급: PUBLIC RESEARCH - External Reference
>
> 문서 버전: v0.1-draft
>
> 기준일: 2026-07-13

## 1. 문서 목적과 사용 범위

본 문서는 병원 실내측위, 디지털 길찾기 및 AR 내비게이션의 공개 적용 사례를 조사하여 Position SDK의 제품 범위와 연동 방향을 검토하기 위한 자료이다.

아래 사례는 모두 외부 기관 또는 솔루션 공급자가 공개한 자료에 기반한다. 기술과 성과는 공개 자료에서 확인되는 범위에 한해 기재했으며, 공급자 자료에만 근거한 내용은 별도로 표시한다.

## 2. 조사 기준

- 병원 또는 복합 실내공간에서 실제 사용되었거나 공식 시험된 사례
- 기존 모바일 앱, 환자 포털, 웹 또는 키오스크와의 연동 구조를 확인할 수 있는 사례
- 실내 지도, 블루닷 측위, 경로 안내, AR 안내 중 하나 이상을 포함한 사례
- 병원·공공기관·시설 운영자의 1차 자료를 우선 사용
- 공급자 자료는 적용 범위 확인용으로 사용하고 정량 성과는 보수적으로 해석

### 2.1 출처 신뢰도 표기

| 등급 | 기준 | 문서 내 사용 방법 |
|---|---|---|
| A | 병원, 공공기관, 시설 운영자의 공식 자료 | 사실관계의 주 근거 |
| B | 기술 또는 솔루션 공급자의 공식 사례·기술 문서 | 구조와 제공 기능의 보조 근거 |
| C | 언론 보도, 2차 요약 자료 | 본 문서에서는 원칙적으로 제외 |

## 3. 사례 요약

| 사례 | 분야 | 제공 채널 | 확인된 핵심 기능 | 출처 |
|---|---|---|---|---|
| UCHealth University of Colorado Hospital | 병원 | 기존 UCHealth 앱 | 예약 목적지 연계, 실외·실내 연속 안내, 블루닷, 다층 경로 | A |
| University Hospitals of Leicester NHS Trust | 병원 PoC | 모바일 웹·앱·키오스크 | QR 목적지, 다국어 경로, 지도, 블루닷 검증 | A |
| St. Olavs Hospital | 병원 | 웹 기반 실내 지도 | 공간 검색, A-to-B 경로, 목적지 공유, 게스트 Wi-Fi 비연결 시 축약 지도 | A |
| Quironsalud | 다기관 병원 | 환자 포털 앱 | 실시간 실내 안내, 다기관 확장 | B |
| Sydney Airport Indoor Live View | 대형 복합시설 | Google Maps Android·iOS | 카메라 기반 AR 방향·거리 표시, 접근성 경로, 음성 안내 | A |

## 4. 상세 사례

### 4.1 UCHealth: 기존 환자 앱에 실내 길찾기 통합

**적용 개요**

- University of Colorado Hospital의 5개 건물, 60개 이상의 층을 대상으로 길찾기 기능을 제공한다.
- 별도 앱이 아니라 기존 UCHealth 앱의 `Find your way` 기능으로 통합되었다.
- 실외에서는 GPS를 사용하고, 실내에서는 휴대전화 가속도계와 주로 Bluetooth 신호를 사용한다.
- 약 3,000개의 Bluetooth 장치를 병원 천장에 설치한 것으로 공개되어 있다.
- Epic/My Health Connection의 예약정보와 연결하여 예약 목적지를 앱에서 바로 안내 대상으로 사용할 수 있다.
- 위치는 블루닷, 경로는 지도 위 선으로 표시하며 주차장부터 진료 구역까지 이어지는 흐름을 제공한다.

**구조적 시사점**

- 예약·진료 맥락과 최종 화면은 기존 환자 앱이 소유하고, 측위·지도 기술은 그 기능 안에 통합하는 형태이다.
- 호스트 앱이 `venueId`, 예약에서 해석한 `destinationId` 등을 SDK에 전달하는 현재 연동 방향과 유사하다.
- OS 권한 설명과 개인정보 정책은 최종 앱의 사용자 흐름 안에서 다루어야 한다. UCHealth도 위치, Bluetooth, 신체활동 권한의 목적을 앱 개인정보정책에 명시한다.
- 병원별 인프라와 공간 데이터 구축은 SDK 바이너리 배포와 별개의 현장 구축 작업이다.

**차이 및 유의사항**

- 해당 사례는 대규모 BLE 인프라를 사용한다. 현재 Position SDK의 측위 방식과 동일한 방식 또는 동일 정확도를 의미하지 않는다.
- 환자실 수준의 정밀 위치가 가능하더라도 개인정보 보호를 위해 안내 목적지를 진료구역 단위로 제한한 운영 정책을 참고할 필요가 있다.

자료: [UCHealth 적용 사례](https://www.uchealth.org/today/hospital-wayfinding-app-helps-patients-visitors-navigate-university-of-colorado-hospital/), [UCHealth 공식 발표](https://www.uchealth.org/innovation/media/new-technology-accessible-on-uchealths-mobile-app-will-help-patients-and-visitors-easily-find-their-way-around-university-of-colorado-hospital/), [UCHealth 개인정보정책](https://www.uchealth.org/privacy-policy/)

### 4.2 University Hospitals of Leicester: 병원 Wi-Fi 기반 디지털 길찾기 시험

**적용 개요**

- NHS England 프로그램으로 2024년 8월부터 2025년 3월까지 Leicester General Hospital 일부 구역에서 시험되었다.
- 변환된 병원 실내 지도와 개인화 경로를 모바일 기기 및 키오스크에 제공했다.
- 예약 안내 또는 현장 표지의 QR 코드를 목적지 진입점으로 사용하고, QR 코드가 없을 때는 부서·병동명 검색을 제공했다.
- 다국어와 접근성을 주요 요구사항으로 포함했다.

**확인된 한계**

- 병원 Wi-Fi의 식별·커버리지 조건 때문에 웹과 앱의 실시간 블루닷 기능이 계획대로 동작하지 않았다.
- 비 NHS Wi-Fi 연결에서도 위치 갱신 지연과 블루닷 부정확성이 관찰되었다.
- 시험은 전체 병원이 아닌 일부 구역에 한정되었고, 미방문 감소가 길찾기 기능만의 효과라고 단정할 수 없다고 공식 결과에 기재되어 있다.

**구조적 시사점**

- 정적 지도·경로와 실시간 블루닷은 별도 capability로 정의해야 한다.
- 측위 실패 시에도 QR 시작점, 검색, 정적 경로, 키오스크 같은 폴백을 제공할 수 있어야 한다.
- 병원 네트워크, SDK, 앱을 함께 검증하는 통합 테스트가 초기 설계 단계에 포함되어야 한다.
- 지도 변환 후 현장 담당자의 검토와 승인 절차가 필요하다.

자료: [NHS England 공식 사례 보고서](https://digital.nhs.uk/services/networks-and-connectivity-centre-of-excellence/connectivity-hub/wireless-trials/connectivity-hub-wireless-trialist-case-studies/university-hospitals-of-leicester-nhs-trust//)

### 4.3 St. Olavs Hospital: 설치 부담이 낮은 웹 실내 지도

**적용 개요**

- 병원 공식 페이지에서 MazeMap 기반 실내 지도와 내비게이션을 제공한다.
- 공간 검색, 출발지에서 목적지까지의 경로, 목적지 공유 기능을 제공한다.
- 병원 게스트 Wi-Fi 연결 시 층과 방까지 경로를 따라갈 수 있고, Wi-Fi 없이도 세부정보가 줄어든 지도를 사용할 수 있다고 안내한다.

**구조적 시사점**

- 모든 사용자가 앱 설치, 카메라 또는 고정밀 측위를 사용할 것이라고 가정하면 안 된다.
- 2D 지도·검색·정적 경로는 AR 또는 실시간 측위의 장애와 단말 제한을 보완하는 독립적인 기본 기능이 될 수 있다.
- 목적지 링크 공유는 예약 알림, 문자, 접수 안내와 길찾기를 연결하는 단순한 통합 방법이다.

자료: [St. Olavs Hospital 공식 지도 페이지](https://www.stolav.no/en/about-the-hospital/contact-us/map/), [상세 안내 페이지](https://www.stolav.no/om-oss/kontakt-oss/kart/)

### 4.4 Quironsalud: 환자 포털 기반 다기관 확장

**적용 개요**

- Situm 공개 자료에 따르면 실내 안내 기능이 5개 병원과 2개 전문센터에 적용되었다.
- 환자와 방문자는 환자 포털 앱에서 실시간 실내 안내를 사용한다.
- 공급자는 공개 당시 100만 명 이상의 환자가 사용할 수 있는 범위라고 설명했다.

**구조적 시사점**

- 병원별 화면을 별도 제품으로 만드는 대신 공통 환자 포털에 측위·길찾기 기능을 결합한 구조이다.
- 다기관 확장을 위해 SDK 버전과 병원별 지도·POI·경로 데이터 버전을 분리해야 한다.
- `venueId`를 기준으로 공간 패키지를 선택하고 검증하는 방식이 적합하다.

**출처 한계**

- 적용 범위와 이용 가능 환자 수는 솔루션 공급자의 공식 사례 자료에 근거하며 독립적인 효과 측정 자료는 아니다.
- 공개 자료만으로 SDK API, 위치 정확도, 폴백 정책은 확인할 수 없다.

자료: [Situm 공식 적용 사례](https://situm.com/?p=3083)

### 4.5 Sydney Airport: 대형 실내공간의 AR 내비게이션

**적용 개요**

- Google Maps의 Indoor Live View가 국제선·국내선 터미널에서 Android와 iOS로 제공되었다.
- 카메라 화면 위에 방향 화살표, 안내 문구, 거리 표식을 중첩한다.
- 탑승구, 수하물 수취, 체크인, 환승 지점, 상점, 식당, 화장실, ATM 등을 목적지로 지원한다.
- 휠체어, 유모차, 여행가방에 적합한 경로 선택과 음성 안내를 함께 제공한다.
- 공항 운영사 자료에 따르면 445,000m² 이상의 터미널을 대상으로 2022년부터 실내 이미지를 수집했다.

**구조적 시사점**

- AR은 지도와 경로를 대체하는 별도 제품이 아니라, 계산된 방향과 거리를 카메라 화면에 표현하는 안내 모드로 설계할 수 있다.
- AR 제공 전에는 대상 공간의 이미지·앵커·POI 구축과 단말 호환성 확인이 선행되어야 한다.
- 접근성 경로와 음성 안내는 지도 데이터 및 UX 요구사항에서 함께 정의해야 한다.
- 카메라 사용이 불가능하거나 AR capability가 부족한 경우 2D 안내로 전환해야 한다.

**차이 및 유의사항**

- 공항 사례이며 병원 예약·진료 흐름과 직접 동일하지 않다.
- Google의 글로벌 로컬라이제이션과 자체 수집 이미지에 기반하므로 Position SDK의 구현 방식이나 성능 비교 자료로 사용할 수 없다.

자료: [Sydney Airport 공식 발표](https://www.sydneyairport.com.au/corporate/media/corporate-newsroom/australian-first-google-indoor-live-view-lands-at-sydney-airport), [Google 공식 소개](https://blog.google/intl/en-au/products/explore-get-answers/indoor-live-view-sydney-airport/)

## 5. 공통 구현 패턴

공개 사례와 기술 가이드에서 다음 패턴을 확인할 수 있다.

### 5.1 앱과 측위 기능의 책임 분리

NHS England의 RTLS 가이드는 실내 길찾기 솔루션을 블루닷·경로의 기반 capability로 설명하고, 실제 모바일 앱은 내부 개발 또는 별도 프로젝트로 구성하여 연결한다고 설명한다. MapsIndoors의 SDK 문서도 경로 요청·응답 처리와 최종 UI/UX 구성을 구분한다.

따라서 Position SDK의 기본 계약은 다음과 같이 두는 것이 타당하다.

- SDK: 측위, 경로, 상태, capability, 이벤트, 오류
- 호스트 앱: 권한 설명, 예약·진료 연계, 화면 전환, 브랜딩, 최종 폴백 UI
- 선택 UI 모듈: 2D 지도·블루닷 또는 AR 안내의 기본 구현체

자료: [NHS England RTLS 가이드](https://digital.nhs.uk/services/networks-and-connectivity-centre-of-excellence/connectivity-hub/advice-and-guidance/rtls-guidance/use-cases-and-capabilities//), [MapsIndoors Directions Service 문서](https://docs.mapsindoors.com/sdks-and-frameworks/web/directions-and-routing/directions-service)

### 5.2 공간 데이터의 별도 생명주기

모든 사례는 시설별 도면, 층, POI, 경로 또는 이미지 구축을 전제로 한다. 시설이 바뀌거나 공간이 개편되어도 앱과 SDK 바이너리를 항상 함께 배포하는 방식은 운영 효율이 낮다.

따라서 다음 분리를 권장한다.

- SDK artifact: 측위·경로 실행 코드와 공개 API
- Venue Package: 도면, 층, POI, 경로 그래프, 앵커 및 런타임 맵
- 운영 절차: 서베이, 데이터 생성, 현장 검수, 승인, 배포, 갱신 및 롤백

이는 공개 사례를 바탕으로 한 설계 권고이며, 외부 사례의 패키지 형식을 그대로 사용한다는 의미는 아니다.

## 6. 프로젝트에 반영 가능한 결론

### 6.1 제품 범위

- SDK 안에 최종 프론트엔드 전체를 고정 포함하지 않는다.
- headless 코어를 필수 제공 범위로 하고, 기본 2D/AR UI는 선택 모듈 또는 샘플로 정의한다.
- 예약, 접수, 진료, 브랜딩 및 최종 화면 전환은 호스트 앱 범위로 둔다.

### 6.2 측위 맵 전달 방식

- 서베이 후 생성되는 측위 맵은 SDK 코드에 정적으로 내장하지 않고 병원·층별 Venue Package로 관리한다.
- PoC 단계에서 앱 리소스로 묶을 수는 있으나, 제품 계약은 SDK 버전과 공간 데이터 버전을 분리한다.
- 전달 전 필수 항목은 대상 범위, 원천 도면, POI, 좌표 정합, 현장 검수 기준, 갱신 책임, 데이터 호환 버전이다.

### 6.3 UI/UX 구체화 시점

UI/UX는 SDK 구현 완료 후 시작하는 후속 작업이 아니라 공개 API와 capability를 고정하기 전에 구체화해야 한다. 다음 순서를 권장한다.

1. 연동 범위와 책임 확정
2. 핵심 사용자 흐름 및 2D·AR·폴백 와이어프레임 확정
3. 진입 파라미터, 상태, 이벤트, 오류 API 확정
4. SDK와 Venue Package 구현
5. 대표 단말·대표 동선 통합 검증
6. 운영 승인 및 배포

UI/UX 컨셉 초안에는 최소 다음 화면 상태가 포함되어야 한다.

- 예약 또는 목적지 선택에서 길찾기 진입
- 권한 사전 설명과 거부·영구거부 처리
- 공간 데이터 준비 및 현재 위치 탐색
- 2D 지도·블루닷·경로 안내
- AR 초기 정합 및 AR 안내
- 층 변경, 경로 이탈, 위치 품질 저하
- AR 미지원·카메라 거부 시 2D 폴백
- 목적지 도착 및 안내 종료

## 7. 출처 목록

1. [UCHealth - Hospital wayfinding app feature](https://www.uchealth.org/today/hospital-wayfinding-app-helps-patients-visitors-navigate-university-of-colorado-hospital/)
2. [UCHealth - 공식 적용 발표](https://www.uchealth.org/innovation/media/new-technology-accessible-on-uchealths-mobile-app-will-help-patients-and-visitors-easily-find-their-way-around-university-of-colorado-hospital/)
3. [UCHealth - Privacy Policy](https://www.uchealth.org/privacy-policy/)
4. [NHS England - University Hospitals of Leicester Digital Patient Wayfinding](https://digital.nhs.uk/services/networks-and-connectivity-centre-of-excellence/connectivity-hub/wireless-trials/connectivity-hub-wireless-trialist-case-studies/university-hospitals-of-leicester-nhs-trust//)
5. [NHS England - RTLS Use Cases and Capabilities](https://digital.nhs.uk/services/networks-and-connectivity-centre-of-excellence/connectivity-hub/advice-and-guidance/rtls-guidance/use-cases-and-capabilities//)
6. [St. Olavs Hospital - Map](https://www.stolav.no/en/about-the-hospital/contact-us/map/)
7. [Situm - Quironsalud 적용 사례](https://situm.com/?p=3083)
8. [Sydney Airport - Indoor Live View 공식 발표](https://www.sydneyairport.com.au/corporate/media/corporate-newsroom/australian-first-google-indoor-live-view-lands-at-sydney-airport)
9. [Google - Indoor Live View at Sydney Airport](https://blog.google/intl/en-au/products/explore-get-answers/indoor-live-view-sydney-airport/)
10. [MapsIndoors - Directions Service](https://docs.mapsindoors.com/sdks-and-frameworks/web/directions-and-routing/directions-service)
