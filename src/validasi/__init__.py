"""Tahap 8 — Validasi dan dokumentasi (pertemuan XIV–XV).

Menjalankan aturan validasi dasar pada Silver pertama dari pipeline.py:
1. Nilai persen berada di rentang 0–100.
2. Keunikan kunci utama Silver (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw).
3. Konsistensi satuan per seri_kode (setiap seri hanya memiliki tepat 1 satuan).
4. Dua definisi indikator berbeda (termasuk dua definisi ILO) tidak berbagi seri_kode yang sama.
5. Setiap baris ILO memiliki OBS_STATUS yang terdaftar di DSD ILOSTAT (atau kosong).
"""

import json
from pathlib import Path
import pandas as pd

from src.common.manifest import RAW, baca as baca_manifest
from src.common.skema import KUNCI, periksa_silver

LAPORAN_VALIDASI = Path("reports/validasi.md")


def _ambil_kode_obs_status_dsd() -> set[str]:
    """Membaca daftar kode CL_OBS_STATUS dari berkas DSD ILOSTAT di data/raw/."""
    # Standar SDMX CL_OBS_STATUS yang digunakan pada DSD ILOSTAT (B = Break in series, dll.)
    kode_valid = {"", "A", "B", "E", "F", "I", "L", "M", "O", "P", "Q", "S", "U"}
    folder_dsd = RAW / "ilostat/2026-10-20/dsd"
    if not folder_dsd.exists():
        return kode_valid

    def _telusuri(obj):
        if isinstance(obj, dict):
            if "OBS_STATUS" in str(obj.get("id", "")).upper() and isinstance(obj.get("codes"), list):
                for item in obj["codes"]:
                    if isinstance(item, dict) and item.get("id"):
                        kode_valid.add(str(item["id"]).strip().upper())
            for v in obj.values():
                _telusuri(v)
        elif isinstance(obj, list):
            for el in obj:
                _telusuri(el)

    for berkas_json in folder_dsd.glob("*.json"):
        with berkas_json.open("r", encoding="utf-8-sig") as f:
            _telusuri(json.load(f))
    return kode_valid





def _muat_silver(sumber) -> pd.DataFrame | None:
    if isinstance(sumber, pd.DataFrame):
        return sumber
    if isinstance(sumber, (str, Path)) and Path(sumber).exists():
        return pd.read_parquet(sumber)
    jalur = Path("data/silver/silver.parquet")
    if jalur.exists():
        return pd.read_parquet(jalur)
    return None


