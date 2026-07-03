# RAPA Corpus 배포 가이드

이 문서는 **처음 배포할 때 1회만** 필요한 셋업 가이드입니다. 한 번 셋업해두면 이후로는 vault에 push할 때마다 자동 배포됩니다.

배포 파이프라인:
- **GitHub Actions** (`publish.yml`) — vault checkout → 무결성 체크 → Quartz 빌드 → Cloudflare Pages 업로드
- **Cloudflare Pages** — 정적 호스팅
- **Cloudflare Access** — 사내/컨소시엄 회원만 접근 가능하도록 인증 게이트

---

## 1. 사전 준비

배포 전 다음이 준비되어 있어야 합니다:

- **Cloudflare 계정** — 무료 플랜으로 충분합니다.
- **Vault repo가 GitHub에 push되어 있어야** — 본 워크플로우는 vault를 별도 repo에서 checkout합니다.
- **Corpus-Site repo도 GitHub에 push되어 있어야** — 워크플로우 파일이 GitHub에서 실행되려면 origin이 필요합니다.
- *(선택)* **Custom domain** — `rapa-corpus.famoz.kr` 같은 도메인을 쓰려면 DNS 제어권이 필요합니다.

---

## 2. GitHub Secrets 설정

`Corpus-Site` repo → Settings → Secrets and variables → Actions → **New repository secret** 으로 3개를 등록합니다.

### 2-1. `CORPUS_VAULT_TOKEN`
- **용도**: vault private repo를 checkout하기 위한 Personal Access Token
- **발급 방법**: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- **Scope**: `repo` (private repo 읽기 권한)
- **참고**: vault repo와 Corpus-Site가 **같은 GitHub user/org 소속이고** vault도 같은 user/org의 private repo라면, 워크플로우의 기본 `GITHUB_TOKEN` 으로도 충분할 수 있습니다. 다른 org/계정에 있다면 PAT가 반드시 필요합니다.

### 2-2. `CLOUDFLARE_API_TOKEN`
- **용도**: Cloudflare Pages 배포 권한
- **발급 방법**: Cloudflare Dashboard → My Profile → API Tokens → Create Token → **"Custom token"**
- **권한 (Permissions)**:
  - `Account` → `Cloudflare Pages` → `Edit`
- **Account Resources**: Include → 본인 account 선택

### 2-3. `CLOUDFLARE_ACCOUNT_ID`
- **용도**: 어느 Cloudflare 계정에 배포할지 식별
- **확인 방법**: Cloudflare Dashboard 우측 상단 또는 우측 사이드바의 "Account ID" 복사

---

## 3. Cloudflare Pages 프로젝트 생성

본 워크플로우는 GitHub Actions에서 빌드하고 Cloudflare는 호스팅만 담당합니다 (Cloudflare 자체 빌드 기능은 **사용하지 않음** — Python 무결성 체크를 거치려면 Actions가 필요).

1. Cloudflare Dashboard → **Workers & Pages** → **Pages** 탭 → **"Create a project"**
2. **"Direct upload"** 선택 (절대 "Connect to Git" 선택 금지 — 우리는 Actions로 빌드)
3. **Project name**: `rapa-corpus` (workflow의 `projectName` 과 정확히 일치)
4. 초기 더미 업로드는 그냥 빈 폴더라도 한 번 올려서 프로젝트를 생성하면 됩니다 — 이후 Actions가 덮어씁니다.
5. 생성 후 production branch는 무엇이든 상관없음 (Actions가 매번 production으로 deploy).

---

## 4. Custom Domain 설정 (선택)

기본 도메인은 `rapa-corpus.pages.dev` 입니다. 자체 도메인을 쓰려면:

1. Cloudflare Pages 프로젝트 → **Custom domains** → **"Set up a custom domain"**
2. 도메인 입력 (예: `rapa-corpus.famoz.kr`)
3. **DNS 설정**:
   - 해당 도메인의 nameserver가 **이미 Cloudflare에 위임**되어 있으면 → 자동으로 CNAME 추가됨
   - 다른 DNS provider를 쓴다면 → 수동으로 `CNAME` 레코드 추가:
     ```
     rapa-corpus.famoz.kr → rapa-corpus.pages.dev
     ```
4. SSL/TLS 인증서는 Cloudflare가 자동 발급 (수 분 소요).

---

## 5. Cloudflare Access 설정 (권장)

corpus는 **사내/컨소시엄 회원만** 봐야 합니다. Cloudflare Access (Zero Trust) 로 게이트를 답니다.

