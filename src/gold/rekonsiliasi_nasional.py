
"""Pembentukan tabel nasional Gold dan penanda asal setiap angka."""

from pathlib import Path

import pandas as pd


DIR_GOLD = Path("data/gold")
FILE_OUTPUT = DIR_GOLD / "tabel_nasional_gold.csv"

SERI_NASIONAL = [
    "var1360",
    "var2003",
    "SDG_0552_NOC_RT",
    "SDG_T552_NOC_RT",
    "SG.GEN.PARL.ZS",
    "SP.M18.2024.FE.ZS",
]

ASAL_NASIONAL = {
    "bps": "Baris Indonesia BPS (wilayah_id=9999)",
    "ilostat": "Baris nasional Indonesia ILOSTAT (REF_AREA=IDN)",
    "wdi": "Baris nasional Indonesia WDI (countryiso3code=IDN)",
}


def buat_tabel_nasional_gold(gold_nasional):
    """Membentuk tabel nasional dengan asal dan lineage setiap angka."""

    if gold_nasional is None or gold_nasional.empty:
        raise ValueError("Data Gold nasional kosong.")

    kolom_wajib = [
        "sumber",
        "seri_kode",
        "wilayah_kode",
        "periode",
        "nilai",
        "_berkas_raw",
        "_sha256_raw",
    ]

    kolom_hilang = [
        kolom for kolom in kolom_wajib
        if kolom not in gold_nasional.columns
    ]

    if kolom_hilang:
        raise ValueError(
            f"Kolom Gold nasional tidak lengkap: {kolom_hilang}"
        )

    tabel = gold_nasional.copy()

    tabel["sumber"] = (
        tabel["sumber"].astype(str).str.lower().str.strip()
    )

    tabel = tabel[
        tabel["seri_kode"].isin(SERI_NASIONAL)
    ].copy()

    sumber_tidak_dikenal = (
        set(tabel["sumber"].unique()) - set(ASAL_NASIONAL)
    )

    if sumber_tidak_dikenal:
        raise ValueError(
            f"Sumber nasional belum memiliki keterangan asal: "
            f"{sorted(sumber_tidak_dikenal)}"
        )

    tabel["asal_nasional"] = tabel["sumber"].map(ASAL_NASIONAL)

    kunci = ["periode", "seri_kode"]

    if tabel.duplicated(kunci).any():
        raise ValueError(
            "Ditemukan duplikasi periode dan seri pada Gold nasional."
        )

    seri_tersedia = set(tabel["seri_kode"].unique())
    seri_hilang = set(SERI_NASIONAL) - seri_tersedia

    if seri_hilang:
        raise ValueError(
            f"Seri nasional belum lengkap: {sorted(seri_hilang)}"
        )

    tabel = tabel.sort_values(
        ["periode", "seri_kode"]
    ).reset_index(drop=True)

    DIR_GOLD.mkdir(parents=True, exist_ok=True)

    tabel.to_csv(
        FILE_OUTPUT,
        index=False,
        lineterminator="\n"
    )

    print("\nTabel nasional Gold berhasil dibuat.")
    print(f"Jumlah baris       : {len(tabel)}")
    print(f"Jumlah seri        : {tabel['seri_kode'].nunique()}")
    print(f"Jumlah periode     : {tabel['periode'].nunique()}")
    print(f"Kolom asal         : asal_nasional")
    print(f"Lokasi output      : {FILE_OUTPUT}")

    return tabel