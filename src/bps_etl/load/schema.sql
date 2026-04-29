-- SQLite schema for ETL BPS socioeconomic analytics.
-- Fase 2 design artifact. Implemented by load layer in Fase 5.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_indikator (
    var_id INTEGER PRIMARY KEY,
    indicator_key TEXT NOT NULL UNIQUE,
    nama_indikator TEXT NOT NULL,
    unit TEXT,
    subject TEXT,
    theme TEXT,
    definisi TEXT,
    catatan TEXT,
    decimal_places INTEGER,
    source_model TEXT NOT NULL DEFAULT 'data.var',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (var_id, indicator_key)
);

CREATE TABLE IF NOT EXISTS dim_wilayah (
    kode_wilayah TEXT PRIMARY KEY,
    nama_wilayah TEXT NOT NULL,
    level_wilayah TEXT NOT NULL DEFAULT 'unknown',
    group_ver_id TEXT,
    group_ver_name TEXT,
    source_model TEXT NOT NULL DEFAULT 'data.vervar',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_waktu (
    th_id INTEGER PRIMARY KEY,
    tahun INTEGER NOT NULL UNIQUE,
    periode_label TEXT NOT NULL,
    source_model TEXT NOT NULL DEFAULT 'th',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (tahun BETWEEN 1990 AND 2035)
);

CREATE TABLE IF NOT EXISTS dim_turvar (
    turvar_id TEXT PRIMARY KEY,
    turvar_label TEXT NOT NULL,
    group_turvar_id TEXT,
    group_turvar_name TEXT,
    source_model TEXT NOT NULL DEFAULT 'turvar',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_turtahun (
    turth_id TEXT PRIMARY KEY,
    turth_label TEXT NOT NULL,
    group_turth_id TEXT,
    group_turth_name TEXT,
    source_model TEXT NOT NULL DEFAULT 'turth',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_statistik (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_key TEXT NOT NULL,
    var_id INTEGER NOT NULL,
    kode_wilayah TEXT NOT NULL,
    th_id INTEGER NOT NULL,
    turvar_id TEXT NOT NULL DEFAULT '0',
    turth_id TEXT NOT NULL DEFAULT '0',
    data_key TEXT NOT NULL,
    source_domain TEXT NOT NULL DEFAULT '0000',
    nilai REAL NOT NULL,
    last_update TEXT,
    loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    run_id TEXT,
    FOREIGN KEY (var_id) REFERENCES dim_indikator(var_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (var_id, indicator_key) REFERENCES dim_indikator(var_id, indicator_key) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (kode_wilayah) REFERENCES dim_wilayah(kode_wilayah) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (th_id) REFERENCES dim_waktu(th_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (turvar_id) REFERENCES dim_turvar(turvar_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (turth_id) REFERENCES dim_turtahun(turth_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (run_id) REFERENCES etl_run_log(run_id) ON UPDATE CASCADE ON DELETE SET NULL,
    UNIQUE (data_key),
    UNIQUE (var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain)
);

CREATE TABLE IF NOT EXISTS raw_api_snapshot (
    snapshot_id TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    var_id INTEGER,
    th_id INTEGER,
    source_domain TEXT NOT NULL DEFAULT '0000',
    artifact_path TEXT NOT NULL,
    artifact_sha256 TEXT,
    row_count INTEGER NOT NULL DEFAULT 0 CHECK (row_count >= 0),
    captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    run_id TEXT,
    FOREIGN KEY (run_id) REFERENCES etl_run_log(run_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id TEXT PRIMARY KEY,
    phase TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed')),
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    indicator_count INTEGER NOT NULL DEFAULT 0 CHECK (indicator_count >= 0),
    raw_snapshot_count INTEGER NOT NULL DEFAULT 0 CHECK (raw_snapshot_count >= 0),
    fact_row_count INTEGER NOT NULL DEFAULT 0 CHECK (fact_row_count >= 0),
    error_message TEXT,
    source_git_commit TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_statistik_var_year ON fact_statistik (var_id, th_id);
CREATE INDEX IF NOT EXISTS idx_fact_statistik_wilayah_year ON fact_statistik (kode_wilayah, th_id);
CREATE INDEX IF NOT EXISTS idx_fact_statistik_indicator ON fact_statistik (indicator_key);
CREATE INDEX IF NOT EXISTS idx_raw_api_snapshot_lookup ON raw_api_snapshot (model, var_id, th_id);
