"""Tahap 1 — Orkestrasi ekstraksi Kasus 10."""

from src.ekstraksi.bps import baca_bps
from src.ekstraksi.ilostat import baca_ilostat
from src.ekstraksi.wdi import baca_wdi


def jalankan():
    """Mengembalikan hasil ekstraksi berdasarkan sumber data."""

    hasil = {
        "bps": baca_bps(),
        "ilostat": baca_ilostat(),
        "wdi": baca_wdi(),
    }

    return hasil