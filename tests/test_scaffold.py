from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_required_scaffold_files_exist():
    required = [
        "AGENTS.md",
        "README.md",
        ".gitignore",
        ".env.example",
        "docs/project/project-control.md",
        "docs/project/phase-gates.md",
        "docs/project/workflow.md",
        "prompts/LECTURER_REVIEWER.md",
        "dashboard/index.html",
        "dashboard/styles/tokens.css",
        "dashboard/styles/base.css",
        "dashboard/styles/layout.css",
        "dashboard/styles/components.css",
        "dashboard/styles/visualizations.css",
        "dashboard/scripts/main.js",
        "dashboard/scripts/data-loader.js",
        "dashboard/scripts/state.js",
        "dashboard/scripts/formatters.js",
        "dashboard/scripts/filters.js",
        "dashboard/scripts/charts.js",
        "dashboard/scripts/table.js",
        "dashboard/scripts/narrative.js",
        "dashboard/data/dashboard-data.json",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing


def test_dashboard_json_is_fase_6_real_data_contract():
    data = json.loads((ROOT / "dashboard/data/dashboard-data.json").read_text(encoding="utf-8"))
    assert data["summary"]["record_count"] == 4292
    assert data["summary"]["indicator_count"] == 6
    assert data["summary"]["region_count"] == 579
    assert data["summary"]["year_count"] == 4
    assert data["charts"]["trend"]
    assert data["charts"]["regional_comparison"]
    assert data["series"]["trend"]
    assert data["rankings"]["top"]
    assert data["rankings"]["bottom"]
    assert data["rankings"]["change"]
    assert len(data["table_rows"]) == 4292
    serialized = json.dumps(data, ensure_ascii=False).lower()
    assert "lorem" not in serialized
    assert "placeholder chart" not in serialized
    assert data["quality"]["no_dummy_data"] is True
    assert data["project"]["current_phase"] == "6.1 — Data Expansion"
    assert data["project"]["review"]["verdict"] == "APPROVED"
    assert data["project"]["review"]["score"] == 92
    assert data["project"]["review"]["file"] == "docs/reviews/REVIEW_phase6_1_data_expansion.md"
    assert data["project"]["review"]["previous"]["score"] == 91
    assert data["design_metrics"]["valid_indicators"] == 6
    assert data["design_metrics"]["api_probe_rows"] == 24
    assert data["design_metrics"]["normalized_sample_records"] == 4292
    assert data["design_metrics"]["schema_validation_tests"] == 10
    assert data["design_metrics"]["extract_tests"] == 8
    assert data["design_metrics"]["transform_tests"] == 5
    assert data["design_metrics"]["extract_targets"] == 24
    assert data["design_metrics"]["total_extract_snapshots"] == 54
    assert data["design_metrics"]["total_raw_rows"] == 5744
    assert data["design_metrics"]["transform_fact_preview_rows"] == 4292
    assert data["design_metrics"]["transform_quality_gate"] == "passed"
    assert data["design_metrics"]["transform_unmatched_count"] == 0
    assert data["design_metrics"]["load_fact_rows"] == 4292
    assert data["design_metrics"]["load_dim_wilayah_rows"] == 579
    assert data["design_metrics"]["load_raw_snapshot_rows"] == 54
    assert data["design_metrics"]["load_run_log_rows"] >= 1
    assert data["design_metrics"]["dashboard_chart_series"] == 6
    assert data["design_metrics"]["dashboard_table_rows"] == 4292
    assert data["schema"]["fact_grain"] == "var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain"


def test_gitignore_blocks_secrets_and_database():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "*.db" in text
    assert "data/raw/" in text
