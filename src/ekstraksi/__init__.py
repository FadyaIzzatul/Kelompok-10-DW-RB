
"""
Tahap 1 — Ekstraksi data mentah.

Menggabungkan hasil pembacaan BPS, WDI, dan ILOSTAT
menjadi satu DataFrame mentah dengan informasi lineage.
"""

import pandas as pd

from .bps import baca_bps
from .wdi import baca_wdi
from .ilostat import baca_ilostat


def jalankan():
    """Gabungkan seluruh hasil pembacaan menjadi satu tabel mentah."""

    hasil_bps = baca_bps()
    hasil_wdi = baca_wdi()
    hasil_ilostat = baca_ilostat()

    seluruh_tabel = []

    for sumber, hasil in [
        ("BPS", hasil_bps),
        ("WDI", hasil_wdi),
        ("ILOSTAT", hasil_ilostat),
    ]:
        for nama, df in hasil.items():
            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"Hasil {sumber} - {nama} bukan DataFrame."
                )

            if "_berkas_raw" not in df.columns:
                raise ValueError(
                    f"Kolom _berkas_raw tidak ditemukan pada {sumber} - {nama}."
                )

            if "_sha256_raw" not in df.columns:
                raise ValueError(
                    f"Kolom _sha256_raw tidak ditemukan pada {sumber} - {nama}."
                )

            seluruh_tabel.append(df)

    if not seluruh_tabel:
        raise ValueError("Tidak ada data hasil ekstraksi.")

    tabel_mentah = pd.concat(
        seluruh_tabel,
        ignore_index=True,
        sort=False
    )

    assert "_berkas_raw" in tabel_mentah.columns
    assert "_sha256_raw" in tabel_mentah.columns

    print(f"Total tabel sumber: {len(seluruh_tabel)}")
    print(f"Total baris mentah: {len(tabel_mentah)}")
    print("Lineage: tersedia")

    return tabel_mentah

