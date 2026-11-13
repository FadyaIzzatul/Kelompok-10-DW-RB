
"""
Pembaca data BPS Kasus 10 (SDG 5).

Membaca dua CSV dan dua JSON BPS menjadi tabel panjang.
Tidak melakukan pembersihan atau perubahan nilai data.
"""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


# Lokasi berkas mentah BPS
DASAR_BPS = Path("bps/2026-10-20")

# Kolom hasil ekstraksi
KOLOM = [
    "var_id",
    "wilayah_id",
    "wilayah",
    "turvar_id",
    "turvar",
    "tahun_id",
    "tahun",
    "periode_id",
    "periode",
    "nilai",
    "satuan",
]


def _tempel_lineage(df, berkas):
    """Menambahkan asal berkas dan hash SHA-256."""
    df["_berkas_raw"] = berkas.as_posix()
    df["_sha256_raw"] = sha256_raw(berkas.as_posix())
    return df


def _baca_csv(nama_berkas):
    """Membaca satu berkas CSV BPS."""
    berkas = DASAR_BPS / nama_berkas
    jalur = RAW / berkas

    df = pd.read_csv(
        jalur,
        encoding="utf-8-sig",
        sep=",",
        decimal=".",
        keep_default_na=False
    )

    df = df[KOLOM].copy()

    return _tempel_lineage(df, berkas)


def _baca_json(nama_berkas):
    """Membaca JSON BPS menjadi tabel panjang."""
    berkas = DASAR_BPS / "json" / nama_berkas
    jalur = RAW / berkas

    with jalur.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise TypeError(
            f"Struktur JSON tidak sesuai: {nama_berkas}"
        )

    baris = []

    for objek in data:
        metadata_var = objek["var"][0]

        peta_wilayah = {
            str(x["val"]): x["label"]
            for x in objek["vervar"]
        }

        peta_turvar = {
            str(x["val"]): x["label"]
            for x in objek["turvar"]
        }

        peta_tahun = {
            str(x["val"]): x["label"]
            for x in objek["tahun"]
        }

        peta_periode = {
            str(x["val"]): x["label"]
            for x in objek["turtahun"]
        }

        for kode, nilai in objek["datacontent"].items():
            kode = str(kode)

            if len(kode) != 13:
                raise ValueError(
                    f"Format kode datacontent tidak sesuai: {kode}"
                )

            wilayah_id = kode[:4]
            var_id = kode[4:8]
            turvar_id = kode[8:9]
            tahun_id = kode[9:12]
            periode_id = kode[12:13]

            baris.append({
                "var_id": int(var_id),
                "wilayah_id": int(wilayah_id),
                "wilayah": peta_wilayah.get(wilayah_id),
                "turvar_id": int(turvar_id),
                "turvar": peta_turvar.get(turvar_id),
                "tahun_id": int(tahun_id),
                "tahun": peta_tahun.get(tahun_id),
                "periode_id": int(periode_id),
                "periode": peta_periode.get(periode_id),
                "nilai": nilai,
                "satuan": (
                    metadata_var.get("unit")
                    or (
                        "Persen"
                        if "Proporsi" in metadata_var.get("label", "")
                        else ""
                    )
                ),
            })

    df = pd.DataFrame(baris, columns=KOLOM)

    return _tempel_lineage(df, berkas)


def baca_bps():
    """
    Membaca dua CSV dan dua JSON BPS.
    Mengembalikan DataFrame terpisah untuk setiap berkas.
    """

    hasil = {
        "var1360_csv": _baca_csv(
            "sdg5_5_3_1_v1360.csv"
        ),
        "var2003_csv": _baca_csv(
            "sdg5_5_5_2_v2003.csv"
        ),
        "var1360_json": _baca_json(
            "sdg5_5_3_1_v1360.json"
        ),
        "var2003_json": _baca_json(
            "sdg5_5_5_2_v2003.json"
        ),
    }

    return hasil


if __name__ == "__main__":
    hasil = baca_bps()

    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")

        assert "_berkas_raw" in df.columns
        assert "_sha256_raw" in df.columns

    print("\nSeluruh berkas BPS berhasil dibaca.")
