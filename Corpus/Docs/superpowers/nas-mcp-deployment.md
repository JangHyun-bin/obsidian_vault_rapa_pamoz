---
type: doc
status: living
last_reviewed: 2026-05-29
owner: "[[FAMOZ]]"
---

# NAS MCP 서버 배포 가이드

vault corpus를 Synology NAS에 Docker로 호스팅하고, **Claude Code/Desktop에서 자연어 질문 → corpus 검색·인용** 까지 가능하게 만드는 셋업·운영 가이드.

이 문서는 *재현 가능*하도록 작성됨 — NAS 옮기거나 새 환경 셋업 시 그대로 따라가면 동일 결과.

---

## 아키텍처

```
PC (사내) ─┐                              ┌─ Tailscale Funnel
PC (외부) ─┼─→ MCP 클라이언트 (Claude) ──┤
모바일 ────┘                              ↓
                              https://famoz-nas.<tailnet>.ts.net/sse
                                        ↓
                              [NAS docker-compose]
                              ┌─────────────────────────┐
                              │ rapa-rag-mcp            │  ← MCP SSE server
                              │  (Python + BM25)        │     port 8765
                              │                         │
                              │  reads: /vault          │
                              └─────────────────────────┘
                                        ↓
                              /volume1/docker/rapa-corpus
                              (NAS에 git clone 한 vault repo)
```

**핵심 결정**:
- **BM25 only retrieval** — torch/sentence-transformers/faiss 다 제외. RAM 250MB로 가벼움 (NAS 2GB OK)
- **외부 노출 = Tailscale Funnel** — Cloudflare Tunnel은 도메인 없으면 못 씀. Tailscale은 무료·영구 `*.ts.net` URL
- **Bearer token 인증** — Funnel이 public이라 URL+토큰 둘 다 있어야 접근
- 의미 검색은 **Claude(외부)가 chunk 후보 받아 보완**

---

## 사전 준비

### NAS 측
- Synology DSM 6 또는 7
- Docker 또는 Container Manager 패키지 설치
- SSH 활성화 (제어판 → 터미널 및 SNMP)
- 빈 디스크 공간 ≥ 3GB (BM25-only 빌드 기준)
- 사용자 홈 서비스 활성화 (제어판 → 사용자 및 그룹 → 고급)

### 계정
- GitHub PAT (vault repo 권한, `repo` scope) — 발급 후 NAS에만 사용
- Tailscale 계정 (Google/MS/GitHub 로그인 — 무료)

---

## 1단계 — vault clone (NAS SSH, ~5분)

```bash
ssh <user>@<NAS-IP>

# /volume1/docker 디렉토리 준비
sudo mkdir -p /volume1/docker
sudo chown -R $(whoami):users /volume1/docker

cd /volume1/docker

# git credential 영구 저장 (한 번만 입력)
git config --global credential.helper store

# clone (Username: GitHub username, Password: PAT)
git clone https://github.com/JangHyun-bin/RAPA_Smart_Hospital_AI_Corpus.git rapa-corpus
```

## 2단계 — Bearer token 생성 + .env (~1분)

```bash
cd /volume1/docker/rapa-corpus/scripts

# 안전한 token 생성
TOKEN=$(openssl rand -base64 32 | tr -d /=+ | head -c 40)
echo "Token: $TOKEN"   # 어딘가 안전한 곳에 메모 (Claude Code 등록 시 필요)

# .env 작성
echo "RAPA_MCP_TOKEN=$TOKEN" > .env
cat .env
```

⚠️ **token 값을 채팅/이메일/메모 앱에 평문 저장 X**. 1Password / Bitwarden 같은 비밀번호 관리자에 저장.

## 3단계 — Docker 컨테이너 빌드·실행 (~3분)

```bash
sudo docker-compose up -d --build
```

빌드 1~2분 (BM25-only 가벼운 deps만). 끝나면:
```
Successfully built ...
Creating rapa-rag-mcp ... done
```

