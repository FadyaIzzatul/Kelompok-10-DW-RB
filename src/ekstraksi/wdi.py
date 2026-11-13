
"""Pembaca data dan metadata WDI Kasus 10 (SDG 5).
Membaca dua JSON observasi dan tiga JSON metadata tanpa pembersihan data.
"""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

DASAR_WDI = Path("wdi/2026-10-20")

INDIKATOR = {
    "SG.GEN.PARL.ZS",
    "SP.M18.2024.FE.ZS",
}

KOLOM_DATA = [
    "indicator_id",
    "indicator",
    "country_id",
    "country",
    "countryiso3code",
    "tahun",
    "nilai",
    "scale",
    "unit",
    "obs_status",
    "decimal",
]


def _baca_json(berkas):
    jalur = RAW / berkas

    with jalur.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _tempel_lineage(df, berkas):
    df["_berkas_raw"] = berkas.as_posix()
    df["_sha256_raw"] = sha256_raw(berkas.as_posix())

    return df


def _baca_data(nama_berkas):
    berkas = DASAR_WDI / "data" / nama_berkas
    isi = _baca_json(berkas)

    if not isinstance(isi, list) or len(isi) < 2:
        raise ValueError(
            f"Struktur JSON WDI tidak sesuai: {berkas}"
        )

    baris = []

    for observasi in isi[1]:
        indikator = observasi.get("indicator") or {}
        indicator_id = indikator.get("id")

        if indicator_id not in INDIKATOR:
            continue

        negara = observasi.get("country") or {}

        baris.append({
            "indicator_id": indicator_id,
            "indicator": indikator.get("value"),
            "country_id": negara.get("id"),
            "country": negara.get("value"),
            "countryiso3code": observasi.get("countryiso3code"),
            "tahun": observasi.get("date"),
            "nilai": observasi.get("value"),
            "scale": observasi.get("scale"),
            "unit": observasi.get("unit"),
            "obs_status": observasi.get("obs_status"),
            "decimal": observasi.get("decimal"),
        })

    df = pd.DataFrame(baris, columns=KOLOM_DATA)

    return _tempel_lineage(df, berkas)


def _baca_metadata(nama_berkas, jenis):
    berkas = DASAR_WDI / "metadata" / nama_berkas
    isi = _baca_json(berkas)

    if not isinstance(isi, list) or len(isi) < 2:
        raise ValueError(
            f"Struktur JSON metadata WDI tidak sesuai: {berkas}"
        )

    data = isi[1]

    if jenis == "indikator":
        data = [
            baris for baris in data
            if baris.get("id") in INDIKATOR
        ]

    df = pd.DataFrame(data)

    if jenis == "indikator" and not df.empty:
        df = df.rename(columns={"id": "indicator_id"})

    return _tempel_lineage(df, berkas)


def baca_wdi():
    """Mengembalikan lima tabel terpisah."""

    return {
        "kelompok_05": _baca_data(
            "kelompok-05-hal-01.json"
        ),

        "kelompok_07": _baca_data(
            "kelompok-07-hal-01.json"
        ),

        "metadata_sumber": _baca_metadata(
            "sumber.json", "sumber"
        ),

        "metadata_sumber2_indikator": _baca_metadata(
            "sumber2_indikator.json", "indikator"
        ),

        "metadata_sumber46_indikator": _baca_metadata(
            "sumber46_indikator.json", "indikator"
        ),
    }


if __name__ == "__main__":
    hasil = baca_wdi()

    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")

        assert "_berkas_raw" in df.columns
        assert "_sha256_raw" in df.columns

    print("\nSeluruh 5 berkas WDI berhasil dibaca.")