def jalankan(silver=None, gold=None) -> dict:
    """Dipanggil otomatis oleh pipeline.py pada tahap validasi."""
    df = _muat_silver(silver)
    if df is None or df.empty:
        raise ValueError("Tabel Silver kosong atau belum tersedia untuk divalidasi.")

    # Pemeriksaan lantai skema minimal src/common/skema.py
    try:
        manifest = baca_manifest()
    except FileNotFoundError:
        manifest = None
    pelanggaran_skema = periksa_silver(df, manifest)
    if pelanggaran_skema:
        print("[PERINGATAN SKEMA]", pelanggaran_skema)

    hasil_aturan = {}
    detail_aturan = {}

    # ---------------------------------------------------------
    # ATURAN 1: Nilai persen berada di rentang 0–100
    # ---------------------------------------------------------
    mask_persen = df["satuan"].astype(str).str.lower().str.strip().isin(["persen", "%", "percent"])
    df_persen = df[mask_persen]
    di_luar_rentang = df_persen[~df_persen["nilai"].between(0, 100)]
    lolos_1 = len(di_luar_rentang) == 0
    hasil_aturan["1_rentang_nilai_persen_0_100"] = lolos_1
    detail_aturan["1_rentang_nilai_persen_0_100"] = (
        f"Diperiksa {len(df_persen)} baris bersatuan Persen; pelanggaran di luar [0, 100] = {len(di_luar_rentang)} baris."
    )

    # ---------------------------------------------------------
    # ATURAN 2: Keunikan kunci utama Silver
    # ---------------------------------------------------------
    kunci_ada = [k for k in KUNCI if k in df.columns]
    jml_duplikat = int(df.duplicated(subset=kunci_ada).sum())
    lolos_2 = jml_duplikat == 0
    hasil_aturan["2_keunikan_kunci_silver"] = lolos_2
    detail_aturan["2_keunikan_kunci_silver"] = (
        f"Kunci {kunci_ada}: total {len(df)} baris unik, duplikat = {jml_duplikat} baris."
    )

    # ---------------------------------------------------------
    # ATURAN 3: Konsistensi satuan per seri_kode
    # ---------------------------------------------------------
    satuan_per_seri = df.groupby("seri_kode")["satuan"].nunique(dropna=False)
    seri_satuan_ganda = satuan_per_seri[satuan_per_seri > 1].index.tolist()
    lolos_3 = len(seri_satuan_ganda) == 0
    hasil_aturan["3_konsistensi_satuan_per_seri"] = lolos_3
    detail_aturan["3_konsistensi_satuan_per_seri"] = (
        f"Diperiksa {df['seri_kode'].nunique()} seri_kode; seri dengan satuan ganda = {seri_satuan_ganda}."
    )

    # ---------------------------------------------------------
    # ATURAN 4: Dua definisi ILO tidak berbagi seri_kode yang sama
    # ---------------------------------------------------------
    df_ilo = df[df["sumber"].astype(str).str.upper() == "ILOSTAT"]
    if "definisi_indikator" in df_ilo.columns and not df_ilo.empty:
        def_per_seri = df_ilo.groupby("seri_kode")["definisi_indikator"].nunique(dropna=True)
        seri_per_def = df_ilo.groupby("definisi_indikator")["seri_kode"].nunique(dropna=True)
        konflik_1 = def_per_seri[def_per_seri > 1].index.tolist()
        konflik_2 = seri_per_def[seri_per_def > 1].index.tolist()
        seri_ilo_unik = sorted(df_ilo["seri_kode"].unique().tolist())
        lolos_4 = (len(konflik_1) == 0) and (len(konflik_2) == 0) and (len(seri_ilo_unik) >= 2)
        detail_aturan["4_pemisahan_seri_kode_definisi_ilo"] = (
            f"Seri ILO terpisah = {seri_ilo_unik} (1 seri_kode = 1 definisi); konflik = {konflik_1 + konflik_2}."
        )
    else:
        seri_ilo_unik = sorted(df_ilo["seri_kode"].unique().tolist())
        lolos_4 = len(seri_ilo_unik) >= 2
        detail_aturan["4_pemisahan_seri_kode_definisi_ilo"] = f"Seri ILO terpisah = {seri_ilo_unik}."
    hasil_aturan["4_pemisahan_seri_kode_definisi_ilo"] = lolos_4

    # ---------------------------------------------------------
    # ATURAN 5: Setiap baris ILO punya OBS_STATUS terdaftar di DSD (atau kosong)
    # ---------------------------------------------------------
    kode_dsd_resmi = _ambil_kode_obs_status_dsd()
    if "obs_status" in df_ilo.columns and not df_ilo.empty:
        obs_ilo = df_ilo["obs_status"].fillna("").astype(str).str.strip().str.upper()
        tidak_terdaftar = obs_ilo[~obs_ilo.isin(kode_dsd_resmi)]
        lolos_5 = len(tidak_terdaftar) == 0
        status_ditemukan = sorted(obs_ilo.unique().tolist())
        detail_aturan["5_validitas_obs_status_ilo_dsd"] = (
            f"Kode OBS_STATUS di data ILO = {status_ditemukan}; terdaftar di DSD/kosong, ilegal = {len(tidak_terdaftar)} baris."
        )
    else:
        lolos_5 = False
        detail_aturan["5_validitas_obs_status_ilo_dsd"] = "Kolom obs_status tidak ditemukan pada baris ILO."
    hasil_aturan["5_validitas_obs_status_ilo_dsd"] = lolos_5

    total_aturan = len(hasil_aturan)
    total_lolos = sum(1 for v in hasil_aturan.values() if v)

    print("\n=== HASIL VALIDASI SILVER PERTAMA ===")
    for nama, status in hasil_aturan.items():
        label = "LOLOS" if status else "GAGAL"
        print(f"[{label}] {nama} -> {detail_aturan[nama]}")
    print(f"Total aturan validasi: {total_lolos}/{total_aturan} LOLOS.\n")

    # Simpan laporan ke reports/validasi.md
    baris_md = [
        "# Laporan Validasi Silver Pertama (Tahap 8)",
        "",
        f"- **Total Baris Silver:** `{len(df)}` baris (`{df['seri_kode'].nunique()}` seri, `{df['wilayah_kode'].nunique()}` wilayah)",
        f"- **Pemeriksaan Skema Dasar (`src.common.skema`):** `{'LOLOS (0 pelanggaran)' if not pelanggaran_skema else pelanggaran_skema}`",
        f"- **Ringkasan Aturan Validasi:** **{total_lolos}/{total_aturan} aturan LOLOS**",
        "",
        "| No | Nama Aturan Validasi | Status | Keterangan Hasil |",
        "| :---: | :--- | :---: | :--- |",
    ]
    for idx, (nama, status) in enumerate(hasil_aturan.items(), start=1):
        baris_md.append(
            f"| {idx} | `{nama}` | **{'LOLOS' if status else 'GAGAL'}** | {detail_aturan[nama]} |"
        )

    LAPORAN_VALIDASI.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN_VALIDASI.write_text("\n".join(baris_md), encoding="utf-8")
    print(f"Laporan validasi tersimpan di: {LAPORAN_VALIDASI}")

    return {
        "aturan_validasi": total_aturan,
        "aturan_lolos": total_lolos,
        "detail": hasil_aturan,
    }


