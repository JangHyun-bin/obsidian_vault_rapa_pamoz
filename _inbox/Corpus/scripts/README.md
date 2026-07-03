# scripts/

Vault 유지·운영용 스크립트.

## 계획 (설계 문서의 ETL/무결성 섹션 참조)

- `ingest/convert.py` — `_raw/` 신규 파일 → `_converted/` 자동 변환 (markitdown + hwp5txt)
- `check_corpus.py` — 무결성 체크 (supersedes 양방향 / 깨진 백링크 / frontmatter 필수 필드)
- `build_index.sh` — Vault → Domain_RAG 인덱스 빌드 트리거

각 스크립트는 실제 구현 시점에 추가.
