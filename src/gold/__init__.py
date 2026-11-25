"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim."""

import pandas as pd

from src.gold.seleksi_gold import pilih_satu_nilai_gold


def jalankan(silver):
    """Terima Silver, jalankan aturan pemilihan satu nilai per sel Gold, dan kembalikan tabel hasil."""
    if silver is None or silver.empty:
        return {"ringkasan_seri": pd.DataFrame()}

    hasil_seleksi = pilih_satu_nilai_gold(silver)
    kandidat = hasil_seleksi["kandidat_gold"]
    ringkasan_aturan = hasil_seleksi["ringkasan_aturan"]

    print(
        "[GOLD - TUGAS #20] Seleksi 1 nilai/sel selesai: "
        f"Silver={ringkasan_aturan['total_silver']} -> Gold={ringkasan_aturan['total_gold']} "
        f"(tersaring periode={ringkasan_aturan['tersaring_periode']}, "
        f"rincian={ringkasan_aturan['tersaring_rincian']}, "
        f"snapshot={ringkasan_aturan['tersaring_snapshot']})"
    )

    ringkasan_seri = (
        kandidat.groupby(["sumber", "seri_kode", "satuan"], as_index=False)
        .agg(jumlah_baris=("nilai", "count"), rata_rata=("nilai", "mean"))
    )

    return {
        "ringkasan_seri": ringkasan_seri,
        "kandidat_gold": kandidat,
        "gold_provinsi": hasil_seleksi["gold_provinsi"],
        "gold_nasional": hasil_seleksi["gold_nasional"],
        "ringkasan_aturan": ringkasan_aturan,
    }