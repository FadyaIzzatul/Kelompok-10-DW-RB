"""Persiapan tahap 6 untuk snapshot Kasus 10."""

from pathlib import Path

import pandas as pd

from src.common.manifest import periksa
from src.ekstraksi import baca_bps, baca_ilostat, baca_wdi

PASANGAN = (
    ("var2003", "SDG_T552_NOC_RT"),
    ("var2003", "SDG_0552_NOC_RT"),
    ("var1360", "SP.M18.2024.FE.ZS"),
)
SERI = (
    "var2003", "SDG_T552_NOC_RT", "SDG_0552_NOC_RT",
    "var1360", "SP.M18.2024.FE.ZS", "SG.GEN.PARL.ZS",
)
TUJUAN = Path(__file__).resolve().parents[2] / "data/gold/rekonsiliasi_nasional_kasus10.csv"


def tabel_nasional(mentah):
    """Susun observasi nasional tahunan dengan satu nilai per periode dan seri."""
    observasi = {}
    for kode in ("var2003", "var1360"):
        bps = mentah[f"{kode}_csv"]
        nasional = bps.loc[
            bps["wilayah_id"].astype(str).eq("9999")
            & bps["turvar_id"].astype(str).eq("0")
            & bps["periode_id"].astype(str).eq("0")
        ]
        observasi[kode] = nasional.set_index("tahun")["nilai"]

    for kode, ukuran in (
        ("SDG_T552_NOC_RT", "SDG_T552_RT"),
        ("SDG_0552_NOC_RT", "SDG_0552_RT"),
    ):
        ilo = mentah[f"{kode}_data"]
        nasional = ilo.loc[
            ilo["REF_AREA"].eq("IDN")
            & ilo["FREQ"].eq("A")
            & ilo["MEASURE"].eq(ukuran)
            & ilo["UNIT_MEASURE"].eq("PT")
            & ilo["UNIT_MULT"].astype(str).eq("0")
            & ilo["SOURCE"].eq("LFS - National Labour Force Survey")
        ]
        observasi[kode] = nasional.set_index("TIME_PERIOD")["OBS_VALUE"]

    wdi = pd.concat([mentah["kelompok_05"], mentah["kelompok_07"]])
    for kode in ("SP.M18.2024.FE.ZS", "SG.GEN.PARL.ZS"):
        nasional = wdi.loc[wdi["countryiso3code"].eq("IDN") & wdi["indicator_id"].eq(kode)]
        observasi[kode] = nasional.set_index("tahun")["nilai"]

    for kode, nilai in observasi.items():
        nilai = pd.to_numeric(nilai.replace("", None)).dropna()
        nilai.index = nilai.index.astype(int)
        if nilai.empty or nilai.index.has_duplicates:
            raise ValueError(f"Observasi nasional kosong atau periode duplikat: {kode}")
        observasi[kode] = nilai

    return pd.DataFrame(observasi, columns=SERI).sort_index().rename_axis("periode")


def main():
    _, salah = periksa()
    if salah:
        raise SystemExit("Snapshot tidak cocok dengan MANIFEST.csv. Jalankan ulang unduh_data.py.")

    tabel = tabel_nasional({**baca_bps(), **baca_ilostat(), **baca_wdi()})
    tabel.to_csv(TUJUAN, lineterminator="\n")
    tahun_beririsan = set()
    for kiri, kanan in PASANGAN:
        tahun = tabel[[kiri, kanan]].dropna().index.tolist()
        tahun_beririsan.update(tahun)
        print(f"{kiri} / {kanan}: {tahun}")
    print(f"pasangan_rekonsiliasi={len(PASANGAN)} periode_beririsan={len(tahun_beririsan)}")


if __name__ == "__main__":
    main()
