"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII). Milik tim.

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber.
"""

from pathlib import Path
import pandas as pd

SILVER_PARQUET = Path("data/silver/silver.parquet")


def _siapkan_bps(mentah):
    """Menyeragamkan dua seri utama BPS (CSV kanonik) ke skema Silver."""
    peta_seri = {
        "var1360_csv": (
            "var1360",
            "Proporsi kursi yang diduduki perempuan di parlemen tingkat pusat dan daerah",
        ),
        "var2003_csv": (
            "var2003",
            "Proporsi perempuan yang berada di posisi manajerial",
        ),
    }
    daftar = []
    for kunci, (seri_kode, definisi) in peta_seri.items():
        df = mentah[kunci].copy()
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
        df = df.dropna(subset=["nilai"])

        out = pd.DataFrame({
            "sumber": "BPS",
            "seri_kode": seri_kode,
            "wilayah_kode": df["wilayah_id"].astype(int),
            "nama_wilayah": df["wilayah"].astype(str).str.strip(),
            "periode": df["tahun"].astype(str).str.strip(),
            "jenis_periode": "tahun",
            "rincian": df["turvar"].astype(str).str.strip().replace("", "Total"),
            "nilai": df["nilai"].astype(float),
            "satuan": "Persen",
            "obs_status": "",
            "definisi_indikator": definisi,
            "_berkas_raw": df["_berkas_raw"],
            "_sha256_raw": df["_sha256_raw"],
        })
        daftar.append(out)
    return pd.concat(daftar, ignore_index=True)


def _siapkan_ilostat(mentah):
    """Menyeragamkan seri pembanding ILOSTAT (wilayah IDN) ke skema Silver."""
    peta_ilo = {
        "SDG_0552_NOC_RT_data": (
            "SDG_0552_NOC_RT",
            "Proporsi perempuan di posisi manajerial senior dan menengah (ISCO-08 11-13)",
        ),
        "SDG_T552_NOC_RT_data": (
            "SDG_T552_NOC_RT",
            "Proporsi perempuan di posisi manajerial total (ISCO-08 kategori 1)",
        ),
    }
    daftar = []
    for kunci, (seri_kode, definisi) in peta_ilo.items():
        df = mentah[kunci].copy()
        if "REF_AREA" in df.columns:
            df = df[df["REF_AREA"].astype(str).str.strip() == "IDN"].copy()

        df["nilai"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
        df = df.dropna(subset=["nilai"])

        classif = df["CLASSIF1"].astype(str).str.strip() if "CLASSIF1" in df.columns else "NOC"
        sex = df["SEX"].astype(str).str.strip() if "SEX" in df.columns else "F"
        rincian = "CLASSIF1=" + classif + ";SEX=" + sex

        out = pd.DataFrame({
            "sumber": "ILOSTAT",
            "seri_kode": seri_kode,
            "wilayah_kode": 9999,
            "nama_wilayah": "INDONESIA",
            "periode": df["TIME_PERIOD"].astype(str).str.strip(),
            "jenis_periode": "tahun",
            "rincian": rincian,
            "nilai": df["nilai"].astype(float),
            "satuan": "Persen",
            "obs_status": df["OBS_STATUS"].fillna("").astype(str).str.strip(),
            "definisi_indikator": definisi,
            "_berkas_raw": df["_berkas_raw"],
            "_sha256_raw": df["_sha256_raw"],
        })
        daftar.append(out)
    return pd.concat(daftar, ignore_index=True)


def _siapkan_wdi(mentah):
    """Menyeragamkan seri pembanding World Bank WDI (wilayah IDN) ke skema Silver."""
    daftar = []
    for kunci in ("kelompok_05", "kelompok_07"):
        df = mentah[kunci].copy()
        df = df[df["countryiso3code"].astype(str).str.strip() == "IDN"].copy()
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
        df = df.dropna(subset=["nilai"])

        out = pd.DataFrame({
            "sumber": "WDI",
            "seri_kode": df["indicator_id"].astype(str).str.strip(),
            "wilayah_kode": 9999,
            "nama_wilayah": "INDONESIA",
            "periode": df["tahun"].astype(str).str.strip(),
            "jenis_periode": "tahun",
            "rincian": "Agregat Nasional (IDN)",
            "nilai": df["nilai"].astype(float),
            "satuan": "Persen",
            "obs_status": df["obs_status"].fillna("").astype(str).str.strip(),
            "definisi_indikator": df["indicator"].astype(str).str.strip(),
            "_berkas_raw": df["_berkas_raw"],
            "_sha256_raw": df["_sha256_raw"],
        })
        daftar.append(out)
    return pd.concat(daftar, ignore_index=True)


def jalankan(mentah):
    """Terima keluaran tahap 1, tulis dan kembalikan DataFrame Silver."""
    df_silver = pd.concat(
        [
            _siapkan_bps(mentah),
            _siapkan_ilostat(mentah),
            _siapkan_wdi(mentah),
        ],
        ignore_index=True,
    )
    df_silver["wilayah_kode"] = df_silver["wilayah_kode"].astype("int64")

    SILVER_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(SILVER_PARQUET, index=False)
    print(f"Silver tersimpan: {SILVER_PARQUET} ({len(df_silver)} baris)")
    return df_silver


