"""Tahap 4 — Aturan pemilihan satu nilai per sel Gold (Tugas #20).

Menetapkan tepat satu observasi per kombinasi kunci Gold:
- Panel provinsi x periode x seri_kode (wilayah_kode != 9999)
- Tabel nasional x periode x seri_kode (wilayah_kode == 9999)

Aturan yang diterapkan:
1. Snapshot: jika terdapat lebih dari satu snapshot pada kunci yang sama,
   pilih snapshot terbaru berdasarkan tanggal pada jalur `_berkas_raw`
   (jika tanggal sama, prioritaskan sumber kanonik CSV daripada JSON).
2. Rincian sebanding: hanya rincian agregat utama (`turvar_id == 0` /
   `turvar == 'Tidak ada'` pada BPS, dan seluruh rincian yang sudah
   terstandar di Silver untuk ILO/WDI) yang masuk ke Gold; sub-rincian
   lain dipertahankan hanya di Silver.
3. Periode: hanya observasi tahunan (`jenis_periode == 'tahun'`) yang
   masuk ke panel Gold; periode semesteran atau bulanan disaring keluar
   dan tidak dirata-ratakan secara paksa.
4. Pemisahan seri ILO: `SDG_0552_NOC_RT` dan `SDG_T552_NOC_RT` tetap
   disimpan sebagai dua seri terpisah, tidak dirata-rata.
5. Penanda kualitas dari Sprint 1 (`flag`, `outlier`, `patahan_seri`,
   `obs_status`, serta `OBS_STATUS` di JSON `rincian`) ikut terbawa.
"""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd


def _ekstrak_tanggal_snapshot(berkas_raw: Any) -> str:
    """Ambil tanggal YYYY-MM-DD dari jalur berkas mentah untuk urutan snapshot."""
    teks = str(berkas_raw or "")
    cocok = re.search(r"(\d{4}-\d{2}-\d{2})", teks)
    return cocok.group(1) if cocok else "0000-00-00"


def _ekstrak_metadata_rincian(rincian_val: Any) -> dict[str, Any]:
    """Parse string JSON pada kolom `rincian` secara aman."""
    if isinstance(rincian_val, dict):
        return rincian_val
    if isinstance(rincian_val, str) and rincian_val.strip().startswith("{"):
        try:
            return json.loads(rincian_val)
        except json.JSONDecodeError:
            return {}
    return {}


def _is_rincian_panel_utama(row: pd.Series, meta: dict[str, Any]) -> bool:
    """Tentukan apakah baris termasuk rincian agregat utama yang layak masuk Gold."""
    sumber = str(row.get("sumber", "")).lower().strip()
    if sumber == "bps":
        turvar_id = str(meta.get("turvar_id", "0")).strip()
        turvar = str(meta.get("turvar", "Tidak ada")).strip().lower()
        return turvar_id == "0" or turvar in {"tidak ada", "total", ""}
    # Untuk ILOSTAT dan WDI, Silver sudah menyaring cakupan nasional standar per seri_kode
    return True


def _ekstrak_penanda_kualitas(df: pd.DataFrame, meta_list: list[dict[str, Any]]) -> pd.DataFrame:
    """Pastikan penanda patahan seri dan outlier dari Sprint 1 terbawa eksplisit ke Gold."""
    hasil = df.copy()

    # Ambil OBS_STATUS dari kolom langsung atau dari JSON rincian
    obs_dari_meta = [str(m.get("OBS_STATUS", "")).strip().upper() for m in meta_list]
    if "obs_status" not in hasil.columns:
        hasil["obs_status"] = obs_dari_meta
    else:
        hasil["obs_status"] = (
            hasil["obs_status"].fillna("").astype(str).str.strip().str.upper()
        )
        kosong = hasil["obs_status"].eq("")
        hasil.loc[kosong, "obs_status"] = pd.Series(obs_dari_meta, index=hasil.index)[kosong]

    # Teruskan kolom penanda outlier/patahan seri bila ada, atau bentuk ringkasan penanda
    if "flag" not in hasil.columns:
        penanda = []
        for idx, row in hasil.iterrows():
            tags = []
            if row["obs_status"] == "B":
                tags.append("patahan_seri")
            if "outlier" in hasil.columns and pd.notna(row.get("outlier")) and str(row.get("outlier")).strip():
                tags.append(str(row["outlier"]).strip())
            if "patahan_seri" in hasil.columns and bool(row.get("patahan_seri")):
                if "patahan_seri" not in tags:
                    tags.append("patahan_seri")
            penanda.append(";".join(tags) if tags else "normal")
        hasil["flag"] = penanda

    return hasil


