"""
Tugas #7 (Tahap 3):
- Pembentukan grid lengkap 38 provinsi x periode per seri BPS (var1360, var2003).
- Pemetaan wilayah ke susunan 38 provinsi (kode BPS 2-digit x 100) sesuai aturan K-001.
- Pemisahan baris nasional (Indonesia, kode 9999) dari baris provinsi.
- Pelaporan kelengkapan panel per seri (persen sel terisi per tahun), dengan membedakan
  structural missing (4 provinsi DOB Papua sebelum tahun berdiri 2022) dan missing aktual.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from src.ekstraksi.bps import baca_bps

ROOT = Path(__file__).resolve().parents[2]
LAPORAN_PATH = ROOT / "reports" / "kelengkapan_panel_tugas7.md"

# Daftar baku 38 Provinsi Indonesia (kode 2-digit BPS x 100, standar 2025)
PROVINSI_38 = {
    1100: "Aceh",
    1200: "Sumatera Utara",
    1300: "Sumatera Barat",
    1400: "Riau",
    1500: "Jambi",
    1600: "Sumatera Selatan",
    1700: "Bengkulu",
    1800: "Lampung",
    1900: "Kepulauan Bangka Belitung",
    2100: "Kepulauan Riau",
    3100: "DKI Jakarta",
    3200: "Jawa Barat",
    3300: "Jawa Tengah",
    3400: "DI Yogyakarta",
    3500: "Jawa Timur",
    3600: "Banten",
    5100: "Bali",
    5200: "Nusa Tenggara Barat",
    5300: "Nusa Tenggara Timur",
    6100: "Kalimantan Barat",
    6200: "Kalimantan Tengah",
    6300: "Kalimantan Selatan",
    6400: "Kalimantan Timur",
    6500: "Kalimantan Utara",
    7100: "Sulawesi Utara",
    7200: "Sulawesi Tengah",
    7300: "Sulawesi Selatan",
    7400: "Sulawesi Tenggara",
    7500: "Gorontalo",
    7600: "Sulawesi Barat",
    8100: "Maluku",
    8200: "Maluku Utara",
    9100: "Papua Barat",
    9200: "Papua Barat Daya",
    9400: "Papua",
    9500: "Papua Selatan",
    9600: "Papua Tengah",
    9700: "Papua Pegunungan",
}

# 4 Provinsi Daerah Otonomi Baru (DOB) Papua hasil pemekaran 2022 (mulai terdata >= 2023)
PROVINSI_DOB_2022 = {9200, 9500, 9600, 9700}
TAHUN_MULAI_DOB = 2023


def bersihkan_nilai(seri_nilai: pd.Series) -> pd.Series:
    """Mengonversi string nilai BPS menjadi float (tanda '-', '', 'n/a' menjadi NaN)."""
    s = seri_nilai.astype(str).str.strip()
    s = s.replace({"": np.nan, "-": np.nan, "nan": np.nan, "None": np.nan, "NA": np.nan, "n/a": np.nan})
    return pd.to_numeric(s, errors="coerce")


def analisis_seri(df_raw: pd.DataFrame, seri_kode: str) -> dict:
    df = df_raw.copy()
    df["wilayah_kode"] = pd.to_numeric(df["wilayah_id"], errors="coerce").astype("Int64")
    df["periode"] = df["tahun"].astype(str).str.strip()
    df["tahun_int"] = pd.to_numeric(df["periode"], errors="coerce")
    df["nilai_num"] = bersihkan_nilai(df["nilai"])

    # 1. Pisahkan baris Indonesia (9999) dan baris provinsi
    df_nasional = df[df["wilayah_kode"] == 9999].copy()
    df_prov_raw = df[df["wilayah_kode"] != 9999].copy()

    # Cek apakah ada kode wilayah tidak dikenal di luar 38 provinsi
    kode_tak_dikenal = sorted(set(df_prov_raw["wilayah_kode"].dropna()) - set(PROVINSI_38.keys()))

    # 2. Deduplikasi observasi pada sumber utama CSV per (wilayah_kode, periode)
    df_prov_obs = (
        df_prov_raw[df_prov_raw["wilayah_kode"].isin(PROVINSI_38.keys())]
        .sort_values(["wilayah_kode", "periode"])
        .drop_duplicates(subset=["wilayah_kode", "periode"], keep="first")
    )

    tahun_tersedia = sorted(df["tahun_int"].dropna().astype(int).unique().tolist())
    periode_list = [str(t) for t in tahun_tersedia]

    # 3. Bentuk Grid Lengkap 38 Provinsi x Semua Periode Seri
    grid = pd.MultiIndex.from_product(
        [sorted(PROVINSI_38.keys()), periode_list],
        names=["wilayah_kode", "periode"],
    ).to_frame(index=False)
    grid["nama_wilayah"] = grid["wilayah_kode"].map(PROVINSI_38)
    grid["tahun_int"] = grid["periode"].astype(int)

    # Gabungkan observasi ke grid
    grid = grid.merge(
        df_prov_obs[["wilayah_kode", "periode", "nilai_num"]],
        on=["wilayah_kode", "periode"],
        how="left",
    )

    # Klasifikasi status sel:
    # - terisi: nilai numerik valid tersedia
    # - belum_terbit (bukan missing): provinsi DOB 2022 pada tahun < 2023
    # - missing_aktual: sel kosong pada provinsi yang sudah berdiri di tahun tersebut
    def klasifikasi_sel(row):
        if pd.notna(row["nilai_num"]):
            return "terisi"
        if row["wilayah_kode"] in PROVINSI_DOB_2022 and row["tahun_int"] < TAHUN_MULAI_DOB:
            return "belum_terbit"
        return "missing_aktual"

    grid["status_sel"] = grid.apply(klasifikasi_sel, axis=1)

    # Ringkasan kelengkapan per tahun
    ringkasan_tahun = []
    for thn in periode_list:
        sub = grid[grid["periode"] == thn]
        total_grid = len(sub)  # selalu 38
        terisi = int((sub["status_sel"] == "terisi").sum())
        belum_terbit = int((sub["status_sel"] == "belum_terbit").sum())
        missing_aktual = int((sub["status_sel"] == "missing_aktual").sum())
        prov_aktif = total_grid - belum_terbit

        persen_dari_38 = (terisi / total_grid) * 100 if total_grid else 0.0
        persen_dari_aktif = (terisi / prov_aktif) * 100 if prov_aktif else 0.0

        nas_ada = bool(df_nasional.loc[df_nasional["periode"] == thn, "nilai_num"].notna().any())

        ringkasan_tahun.append({
            "periode": thn,
            "total_grid": total_grid,
            "prov_aktif": prov_aktif,
            "terisi": terisi,
            "belum_terbit": belum_terbit,
            "missing_aktual": missing_aktual,
            "persen_grid_38": round(persen_dari_38, 2),
            "persen_prov_aktif": round(persen_dari_aktif, 2),
            "nasional_9999": "Ada" if nas_ada else "Kosong",
        })

    df_ringkasan = pd.DataFrame(ringkasan_tahun)
    df_missing_detail = grid[grid["status_sel"] == "missing_aktual"].copy()

    return {
        "seri_kode": seri_kode,
        "periode_list": periode_list,
        "baris_mentah": len(df_raw),
        "baris_nasional": len(df_nasional),
        "baris_prov_mentah": len(df_prov_raw),
        "kode_tak_dikenal": kode_tak_dikenal,
        "total_sel_grid": len(grid),
        "total_terisi": int((grid["status_sel"] == "terisi").sum()),
        "total_belum_terbit": int((grid["status_sel"] == "belum_terbit").sum()),
        "total_missing_aktual": int((grid["status_sel"] == "missing_aktual").sum()),
        "ringkasan_tahun": df_ringkasan,
        "missing_detail": df_missing_detail,
        "nasional_df": df_nasional,
    }


def main():
    bps_data = baca_bps()

    hasil_1360 = analisis_seri(bps_data["var1360_csv"], "var1360")
    hasil_2003 = analisis_seri(bps_data["var2003_csv"], "var2003")

    for h in (hasil_1360, hasil_2003):
        print(f"\nSERI: {h['seri_kode']}")
        print(f"Periode tersedia      : {h['periode_list'][0]} - {h['periode_list'][-1]} ({len(h['periode_list'])} tahun)")
        print(f"Baris mentah CSV      : {h['baris_mentah']} (Nasional 9999: {h['baris_nasional']}, Provinsi: {h['baris_prov_mentah']})")
        print(f"Kode wilayah asing    : {h['kode_tak_dikenal']}")
        print(f"Total sel grid (38xT) : {h['total_sel_grid']}")
        print(f"  - Terisi (Silver)   : {h['total_terisi']}")
        print(f"  - Belum terbit (DOB): {h['total_belum_terbit']} (bukan missing)")
        print(f"  - Missing aktual    : {h['total_missing_aktual']}")
        print("\nTabel Kelengkapan Per Tahun:")
        print(h["ringkasan_tahun"].to_string(index=False))
        if not h["missing_detail"].empty:
            print("\nDaftar Sel Missing Aktual:")
            print(h["missing_detail"][["wilayah_kode", "nama_wilayah", "periode"]].to_string(index=False))

    # Tulis laporan Markdown ke reports/kelengkapan_panel_tugas7.md
    LAPORAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Laporan Kelengkapan Panel Provinsi × Periode (Tugas #7)",
        "",
        "## 1. Aturan Pemetaan Wilayah & Pemisahan Nasional",
        "- **Pemetaan Wilayah:** Mengacu pada keputusan `K-001` (`log-keputusan.csv`), seluruh kode wilayah diselaraskan ke standar **38 provinsi BPS (kode 2-digit × 100)**.",
        "- **Pemisahan Nasional:** Baris dengan `wilayah_kode = 9999` (**Indonesia**) dipisahkan dari tabel panel provinsi agar tidak terjadi penghitungan ganda (*double counting*) saat agregasi.",
        "- **Definisi Missing vs Belum Terbit:** Empat provinsi Daerah Otonomi Baru (DOB) Papua hasil pemekaran tahun 2022 (`9200` Papua Barat Daya, `9500` Papua Selatan, `9600` Papua Tengah, `9700` Papua Pegunungan) belum memiliki entitas administratif sebelum tahun 2023. Oleh karena itu, sel kosong pada 4 provinsi tersebut untuk tahun `< 2023` diklasifikasikan sebagai **belum terbit (structural)** dan **bukan missing**.",
        "",
    ]

    for h in (hasil_1360, hasil_2003):
        lines.extend([
            f"## 2. Kelengkapan Panel Seri `{h['seri_kode']}`",
            f"- **Rentang Periode:** {h['periode_list'][0]}–{h['periode_list'][-1]} ({len(h['periode_list'])} tahun)",
            f"- **Total Grid (38 provinsi × {len(h['periode_list'])} tahun):** {h['total_sel_grid']} sel",
            f"- **Sel Terisi (Masuk Silver):** {h['total_terisi']} sel",
            f"- **Sel Belum Terbit (4 DOB Papua < 2023):** {h['total_belum_terbit']} sel",
            f"- **Sel Missing Aktual:** {h['total_missing_aktual']} sel",
            "",
            "| Tahun | Total Grid | Prov. Aktif | Terisi | Belum Terbit (DOB) | Missing Aktual | Kelengkapan vs 38 Prov (%) | Kelengkapan vs Prov. Aktif (%) | Nasional (9999) |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ])
        for _, r in h["ringkasan_tahun"].iterrows():
            lines.append(
                f"| {r['periode']} | {r['total_grid']} | {r['prov_aktif']} | {r['terisi']} | "
                f"{r['belum_terbit']} | {r['missing_aktual']} | {r['persen_grid_38']:.2f}% | "
                f"{r['persen_prov_aktif']:.2f}% | {r['nasional_9999']} |"
            )
        lines.append("")
        if not h["missing_detail"].empty:
            lines.append(f"### Rincian Sel Missing Aktual (`{h['seri_kode']}`)")
            lines.append("| Kode Wilayah | Nama Provinsi | Tahun |")
            lines.append("| :---: | :--- | :---: |")
            for _, m in h["missing_detail"].iterrows():
                lines.append(f"| {m['wilayah_kode']} | {m['nama_wilayah']} | {m['periode']} |")
            lines.append("")

    LAPORAN_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nLaporan tersimpan di: {LAPORAN_PATH}")


if __name__ == "__main__":
    main()