"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim."""

import pandas as pd


def jalankan(silver):
    """Terima Silver, kembalikan tabel agregat awal sementara sebelum tahap Gold penuh."""
    if silver is None or silver.empty:
        return {"ringkasan_seri": pd.DataFrame()}
    ringkasan = (
        silver.groupby(["sumber", "seri_kode", "satuan"], as_index=False)
        .agg(jumlah_baris=("nilai", "count"), rata_rata=("nilai", "mean"))
    )
    return {"ringkasan_seri": ringkasan}


