# OpenProject API Token 발급 가이드

## URL
http://localhost:8082

## 발급 단계 (스크린샷 가이드)

1. **브라우저 열기**: http://localhost:8082
2. **로그인**: admin 계정 (초기 admin/비번은 OpenProject 첫 실행 시 설정한 것)
3. **우상단 프로필 아이콘 클릭** → **My page** 또는 **Account settings**
4. **좌측 메뉴 → Access tokens** 클릭
5. **"Add"** 또는 **"API token"** 버튼 클릭
6. **Token name**: `rapa-pamoz-vault-sync` (식별용)
7. **Scopes**: 기본값 (Read + Write)
8. **"Create"** 클릭
9. **생성된 token 복사** (한 번만 보임, 분실 시 재발급)

## Token을 알려주세요
아래 명령으로 token만 회신:

```bash
# 또는 직접 입력 (vault에 저장하지 마세요)
# 예시: abcd1234efgh5678ijkl9012mnop3456qrst
```

저는 token을:
- vault `_curator/.openproject_token` 에 저장 (gitignore, 로컬만)
- `sync_intelligent.py`에 stage 6 추가
- OpenProject RAPA 프로젝트 자동 생성 + WBS 98 task import

## 안전
- Token은 절대 GitHub에 push 안 됨 (`.gitignore`에 `_curator/` 추가됨)
- 1회용 (분실 시 regenerate)
- 권한 최소화 (Write only, Admin X)
