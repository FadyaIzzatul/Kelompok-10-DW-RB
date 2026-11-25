"""Tahap 4–6 — Pembentukan dan penyimpanan panel Gold."""

from pathlib import Path

import pandas as pd

from src.gold.seleksi_gold import pilih_satu_nilai_gold


DIR_GOLD = Path("data/gold")


def jalankan(silver):
    """Membentuk panel Gold dan menyimpan hasilnya ke Parquet."""

    if silver is None or silver.empty:
        return {"ringkasan_seri": pd.DataFrame()}

    # 1. Seleksi data Silver
    hasil_seleksi = pilih_satu_nilai_gold(silver)

    kandidat = hasil_seleksi["kandidat_gold"]
    gold_provinsi = hasil_seleksi["gold_provinsi"]
    gold_nasional = hasil_seleksi["gold_nasional"]
    ringkasan_aturan = hasil_seleksi["ringkasan_aturan"]

    # 2. Membuat direktori Gold
    DIR_GOLD.mkdir(parents=True, exist_ok=True)

    # 3. Menyimpan hasil panel ke Parquet
    kandidat.to_parquet(
        DIR_GOLD / "panel_gold.parquet",
        index=False
    )

    gold_provinsi.to_parquet(
        DIR_GOLD / "panel_provinsi.parquet",
        index=False
    )

    gold_nasional.to_parquet(
        DIR_GOLD / "panel_nasional.parquet",
        index=False
    )

    # 4. Membuat ringkasan seri
    ringkasan_seri = (
        kandidat.groupby(
            ["sumber", "seri_kode", "satuan"],
            as_index=False
        )
        .agg(
            jumlah_baris=("nilai", "count"),
            rata_rata=("nilai", "mean")
        )
    )

    # 5. Menampilkan hasil
    print("\nPembentukan Gold berhasil.")
    print(f"Jumlah baris Gold     : {len(kandidat)}")
    print(f"Panel provinsi        : {len(gold_provinsi)}")
    print(f"Panel nasional        : {len(gold_nasional)}")
    print(f"Jumlah seri           : {kandidat['seri_kode'].nunique()}")
    print(f"Lokasi output         : {DIR_GOLD}")

    return {
        "ringkasan_seri": ringkasan_seri,
        "kandidat_gold": kandidat,
        "gold_provinsi": gold_provinsi,
        "gold_nasional": gold_nasional,
        "ringkasan_aturan": ringkasan_aturan,
    }