"""Muat satu snapshot Silver Parquet ke tabel silver di SQLite."""

import argparse
from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd

from src.common.skema import KOLOM, periksa_silver
from src.silver import OUTPUT_SILVER

DDL = Path(__file__).with_name("silver.sql")
KOLOM_SQL = (*KOLOM, "obs_status", "definisi_indikator")


def muat_silver(parquet, basis_data):
    """Ganti isi tabel secara atomik dan kembalikan jumlah observasi."""
    silver = pd.read_parquet(parquet)
    salah = periksa_silver(silver)
    if salah:
        raise ValueError("Silver tidak valid\n" + "\n".join(salah))

    baris = silver.reindex(columns=KOLOM_SQL).astype(object)
    baris = baris.where(baris.notna(), None)
    kolom = ", ".join(KOLOM_SQL)
    parameter = ", ".join("?" for _ in KOLOM_SQL)
    ddl = DDL.read_text(encoding="utf-8")

    with closing(sqlite3.connect(basis_data)) as koneksi, koneksi:
        koneksi.execute("BEGIN IMMEDIATE")
        koneksi.execute(ddl)
        koneksi.execute("DELETE FROM silver")
        koneksi.executemany(
            f"INSERT INTO silver ({kolom}) VALUES ({parameter})",
            baris.itertuples(index=False, name=None),
        )
    return len(baris)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, default=OUTPUT_SILVER)
    parser.add_argument("--basis-data", type=Path, default=Path("data/silver/silver.sqlite3"))
    argumen = parser.parse_args()
    try:
        jumlah = muat_silver(argumen.parquet, argumen.basis_data)
    except (ValueError, OSError, sqlite3.Error) as galat:
        parser.exit(1, f"Gagal memuat Silver. {galat}\n")
    print(f"{jumlah} baris Silver dimuat ke {argumen.basis_data}")


if __name__ == "__main__":
    main()
