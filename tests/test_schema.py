from __future__ import annotations

import sqlite3

import pytest

from bps_etl.load.models import FACT_UNIQUE_GRAIN, TARGET_TABLES, load_schema_sql


def make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(load_schema_sql())
    return conn


def table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def index_columns(conn: sqlite3.Connection, index_name: str) -> tuple[str, ...]:
    rows = conn.execute(f"PRAGMA index_info({index_name})").fetchall()
    return tuple(row[2] for row in rows)


def test_schema_creates_all_target_tables():
    conn = make_connection()
    assert set(TARGET_TABLES).issubset(table_names(conn))


def test_fact_table_has_foreign_keys_to_dimensions_and_run_log():
    conn = make_connection()
    fk_rows = conn.execute("PRAGMA foreign_key_list(fact_statistik)").fetchall()
    fk_tables = {row[2] for row in fk_rows}
    assert {"dim_indikator", "dim_wilayah", "dim_waktu", "dim_turvar", "dim_turtahun", "etl_run_log"}.issubset(fk_tables)


def test_raw_snapshot_has_run_log_foreign_key():
    conn = make_connection()
    fk_rows = conn.execute("PRAGMA foreign_key_list(raw_api_snapshot)").fetchall()
    assert {row[2] for row in fk_rows} == {"etl_run_log"}


def test_fact_table_has_unique_grain_index():
    conn = make_connection()
    indexes = conn.execute("PRAGMA index_list(fact_statistik)").fetchall()
    unique_indexes = [row[1] for row in indexes if row[2] == 1]
    unique_column_sets = {index_columns(conn, index_name) for index_name in unique_indexes}

    assert FACT_UNIQUE_GRAIN in unique_column_sets
    assert ("data_key",) in unique_column_sets


def seed_dimensions(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT INTO dim_indikator (var_id, indicator_key, nama_indikator, unit, subject, theme)
        VALUES (192, 'poverty_rate', 'Persentase Penduduk Miskin', 'Persen', 'Kemiskinan', 'Kemiskinan')
        """
    )
    conn.execute(
        """
        INSERT INTO dim_wilayah (kode_wilayah, nama_wilayah, level_wilayah)
        VALUES ('1100', 'ACEH', 'provinsi')
        """
    )
    conn.execute(
        """
        INSERT INTO dim_waktu (th_id, tahun, periode_label)
        VALUES (123, 2023, '2023')
        """
    )
    conn.execute(
        """
        INSERT INTO dim_turvar (turvar_id, turvar_label)
        VALUES ('434', 'Jumlah')
        """
    )
    conn.execute(
        """
        INSERT INTO dim_turtahun (turth_id, turth_label)
        VALUES ('63', 'Tahunan')
        """
    )


def insert_sample_fact(
    conn: sqlite3.Connection,
    *,
    data_key: str = "110019243412363",
    kode_wilayah: str = "1100",
    indicator_key: str = "poverty_rate",
) -> None:
    conn.execute(
        """
        INSERT INTO fact_statistik (
            indicator_key, var_id, kode_wilayah, th_id, turvar_id, turth_id,
            data_key, source_domain, nilai, last_update
        )
        VALUES (?, 192, ?, 123, '434', '63', ?, '0000', 14.45, '2026-04-29')
        """,
        (indicator_key, kode_wilayah, data_key),
    )


def test_schema_accepts_valid_sample_fact_row():
    conn = make_connection()
    seed_dimensions(conn)
    insert_sample_fact(conn)

    count = conn.execute("SELECT COUNT(*) FROM fact_statistik").fetchone()[0]
    assert count == 1


def test_schema_rejects_duplicate_fact_grain():
    conn = make_connection()
    seed_dimensions(conn)
    insert_sample_fact(conn, data_key="110019243412363")

    with pytest.raises(sqlite3.IntegrityError):
        insert_sample_fact(conn, data_key="different-data-key-same-grain")


def test_schema_rejects_duplicate_data_key():
    conn = make_connection()
    seed_dimensions(conn)
    conn.execute("INSERT INTO dim_wilayah (kode_wilayah, nama_wilayah, level_wilayah) VALUES ('1200', 'SUMATERA UTARA', 'provinsi')")
    insert_sample_fact(conn, data_key="same-data-key", kode_wilayah="1100")

    with pytest.raises(sqlite3.IntegrityError):
        insert_sample_fact(conn, data_key="same-data-key", kode_wilayah="1200")


def test_schema_rejects_inconsistent_indicator_key_for_var_id():
    conn = make_connection()
    seed_dimensions(conn)

    with pytest.raises(sqlite3.IntegrityError):
        insert_sample_fact(conn, data_key="bad-key", indicator_key="wrong_indicator_key")


def test_schema_rejects_fact_without_dimension_row():
    conn = make_connection()
    with pytest.raises(sqlite3.IntegrityError):
        insert_sample_fact(conn)


def test_schema_rejects_negative_audit_counters():
    conn = make_connection()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO etl_run_log (run_id, phase, status, indicator_count)
            VALUES ('run-negative', 'phase-2-test', 'success', -1)
            """
        )
