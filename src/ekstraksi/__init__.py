"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ menjadi DataFrame mentah yang setia pada sumbernya.
"""

from src.ekstraksi.bps import baca_bps
from src.ekstraksi.ilostat import baca_ilostat
from src.ekstraksi.wdi import baca_wdi


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    hasil = {}
    hasil.update(baca_bps())
    hasil.update(baca_ilostat())
    hasil.update(baca_wdi())
    return hasil