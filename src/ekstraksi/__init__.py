
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
    """Mengembalikan hasil ekstraksi berdasarkan sumber data."""

    hasil_bps = baca_bps()
    hasil_wdi = baca_wdi()
    hasil_ilostat = baca_ilostat()

    hasil = {
        "bps": hasil_bps,
        "wdi": hasil_wdi,
        "ilostat": hasil_ilostat,
    }

    total_tabel = 0
    total_baris = 0

    for sumber, tabel in hasil.items():
        for nama, df in tabel.items():

            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"Hasil {sumber} - {nama} bukan DataFrame."
                )

            if "_berkas_raw" not in df.columns:
                raise ValueError(
                    f"Kolom _berkas_raw tidak ditemukan "
                    f"pada {sumber} - {nama}."
                )

            if "_sha256_raw" not in df.columns:
                raise ValueError(
                    f"Kolom _sha256_raw tidak ditemukan "
                    f"pada {sumber} - {nama}."
                )

            total_tabel += 1
            total_baris += len(df)

    print(f"Total tabel sumber: {total_tabel}")
    print(f"Total baris mentah: {total_baris}")
    print("Lineage: tersedia")

    return hasil