1. Cloudflare Dashboard → **Zero Trust** → **Access** → **Applications** → **"Add an application"**
2. Application type: **Self-hosted**
3. **Application name**: `RAPA Corpus`
4. **Application domain**: 위 4단계에서 설정한 custom domain (또는 `.pages.dev` 도메인)
5. **Identity providers**:
   - 가장 간단: **One-time PIN (email OTP)** — 별도 IdP 셋업 없이 이메일만 있으면 됨
   - 조직 단위로 관리: **Google Workspace**, **Azure AD** 등 연동
6. **Policy** 설정:
   - **Action**: Allow
   - **Include** → **Emails ending in**:
     - `@famoz.com`
     - `@jnuh.kr`
     - `@rapa.or.kr`
     - *(필요한 도메인 추가)*
7. 저장 후, 해당 도메인 접근 시 자동으로 Cloudflare Access 로그인 화면이 뜸.

---

## 6. Workflow placeholder 교체 ✅ 완료됨

`.github/workflows/publish.yml` 의 `repository` 가 실제 vault repo 경로로 이미 설정되어 있습니다:

```yaml
repository: JangHyun-bin/RAPA_Smart_Hospital_AI_Corpus
```

이후 vault repo 위치를 옮긴다면 이 줄을 수정하고 commit & push 하세요.

---

## 7. 첫 배포 트리거

두 가지 방법:

**방법 A — main branch에 push**:
```bash
git push origin main
```

**방법 B — 수동 트리거 (권장: 첫 테스트)**:
1. GitHub repo → **Actions** 탭
2. 좌측 사이드바에서 **"Publish Quartz"** 워크플로우 선택
3. 우측 **"Run workflow"** 버튼 → **Run workflow**

빌드 로그를 보며 각 step이 통과하는지 확인합니다. 평균 2-4분 소요.

---

## 8. 트러블슈팅

### 빌드 실패: "Repository not found" 또는 "Bad credentials"
- **원인**: `CORPUS_VAULT_TOKEN` 미설정 또는 토큰의 `repo` scope 부족
- **해결**: 토큰을 재발급하고 `repo` scope 체크 확인 → GitHub Secrets 재등록

### 빌드 실패: 무결성 체크 단계에서 stop
- **원인**: vault에 frontmatter 누락된 노트가 있거나, 깨진 wikilink, 또는 ID 충돌
- **해결**: 로그에 표시된 파일을 vault에서 수정 → vault repo에 push → 다시 트리거

### 빌드 실패: "npx quartz build" 단계에서 오류
- **원인**: vault content에 Quartz가 파싱 못하는 문법, 또는 plugin 충돌
- **해결**: 로컬에서 `npx quartz build --directory ../Corpus --output public` 으로 재현하여 디버그

### Cloudflare deploy 실패: "Authentication error"
- **원인**: `CLOUDFLARE_API_TOKEN` 권한 부족 (Pages:Edit 누락) 또는 `CLOUDFLARE_ACCOUNT_ID` 오타
- **해결**: API 토큰 재발급 시 권한 다시 확인, Account ID 다시 복사

### Cloudflare deploy 실패: "Project not found"
- **원인**: workflow의 `projectName: rapa-corpus` 와 Cloudflare 콘솔의 프로젝트명 불일치
- **해결**: 정확히 같은 이름으로 맞추기 (대소문자 구분)

### 배포는 성공했는데 페이지가 안 열림
- **원인**: Cloudflare Access 정책이 너무 좁아 본인 이메일도 차단됨
- **해결**: Access policy의 Include 조건 확인, 필요시 본인 이메일 도메인 추가

---

## 9. 일상 운영

셋업 완료 후 일상 워크플로우:

1. vault에 노트 추가/수정
2. `git push` (vault repo)
3. **잠깐** — push만으로는 자동 배포 안 됨 (현재 워크플로우는 Corpus-Site repo의 push에만 반응)
4. Corpus-Site repo에서 **Actions → Publish Quartz → Run workflow** 수동 트리거
5. 또는 Corpus-Site repo에 trivial commit 후 push

> **향후 개선**: vault repo에서 webhook으로 Corpus-Site의 workflow_dispatch를 트리거하면 vault push → 자동 빌드 가능. 별도 셋업 필요.

---

배포에 문제가 있으면 GitHub Actions의 로그를 먼저 확인하세요. 대부분의 실패는 Secrets 미설정 또는 vault 무결성 문제입니다.
