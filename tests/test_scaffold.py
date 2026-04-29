from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_required_scaffold_files_exist():
    required = [
        "AGENTS.md",
        "README.md",
        ".gitignore",
        ".env.example",
        "docs/project-control.md",
        "docs/phase-gates.md",
        "docs/workflow.md",
        "prompts/LECTURER_REVIEWER.md",
        "dashboard/index.html",
        "dashboard/app.js",
        "dashboard/data/dashboard-data.json",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing


def test_dashboard_json_is_empty_state_not_fake_data():
    data = json.loads((ROOT / "dashboard/data/dashboard-data.json").read_text(encoding="utf-8"))
    assert data["summary"]["record_count"] == 0
    assert data["charts"]["trend"] == []
    assert data["charts"]["regional_comparison"] == []
    assert "dummy" not in json.dumps(data, ensure_ascii=False).lower()


def test_gitignore_blocks_secrets_and_database():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "*.db" in text
    assert "data/raw/" in text