확인:
```bash
sudo docker logs -f rapa-rag-mcp
```

기대 출력:
```
[entrypoint] Building RAG index at /vault/scripts/rag/index ...
[entrypoint] Index built.
[entrypoint] Starting MCP server (transport=sse, port=8765) ...
INFO:     Uvicorn running on http://0.0.0.0:8765
```

`Ctrl+C` 로 로그 따라가기 종료 (컨테이너는 계속 가동).

### 사내망 동작 확인

```bash
# 인증 없이 → 401 (인증 활성 확인)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/sse

# 토큰으로 → 200 (3초 timeout, SSE는 long-lived)
curl -s -o /dev/null -w "%{http_code}\n" --max-time 3 \
  -H "Authorization: Bearer $TOKEN" http://localhost:8765/sse
```

`401` / `200` 나오면 ✅.

## 4단계 — Tailscale 설치 + Funnel 활성화 (~10분)

### Tailscale 패키지 설치 (DSM GUI)
1. 패키지 센터 → "Tailscale" 검색 → 설치
2. 검색 안 되면 https://pkgs.tailscale.com/stable/#synology 에서 본인 NAS 모델용 .spk 받아 → 수동 설치

### 로그인
```bash
sudo tailscale up
```
출력 URL을 PC 브라우저에 페이스트 → Google/GitHub 등으로 로그인.

### Funnel 활성화 (외부 인터넷 노출)
```bash
sudo tailscale funnel --bg 8765
tailscale funnel status
```

기대 출력:
```
# Funnel on:
#     - https://famoz-nas.<tailnet>.ts.net

https://famoz-nas.<tailnet>.ts.net (Funnel on)
└─ / proxy http://127.0.0.1:8765
```

이 URL을 메모.

### 외부 동작 확인

**PC 브라우저 또는 휴대폰 LTE** (NAS의 funnel URL을 NAS 자기 자신이 호출하면 loopback으로 안 되므로 *반드시 외부에서*):

```
https://famoz-nas.<tailnet>.ts.net/sse
```

- "Unauthorized" → 인증 활성 ✓
- SSE 응답(`event: endpoint`) → 인증 비활성 (RAPA_MCP_TOKEN 미설정 상태)

## 5단계 — Claude Code MCP 등록 (~1분)

PC PowerShell 또는 bash:

```bash
claude mcp remove rapa-corpus 2>/dev/null
claude mcp add --transport sse rapa-corpus \
  https://famoz-nas.<tailnet>.ts.net/sse \
  --header "Authorization: Bearer <token>"

claude mcp list
```

`--header` 지원 안 되면 `-H` 또는 `claude mcp add --help` 로 정확한 옵션 확인.

Claude Code 재시작 → `/mcp` 에서 `rapa-corpus` `connected` 확인.

### 사용

채팅에 자연어로:
```
나: 측위 백엔드는 어디에 배치하기로 했지?
```

Claude 가 자동으로 `rapa-corpus` 의 `ask` 도구 호출 → corpus 검색 → 출처 + 답변.

---

## 운영

### vault 변경 반영

PC에서 vault 수정 → `git push` → NAS는 *자동 갱신 안 됨*. NAS에서 수동:

```bash
cd /volume1/docker/rapa-corpus
git pull
# 인덱스는 컨테이너 시작 시 빌드되니, 재시작으로 인덱스 갱신:
cd scripts
sudo docker-compose restart rapa-rag-mcp
```

또는 컨테이너 안에서 인덱스만 재빌드:
```bash
sudo docker exec rapa-rag-mcp python -c \
  "from pathlib import Path; from rag.build_index import build_index; build_index(Path('/vault'), Path('/vault/scripts/rag/index'))"
sudo docker-compose restart rapa-rag-mcp
```

### Token rotate (90일 권장)

