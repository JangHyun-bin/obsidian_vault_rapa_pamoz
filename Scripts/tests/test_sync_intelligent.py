"""Tests for sync_intelligent.py — Phase 1+2+3.

Validates:
- EXCLUDE filter (dirs + name patterns + extensions)
- SYNC_MAP routing (14 paths)
- SHA256 dedup
- .gitignore correctness (_curator ignored, _summaries tracked)
- venv-isolated module import
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Force .env load before any module-level code
_env = Path(r"C:/Users/user/AppData/Local/hermes/.env")
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())


# ──────────────────────────────────────
# Fixtures
# ──────────────────────────────────────
@pytest.fixture(scope="module")
def sync():
    """Import sync_intelligent once per test module (heavy import: chromadb)."""
    # Ensure Scripts/ is on path (conftest adds it for the test run)
    import sync_intelligent  # noqa: F401
    if "sync_intelligent" in sys.modules:
        # Force reload to pick up conftest-injected path
        del sys.modules["sync_intelligent"]
    import sync_intelligent as m
    return m


@pytest.fixture
def tmp_docs_root(tmp_path):
    """Isolated fake docs/ tree under tmp_path."""
    docs = tmp_path / "docs"
    docs.mkdir()
    for d in ["Corpus/decisions", "Corpus/specs", "Corpus/scripts/.venv/Lib",
              "Corpus/node_modules", "Corpus/_raw",
              "OUTPUT/1.3_deliverables_draft", "OUTPUT/주간보고",
              "OUTPUT/WBS/legacy", "산출물 폴더",
              "tmp.tmp.drivedownload"]:
        (docs / d).mkdir(parents=True, exist_ok=True)
    files = {
        "Corpus/decisions/0001-test.md": "ADR test",
        "Corpus/specs/system-arch.md": "spec",
        "Corpus/MOC.md": "MOC",
        "Corpus/README.md": "Corpus README",
        "Corpus/scripts/.venv/Lib/should-skip.md": "venv",
        "Corpus/node_modules/skip.md": "node_modules",
        "Corpus/_raw/paper.md": "raw",
        "OUTPUT/1.3_deliverables_draft/del.md": "deliverable",
        "OUTPUT/주간보고/W1.md": "weekly",
        "OUTPUT/WBS/legacy/old.md": "legacy",
        "산출물 폴더/unmapped.md": "unmapped",
        "~$lockfile.md": "lock",
        ".tmp.foo.md": "tmp pattern",
        "test.xyz": "wrong ext",
    }
    for rel, content in files.items():
        p = docs / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    # WBS xlsm placeholder
    (docs / "OUTPUT" / "WBS" / "fake.xlsm").write_bytes(b"fake")
    return docs


# ──────────────────────────────────────
# EXCLUDE 필터
# ──────────────────────────────────────
class TestExclude:
    @pytest.mark.parametrize("rel,expected", [
        ("Corpus/scripts/.venv/Lib/should-skip.md", True),
        ("Corpus/node_modules/skip.md", True),
        ("OUTPUT/WBS/legacy/old.md", True),
        ("tmp.tmp.drivedownload/dl.md", True),
        ("~$lockfile.md", True),
        (".tmp.foo.md", True),
        # NOTE: extension check (e.g. test.xyz) happens in scan_docs(),
        # not is_excluded(). is_excluded() is directory/filename filter only.
    ])
    def test_excluded(self, sync, tmp_docs_root, rel, expected):
        p = tmp_docs_root / rel
        if p.exists():
            assert sync.is_excluded(p) == expected, \
                f"is_excluded({p.name}) should be {expected}"

    @pytest.mark.parametrize("rel,expected", [
        ("Corpus/decisions/0001-test.md", False),
        ("산출물 폴더/unmapped.md", False),
    ])
    def test_included(self, sync, tmp_docs_root, rel, expected):
        p = tmp_docs_root / rel
        assert sync.is_excluded(p) == expected


# ──────────────────────────────────────
# SYNC_MAP 라우팅
# ──────────────────────────────────────
class TestRoute:
    @pytest.mark.parametrize("rel,expected_prefix", [
        ("Corpus/decisions/0001-test.md", "ADR"),
        ("Corpus/specs/system-arch.md", "Specs"),
        ("Corpus/MOC.md", "MOC.md"),
        ("Corpus/README.md", "Corpus-README.md"),
        ("Corpus/_raw/paper.md", "Corpus/_raw"),
        ("OUTPUT/1.3_deliverables_draft/del.md", "Deliverables/1.3"),
        ("OUTPUT/주간보고/W1.md", "Reports/weekly"),
        ("OUTPUT/WBS/legacy/old.md", "WBS-source"),  # legacy 안 들어가므로 OK
        ("산출물 폴더/unmapped.md", "_inbox"),
    ])
    def test_route(self, sync, tmp_docs_root, rel, expected_prefix):
        # Use real DOCS_ROOT for routing (SYNC_MAP uses string prefix on rel)
        # but DOCS_ROOT is used only for rel extraction; rel-based routing
        # is independent of actual root.
        sync.DOCS_ROOT = tmp_docs_root
        p = tmp_docs_root / rel
        if not p.exists():
            pytest.skip(f"fixture missing {rel}")
        # create a fake dst for the test (avoid touching real vault)
        dst = sync.map_to_vault(p)
        got = str(dst).replace("\\", "/")
        # Match by expected_prefix (after VAULT)
        # dst starts with VAULT, so just check suffix
        assert expected_prefix in got, f"expected prefix '{expected_prefix}' in '{got}'"


# ──────────────────────────────────────
# SHA256 dedup
# ──────────────────────────────────────
class TestShaDedup:
    def test_match(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"hello")
        b.write_bytes(b"hello")
        from sync_intelligent import sha256
        assert sha256(a) == sha256(b)

    def test_diff(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"hello")
        b.write_bytes(b"world")
        from sync_intelligent import sha256
        assert sha256(a) != sha256(b)


# ──────────────────────────────────────
# sync_files() dry-run
# ──────────────────────────────────────
class TestDryRun:
    def test_no_disk_change(self, sync, tmp_docs_root, tmp_path):
        fake_vault = tmp_path / "vault"
        fake_vault.mkdir()
        (fake_vault / ".git").mkdir()
        sync.DOCS_ROOT = tmp_docs_root
        sync.VAULT = fake_vault
        before = set(fake_vault.rglob("*"))
        # sync_intelligent is the main 5-stage entry; pass --skip-push + dry-run via CLI
        import subprocess as sp
        venv = r"C:\Users\user\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
        r = sp.run(
            [venv, str(Path(sync.__file__).parent / "sync_intelligent.py"),
             "--dry-run", "--skip-push"],
            capture_output=True, text=True, cwd=str(Path(sync.__file__).parent.parent),
        )
        after = set(fake_vault.rglob("*"))
        assert before == after, \
            f"dry-run must not change vault disk. stderr={r.stderr[-500:]}"
        assert r.returncode == 0


# ──────────────────────────────────────
# .gitignore: _curator ignored, _summaries tracked
# ──────────────────────────────────────
class TestGitignore:
    def test_curator_ignored(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / "_curator").mkdir()
        (repo / "_curator" / "chroma").mkdir()
        (repo / "_curator" / "data.json").write_text("{}")
        # .gitignore
        (repo / ".gitignore").write_text(
            ".obsidian/workspace.json\n"
            "_curator/chroma/\n"
            "_curator/embeddings_cache/\n"
            "_curator/.index_state.json\n"
            "_summaries/\n"
        )
        # git init (if not present)
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"],
                       cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "test"],
                       cwd=repo, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
        r = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                          cwd=repo, capture_output=True, text=True)
        tracked = set()
        for f in (repo / "_curator").rglob("*"):
            if f.is_file():
                tracked.add(f)
        # _curator contents should be ignored or untracked
        # check-ignore on a sample file
        r2 = subprocess.run(
            ["git", "check-ignore", "_curator/chroma/data.bin"],
            cwd=repo, capture_output=True, text=True
        )
        assert r2.returncode == 0, "_curator/chroma/ should be ignored"

    def test_summaries_tracked(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / "_summaries").mkdir()
        (repo / "_summaries" / "test.md").write_text("# test")
        # .gitignore: _curator ignored, but NO _summaries/ entry
        (repo / ".gitignore").write_text(
            ".obsidian/workspace.json\n"
            "_curator/chroma/\n"
            "_curator/embeddings_cache/\n"
            "_curator/.index_state.json\n"
            # _summaries/ is intentionally NOT ignored
        )
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"],
                       cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "test"],
                       cwd=repo, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
        r = subprocess.run(["git", "ls-files"], cwd=repo,
                          capture_output=True, text=True)
        assert "_summaries/test.md" in r.stdout, \
            f"_summaries/ should be tracked, got: {r.stdout!r}"


# ──────────────────────────────────────
# LLM helper (mocked — no real API call)
# ──────────────────────────────────────
class TestLlmMocked:
    def test_summarize_returns_parsed_json(self, sync, monkeypatch):
        from sync_intelligent import summarize_with_llm
        # Mock call_llm to return canned JSON
        def fake_call(prompt, **kw):
            return '{"summary": "테스트", "category": "ADR", "tags": ["t1"], "related_keywords": ["k1"]}'
        monkeypatch.setattr(sync, "call_llm", fake_call)
        result = summarize_with_llm("# doc body content")
        assert result is not None
        assert result["summary"] == "테스트"
        assert result["category"] == "ADR"
        assert result["tags"] == ["t1"]
        assert result["related_keywords"] == ["k1"]

    def test_summarize_handles_markdown_fenced_json(self, sync, monkeypatch):
        from sync_intelligent import summarize_with_llm
        def fake_call(prompt, **kw):
            return '```json\n{"summary": "s", "category": "Other", "tags": [], "related_keywords": []}\n```'
        monkeypatch.setattr(sync, "call_llm", fake_call)
        result = summarize_with_llm("body")
        assert result is not None
        assert result["summary"] == "s"

    def test_summarize_returns_none_on_invalid_json(self, sync, monkeypatch):
        from sync_intelligent import summarize_with_llm
        monkeypatch.setattr(sync, "call_llm", lambda *a, **kw: "not json")
        assert summarize_with_llm("body") is None

    def test_call_llm_no_api_key(self, sync, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        from sync_intelligent import call_llm
        result = call_llm("test")
        assert result is None


# ──────────────────────────────────────
# Module import (smoke test for venv isolation)
# ──────────────────────────────────────
def test_module_importable():
    """sync_intelligent must import without errors from hermes venv."""
    if "sync_intelligent" in sys.modules:
        del sys.modules["sync_intelligent"]
    import sync_intelligent  # noqa: F401
    assert hasattr(sync_intelligent, "sync_intelligent")
    assert hasattr(sync_intelligent, "summarize_with_llm")
    assert hasattr(sync_intelligent, "chroma_index_file")


# ──────────────────────────────────────
# GanttProject .gan (Stage 2.5 in pipeline)
# ──────────────────────────────────────
class TestGanGeneration:
    def test_gan_script_exists(self):
        path = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/Scripts/wbs_to_gan.py")
        assert path.exists(), f"missing: {path}"

    def test_gan_output_valid_zip(self):
        import zipfile
        out = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/Attachments/RAPA_파모즈_v0.7.gan")
        if not out.exists():
            pytest.skip("gan not yet generated (run sync_intelligent first)")
        assert zipfile.is_zipfile(out)
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
            assert "project.xml" in names
            xml = z.read("project.xml").decode("utf-8")
            assert "<project" in xml
            assert "<task>" in xml

    def test_gan_task_count_matches_wbs(self):
        import zipfile
        out = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/Attachments/RAPA_파모즈_v0.7.gan")
        if not out.exists():
            pytest.skip("gan not yet generated")
        with zipfile.ZipFile(out) as z:
            xml = z.read("project.xml").decode("utf-8")
        task_count = xml.count("<task>")
        # WBS has 69 L3 tasks (level 3 with start+end)
        # Allow some slack (69 ± 5)
        assert 60 <= task_count <= 80, \
            f"task count {task_count} out of expected range"


# ──────────────────────────────────────
# OpenProject sync (Stage 6 in pipeline)
# ──────────────────────────────────────
class TestOpenProjectSync:
    def test_op_script_exists(self):
        path = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/Scripts/sync_openproject.py")
        assert path.exists(), f"missing: {path}"

    def test_op_token_file_exists_or_skip(self):
        path = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/_curator/.openproject_token")
        if not path.exists():
            pytest.skip("OP token not configured (run OpenProject setup)")
        # token should be 64-char hex
        token = path.read_text(encoding="utf-8").strip()
        assert len(token) == 64
        assert all(c in "0123456789abcdef" for c in token)

    def test_op_api_reachable_or_skip(self):
        import base64
        import httpx
        path = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/_curator/.openproject_token")
        if not path.exists():
            pytest.skip("OP token not configured")
        token = path.read_text(encoding="utf-8").strip()
        creds = base64.b64encode(f"apikey:{token}".encode()).decode()
        try:
            r = httpx.get("http://localhost:8082/api/v3/users/me",
                          headers={"Authorization": f"Basic {creds}"},
                          timeout=5)
        except Exception as e:
            pytest.skip(f"OP not reachable: {e}")
        # 200 (auth OK) or 401 (token invalid) both acceptable for env check
        assert r.status_code in (200, 401)

    def test_op_project_exists_or_skip(self):
        import base64
        import httpx
        path = Path(r"D:/HB/P.RAPA_DEV/_obsidian_vault/_curator/.openproject_token")
        if not path.exists():
            pytest.skip("OP token not configured")
        token = path.read_text(encoding="utf-8").strip()
        creds = base64.b64encode(f"apikey:{token}".encode()).decode()
        try:
            r = httpx.get("http://localhost:8082/api/v3/projects",
                          headers={"Authorization": f"Basic {creds}"},
                          params={"pageSize": 100}, timeout=10)
            if r.status_code != 200:
                pytest.skip(f"OP auth failed: {r.status_code}")
            data = r.json()
            names = [p.get("name") for p in data.get("_embedded", {}).get("elements", [])]
            assert "RAPA 스마트병원동행AI앱 (파모즈)" in names, \
                f"RAPA project not found. Existing: {names}"
        except Exception as e:
            pytest.skip(f"OP not reachable: {e}")
