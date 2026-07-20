# RAG Engine v0.1

전남대학교병원 안내 문서 29건을 BGE-M3 dense 임베딩으로 검색하고, Chroma의 유사 문서와 출처 metadata를 반환하는 독립 실행형 제출 코드입니다. 검색 기능과 이를 확인하는 단일 웹 화면만 포함합니다.

## 1. 설치

Python 3.12와 `uv`가 준비된 환경에서 이 서브프로젝트 폴더로 이동한 뒤 자체 가상환경을 동기화합니다.

```bash
cd deliverable/rag_engine_v0.1
uv python install 3.12
uv sync --group dev
```

예상 출력: 의존성 해석과 설치가 오류 없이 끝나고 현재 폴더에 `.venv`가 생성됩니다.

## 2. 인제스트

커밋된 `data/sample/corpus.jsonl`을 임베딩해 독립 Chroma DB에 업서트합니다. BGE-M3 모델은 이때 처음 로드되며, 같은 명령을 다시 실행해도 문서가 중복되지 않습니다.

```bash
uv run python scripts/ingest.py
```

예상 출력: 처리가 정상 종료되고 최종 컬렉션 건수로 `29건`이 표시됩니다.

## 3. 실행

기본 포트 `20013`에서 FastAPI 서버를 백그라운드로 시작합니다.

```bash
./start.sh
```

예상 출력: 서버 PID, 접속 주소, 로그 파일 `rag_engine_v01.log`가 표시됩니다. 이미 기록된 PID의 프로세스가 살아 있으면 새 서버를 시작하지 않습니다.

## 4. 확인

브라우저에서 아래 주소를 열어 검색어와 top-k를 입력하고 결과 카드의 유사도, 문서 발췌, 출처 기관과 URL을 확인합니다.

```text
http://<host>:20013
```

상태 API도 확인할 수 있습니다.

```bash
curl http://127.0.0.1:20013/api/status
```

예상 출력: 웹 화면이 열리고, 상태 API는 HTTP 200과 함께 `"version":"0.1.0"`, `"document_count":29`를 반환합니다.

서버 종료는 PID 파일에 기록된 해당 프로세스만 대상으로 수행합니다.

```bash
kill $(cat rag_engine_v01.pid)
```

기본 포트는 `PORT=20013`이며, `EMBEDDING_DEVICES`를 지정하지 않으면 CUDA 사용 가능 시 `cuda:0`, 그 외에는 `cpu`를 선택합니다. `EMBEDDING_DEVICES`에는 `cuda:0`, `auto`, `cpu` 또는 쉼표로 구분한 장치 목록을 지정할 수 있고 `EMBEDDING_USE_FP16`은 기본 `false`입니다. DB 경로는 기본적으로 이 서브프로젝트의 `data/chroma_v01/`이며 `RAG_V01_DB_PATH`로 별도 경로를 지정할 수 있습니다. BGE-M3는 외부 접속 없이 서버 공용 Hugging Face 캐시만 사용하므로 모델이 캐시에 준비되어 있어야 합니다.