```bash
cd /volume1/docker/rapa-corpus/scripts
NEW_TOKEN=$(openssl rand -base64 32 | tr -d /=+ | head -c 40)
echo "New: $NEW_TOKEN"

# .env 갈아끼기 (기존 RAPA_MCP_TOKEN 줄 교체)
sed -i "s|^RAPA_MCP_TOKEN=.*|RAPA_MCP_TOKEN=$NEW_TOKEN|" .env

sudo docker-compose up -d
```

그리고 PC에서:
```bash
claude mcp remove rapa-corpus
claude mcp add --transport sse rapa-corpus <URL> --header "Authorization: Bearer $NEW_TOKEN"
```

### 로그·진단

```bash
# 최근 100줄
sudo docker logs --tail 100 rapa-rag-mcp

# 실시간
sudo docker logs -f rapa-rag-mcp

# 컨테이너 상태
sudo docker ps | grep rapa-rag

# Tailscale 상태
tailscale status
tailscale funnel status
```

---

## 트러블슈팅

### 빌드 중 nvidia-* 패키지 다 받음 (~1.5GB)
- `requirements-light.txt` 사용 확인 (Dockerfile에서). torch/sentence-transformers/faiss 빠진 가벼운 버전이어야 함.
- 잘못 빌드됐다면 `sudo docker image prune -f` 후 재빌드.

### `Invalid Host header` / `421 Misdirected Request`
- mcp 1.27의 `transport_security` 가 외부 host 거부.
- `mcp_server.py` 의 `_BearerAuthASGI` + `enable_dns_rebinding_protection=False` 우회 코드 적용 확인.
- 위 우회 코드는 `mcp.sse_app()` 직접 호출 + uvicorn 사용 흐름이어야 작동.

### `Uvicorn running on http://127.0.0.1:8000` (잘못된 host/port)
- `mcp_server.py` 의 `mcp.settings.host`/`mcp.settings.port` 명시 설정 확인.
- `mcp.run()` 단순 호출은 환경변수 무시함 → `mcp.sse_app() + uvicorn.run()` 패턴 사용.

### `pip install` 시 `markitdown==0.0.1a3` not found
- Python 3.13에서는 wheel 없음. 컨테이너는 `python:3.11-slim` 사용.
- `pyproject.toml`의 `requires-python = ">=3.11,<3.12"` 확인.

### `Authentication failed for ... github.com`
- GitHub은 비번 인증 차단. PAT(`ghp_...`) 만 사용.
- `git config --global credential.helper store` 후 한 번만 입력하면 영구 저장.

### NAS 안에서 funnel URL curl → `000`
- Tailscale loopback 이슈. NAS 자기 자신이 외부 URL 호출 못함.
- 반드시 *외부* (PC 브라우저, 휴대폰 LTE) 에서 확인.

### Claude Code `/mcp` 에서 connection error
- 우선 PC PowerShell에서 `curl.exe -H "Authorization: Bearer $TOKEN" <URL>/sse --max-time 3` 결과 확인.
- 200 이면 Claude Code 설정 문제 → `claude mcp list` 로 헤더 등록 확인.
- 401 이면 토큰 불일치 — `.env` 의 값과 Claude Code 등록값 비교.

---

## 정리 (deployment 풀어 내릴 때)

```bash
# 컨테이너 멈춤 + 제거
cd /volume1/docker/rapa-corpus/scripts
sudo docker-compose down

# 이미지 정리
sudo docker rmi rapa-rag-mcp:latest

# Tailscale funnel 끄기
sudo tailscale funnel 443 off
sudo tailscale serve reset

# (선택) Tailscale device 자체 제거
sudo tailscale logout
```

---

## 참고

- [Tailscale Funnel docs](https://tailscale.com/kb/1223/funnel)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP](https://github.com/jlowin/fastmcp)
- Vault 설계 문서: `docs/superpowers/specs/2026-05-28-corpus-design.md`
- 구현 plan: `docs/superpowers/plans/2026-05-28-corpus-migration.md`
- 미해결 follow-up: `docs/superpowers/phase-a-c-followup.md`
