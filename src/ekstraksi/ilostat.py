
"""
Pembaca data ILOSTAT Kasus 10 (SDG 5).

Membaca dua CSV observasi, dua JSON DSD,
dan satu JSON metadata dataflow.

Tidak melakukan pembersihan data dan tidak
menggabungkan kedua definisi seri.
"""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


DASAR_ILO = Path("ilostat/2026-10-20")

SERI = {
    "SDG_0552_NOC_RT": {
        "csv": "DF_SDG_0552_NOC_RT.csv",
        "dsd": "SDG_0552_NOC_RT.json",
        "dataflow": "DF_SDG_0552_NOC_RT",
    },
    "SDG_T552_NOC_RT": {
        "csv": "DF_SDG_T552_NOC_RT.csv",
        "dsd": "SDG_T552_NOC_RT.json",
        "dataflow": "DF_SDG_T552_NOC_RT",
    },
}


def _baca_json(berkas):
    jalur = RAW / berkas

    with jalur.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _tempel_lineage(df, berkas):
    df["_berkas_raw"] = berkas.as_posix()
    df["_sha256_raw"] = sha256_raw(berkas.as_posix())

    return df


def _baca_csv(nama_berkas):
    berkas = DASAR_ILO / "data" / nama_berkas

    df = pd.read_csv(
        RAW / berkas,
        encoding="utf-8-sig",
        sep=",",
        decimal=".",
        keep_default_na=False,
        dtype=str,
    )

    if "OBS_STATUS" not in df.columns:
        raise ValueError(
            f"Kolom OBS_STATUS tidak ditemukan: {berkas}"
        )

    return _tempel_lineage(df, berkas)


def _baca_dsd(nama_berkas):
    berkas = DASAR_ILO / "dsd" / nama_berkas
    isi = _baca_json(berkas)

    struktur = isi["data"]["dataStructures"]

    if not struktur:
        raise ValueError(
            f"Struktur DSD kosong: {berkas}"
        )

    df = pd.DataFrame(struktur)

    return _tempel_lineage(df, berkas)


def _baca_metadata():
    berkas = DASAR_ILO / "metadata" / "dataflow.json"
    isi = _baca_json(berkas)

    semua_dataflow = isi["data"]["dataflows"]

    id_target = {
        informasi["dataflow"]
        for informasi in SERI.values()
    }

    dataflow_terpilih = [
        item
        for item in semua_dataflow
        if item.get("id") in id_target
    ]

    if len(dataflow_terpilih) != 2:
        raise ValueError(
            "Jumlah metadata dataflow tidak sesuai. "
            f"Ditemukan {len(dataflow_terpilih)}, seharusnya 2."
        )

    df = pd.DataFrame(dataflow_terpilih)

    return _tempel_lineage(df, berkas)


def baca_ilostat():
    """Membaca lima berkas ILOSTAT secara terpisah."""

    hasil = {}

    for nama_seri, informasi in SERI.items():

        hasil[f"{nama_seri}_data"] = _baca_csv(
            informasi["csv"]
        )

        hasil[f"{nama_seri}_dsd"] = _baca_dsd(
            informasi["dsd"]
        )

    hasil["metadata_dataflow"] = _baca_metadata()

    return hasil


if __name__ == "__main__":
    hasil = baca_ilostat()

    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")

        assert "_berkas_raw" in df.columns
        assert "_sha256_raw" in df.columns

    for nama_seri in SERI:
        tabel = hasil[f"{nama_seri}_data"]

        assert "OBS_STATUS" in tabel.columns

    print("\nSeluruh 5 berkas ILOSTAT berhasil dibaca.")
    print("OBS_STATUS tetap dipertahankan.")
    print("Lineage tersedia pada seluruh tabel.")
