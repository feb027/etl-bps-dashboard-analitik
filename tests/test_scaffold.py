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
    assert data["summary"]["record_count"] == 2490
    assert data["summary"]["indicator_count"] == 4
    assert data["summary"]["region_count"] == 553
    assert data["summary"]["year_count"] == 3
    assert data["charts"]["trend"] == []
    assert data["charts"]["regional_comparison"] == []
    assert "dummy" not in json.dumps(data, ensure_ascii=False).lower()
    assert data["project"]["current_phase"] == "5 — Load Layer"
    assert data["project"]["review"]["verdict"] == "APPROVED"
    assert data["project"]["review"]["score"] == 92
    assert data["design_metrics"]["valid_indicators"] == 4
    assert data["design_metrics"]["schema_validation_tests"] == 10
    assert data["design_metrics"]["extract_tests"] == 8
    assert data["design_metrics"]["transform_tests"] == 5
    assert data["design_metrics"]["extract_targets"] == 12
    assert data["design_metrics"]["total_extract_snapshots"] == 32
    assert data["design_metrics"]["total_raw_rows"] == 3642
    assert data["design_metrics"]["transform_fact_preview_rows"] == 2490
    assert data["design_metrics"]["transform_quality_gate"] == "passed"
    assert data["design_metrics"]["transform_unmatched_count"] == 0
    assert data["design_metrics"]["load_fact_rows"] == 2490
    assert data["design_metrics"]["load_dim_wilayah_rows"] == 553
    assert data["design_metrics"]["load_raw_snapshot_rows"] == 32
    assert data["design_metrics"]["load_run_log_rows"] == 1
    assert data["schema"]["fact_grain"] == "var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain"


def test_gitignore_blocks_secrets_and_database():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "*.db" in text
    assert "data/raw/" in text
