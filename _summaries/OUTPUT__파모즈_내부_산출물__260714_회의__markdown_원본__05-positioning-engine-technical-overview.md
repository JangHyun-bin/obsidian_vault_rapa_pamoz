---
original: "OUTPUT__파모즈_내부_산출물__260714_회의__markdown_원본__05-positioning-engine-technical-overview"
category: "Specs"
tags: [실내측위, 하이브리드, 카메라, 관성센서, 공간데이터]
related: [실내 위치 추적, 실내 내비게이션, 증강현실]
indexed_at: "2026-07-20T09:02:04"
---
# OUTPUT\파모즈_내부_산출물\260714_회의\markdown_원본\05-positioning-engine-technical-overview.md

**원본**: [[Internal/260714_회의/markdown_원본/05-positioning-engine-technical-overview.md|OUTPUT\파모즈_내부_산출물\260714_회의\markdown_원본\05-positioning-engine-technical-overview.md]]

## 요약
Position SDK는 카메라 기반 절대 위치 확인과 모바일 모션 센서 기반 연속 위치 추적을 결합한 하이브리드 실내측위 엔진이다. 초기 위치 또는 추적 재획득 시 시각 정보를 이용해 병원 공간 좌표계의 기준 위치를 확인하고, 이후 관성 센서와 공간 데이터를 확률적으로 결합해 위치와 불확실성을 제공한다.

## 태그
실내측위, 하이브리드, 카메라, 관성센서, 공간데이터

## 관련 키워드
실내 위치 추적, 실내 내비게이션, 증강현실