def pilih_satu_nilai_gold(silver: pd.DataFrame) -> dict[str, Any]:
    """Terapkan aturan seleksi satu nilai per sel Gold dan hitung jumlah baris tersaring.

    Mengembalikan dictionary berisi:
    - `kandidat_gold`: DataFrame bersih tepat 1 baris per (wilayah_kode, periode, seri_kode)
    - `gold_provinsi`: DataFrame khusus panel provinsi (wilayah_kode != 9999)
    - `gold_nasional`: DataFrame khusus tabel nasional BPS-ILO-WDI (wilayah_kode == 9999)
    - `ringkasan_aturan`: Statistik baris input, tersaring per aturan, dan output akhir
    """
    if silver is None or silver.empty:
        kosong = pd.DataFrame()
        return {
            "kandidat_gold": kosong,
            "gold_provinsi": kosong,
            "gold_nasional": kosong,
            "ringkasan_aturan": {
                "total_silver": 0,
                "tersaring_periode": 0,
                "tersaring_rincian": 0,
                "tersaring_snapshot": 0,
                "total_tidak_terpilih": 0,
                "total_gold": 0,
            },
        }

    total_silver = len(silver)
    df = silver.copy()
    df["wilayah_kode"] = df["wilayah_kode"].astype(str).str.strip()
    df["periode"] = df["periode"].astype(str).str.strip()

    # ATURAN 1: Periode tahunan (saring periode semesteran atau bulanan)
    mask_tahunan = (
        df["jenis_periode"].astype(str).str.lower().str.strip().eq("tahun")
        & df["periode"].str.fullmatch(r"\d{4}")
    )
    tersaring_periode = int((~mask_tahunan).sum())
    df = df[mask_tahunan].copy()

    # ATURAN 2: Rincian sebanding (hanya agregat utama masuk panel Gold)
    meta_list = [_ekstrak_metadata_rincian(v) for v in df["rincian"]]
    mask_rincian = [
        _is_rincian_panel_utama(row, meta)
        for (_, row), meta in zip(df.iterrows(), meta_list)
    ]
    mask_rincian_s = pd.Series(mask_rincian, index=df.index)
    tersaring_rincian = int((~mask_rincian_s).sum())
    df = df[mask_rincian_s].copy()
    meta_terpilih = [m for m, keep in zip(meta_list, mask_rincian) if keep]

    # Bawa penanda kualitas Sprint 1 (patahan seri & outlier) sebelum deduplikasi snapshot
    df = _ekstrak_penanda_kualitas(df, meta_terpilih)

    # ATURAN 3: Satu nilai per (wilayah_kode, periode, seri_kode)
    # Jika terdapat >1 snapshot, pilih snapshot terbaru; jika tanggal sama,
    # prioritaskan berkas CSV kanonik dibanding JSON.
    df["_tgl_snapshot"] = df["_berkas_raw"].apply(_ekstrak_tanggal_snapshot)
    df["_prioritas_format"] = df["_berkas_raw"].astype(str).str.lower().str.endswith(".csv").astype(int)

    df = df.sort_values(
        by=["wilayah_kode", "periode", "seri_kode", "_tgl_snapshot", "_prioritas_format"],
        ascending=[True, True, True, False, False],
    )

    kunci_sel_gold = ["wilayah_kode", "periode", "seri_kode"]
    sebelum_snapshot = len(df)
    df = df.drop_duplicates(subset=kunci_sel_gold, keep="first").copy()
    tersaring_snapshot = sebelum_snapshot - len(df)

    # Hapus kolom bantu internal pengurutan snapshot
    df = df.drop(columns=["_tgl_snapshot", "_prioritas_format"]).reset_index(drop=True)

    # Validasi keras: tidak boleh ada sel ganda di Gold
    assert not df.duplicated(subset=kunci_sel_gold).any(), "Pelanggaran aturan Gold: masih ada sel ganda!"

    # Pisahkan panel provinsi vs seri nasional (dua seri ILO tetap terpisah, tidak dirata-rata)
    gold_provinsi = df[df["wilayah_kode"] != "9999"].reset_index(drop=True)
    gold_nasional = df[df["wilayah_kode"] == "9999"].reset_index(drop=True)

    ringkasan = {
        "total_silver": total_silver,
        "tersaring_periode": tersaring_periode,
        "tersaring_rincian": tersaring_rincian,
        "tersaring_snapshot": tersaring_snapshot,
        "total_tidak_terpilih": total_silver - len(df),
        "total_gold": len(df),
        "total_gold_provinsi": len(gold_provinsi),
        "total_gold_nasional": len(gold_nasional),
    }

    return {
        "kandidat_gold": df,
        "gold_provinsi": gold_provinsi,
        "gold_nasional": gold_nasional,
        "ringkasan_aturan": ringkasan,
    }