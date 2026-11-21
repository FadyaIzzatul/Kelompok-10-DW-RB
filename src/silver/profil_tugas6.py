import json
import os
import pandas as pd


def load_bps_years(path_csv):
    df = pd.read_csv(path_csv)
    tahun_col = [c for c in df.columns if "tahun" in c.lower()][0]
    raw_years = sorted(df[tahun_col].dropna().astype(int).unique().tolist())
    # Konversi pengkodean tahun BPS (115 -> 2015, dst.)
    years_4d = [1900 + y if y < 1000 else y for y in raw_years]
    return years_4d


def inspect_ilostat_csv(path_csv, dsd_path, kode_seri, tahun_utama):
    df = pd.read_csv(path_csv)
    dsd_label = ""
    if os.path.exists(dsd_path):
        with open(dsd_path, "r", encoding="utf-8") as f:
            dsd_json = json.load(f)
            dsd_label = str(dsd_json.get("data", {}).get("dataflows", [{}])[0].get("name", ""))

    valid_grp = df.dropna(subset=["OBS_VALUE"]).sort_values("TIME_PERIOD")
    tahun_tersedia = sorted(valid_grp["TIME_PERIOD"].astype(int).unique().tolist())
    irisan = sorted(list(set(tahun_tersedia).intersection(set(tahun_utama))))

    break_years = valid_grp[valid_grp["NOTE_INDICATOR"].notna()]["TIME_PERIOD"].astype(int).tolist()
    catatan = f"Sumber survei: {valid_grp['SOURCE'].dropna().iloc[0]}"
    if break_years:
        catatan += f"; Break in series pada tahun {break_years}"

    rincian_desc = (
        f"Measure: `{valid_grp['MEASURE'].iloc[0]}`; "
        f"Klasifikasi: `NOC` (Agregat Total / Tanpa Rincian Sub-kategori); "
        f"Jenis Kelamin: Perempuan (rasio terhadap total); "
        f"Level: Nasional (`IDN`)"
    )

    row = {
        "seri": kode_seri,
        "sumber": "ILOSTAT",
        "wilayah": "IDN (Indonesia)",
        "rincian": rincian_desc,
        "satuan": f"Persen (`{valid_grp['UNIT_MEASURE'].iloc[0]}` / `{valid_grp['UNIT_MEASURE_TYPE'].iloc[0]}`)",
        "jumlah_obs": len(valid_grp),
        "periode": f"{min(tahun_tersedia)}–{max(tahun_tersedia)}" if tahun_tersedia else "-",
        "daftar_tahun": tahun_tersedia,
        "tahun_irisan": irisan,
        "jumlah_irisan": len(irisan),
        "nilai_min": round(valid_grp["OBS_VALUE"].min(), 3),
        "nilai_max": round(valid_grp["OBS_VALUE"].max(), 3),
        "catatan_status": catatan,
        "dsd_label": dsd_label
    }
    return row


def inspect_wdi_json(paths_json, kode_seri, tahun_utama):
    records = []
    for p in paths_json:
        with open(p, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if isinstance(raw, list) and len(raw) > 1 and isinstance(raw[1], list):
                records.extend(raw[1])

    df = pd.DataFrame(records)
    df["ind_id"] = df["indicator"].apply(lambda x: x.get("id") if isinstance(x, dict) else x)
    df["ind_name"] = df["indicator"].apply(lambda x: x.get("value") if isinstance(x, dict) else x)
    df["country_name"] = df["country"].apply(lambda x: x.get("value") if isinstance(x, dict) else x)
    df["year"] = df["date"].astype(int)
    df["val"] = pd.to_numeric(df["value"], errors="coerce")

    sub = df[(df["countryiso3code"] == "IDN") & (df["ind_id"] == kode_seri)].drop_duplicates(subset=["year"])
    valid_df = sub.dropna(subset=["val"]).sort_values("year")

    tahun_tersedia = sorted(valid_df["year"].unique().tolist())
    irisan = sorted(list(set(tahun_tersedia).intersection(set(tahun_utama))))
    nama_indikator = sub["ind_name"].dropna().iloc[0] if len(sub["ind_name"].dropna()) else kode_seri

    if kode_seri == "SG.GEN.PARL.ZS":
        rincian_desc = "Jenis Kelamin: Perempuan (`Female`); Lingkup: Parlemen Nasional (Single/Lower House); Umur/Daerah: Agregat Nasional (`IDN`)"
    elif kode_seri == "SP.M18.2024.FE.ZS":
        rincian_desc = "Jenis Kelamin: Perempuan (`Female`); Kelompok Umur: 20–24 tahun (menikah pertama kali sebelum usia 18 tahun); Daerah: Agregat Nasional (`IDN`)"
    else:
        rincian_desc = "Agregat Nasional (`IDN`)"

    row = {
        "seri": kode_seri,
        "sumber": "World Bank WDI",
        "wilayah": "IDN (Indonesia)",
        "rincian": rincian_desc,
        "satuan": "Persen (`%`, kode indikator `.ZS`)",
        "jumlah_obs": len(valid_df),
        "periode": f"{min(tahun_tersedia)}–{max(tahun_tersedia)}" if tahun_tersedia else "-",
        "daftar_tahun": tahun_tersedia,
        "tahun_irisan": irisan,
        "jumlah_irisan": len(irisan),
        "nilai_min": round(valid_df["val"].min(), 3),
        "nilai_max": round(valid_df["val"].max(), 3),
        "catatan_status": f"Nama resmi: {nama_indikator} (total record IDN mentah: {len(sub)}, non-null: {len(valid_df)})",
        "dsd_label": nama_indikator
    }
    return row


def main():
    os.makedirs("reports", exist_ok=True)

    tahun_v1360 = load_bps_years("data/raw/bps/2026-10-20/sdg5_5_3_1_v1360.csv")
    tahun_v2003 = load_bps_years("data/raw/bps/2026-10-20/sdg5_5_5_2_v2003.csv")
    tahun_utama = sorted(list(set(tahun_v1360).union(set(tahun_v2003))))

    wdi_files = [
        "data/raw/wdi/2026-10-20/data/kelompok-05-hal-01.json",
        "data/raw/wdi/2026-10-20/data/kelompok-07-hal-01.json",
    ]

    rows = [
        inspect_ilostat_csv(
            "data/raw/ilostat/2026-10-20/data/DF_SDG_0552_NOC_RT.csv",
            "data/raw/ilostat/2026-10-20/dsd/SDG_0552_NOC_RT.json",
            "SDG_0552_NOC_RT",
            tahun_utama,
        ),
        inspect_ilostat_csv(
            "data/raw/ilostat/2026-10-20/data/DF_SDG_T552_NOC_RT.csv",
            "data/raw/ilostat/2026-10-20/dsd/SDG_T552_NOC_RT.json",
            "SDG_T552_NOC_RT",
            tahun_utama,
        ),
        inspect_wdi_json(wdi_files, "SG.GEN.PARL.ZS", tahun_utama),
        inspect_wdi_json(wdi_files, "SP.M18.2024.FE.ZS", tahun_utama),
    ]

    for r in rows:
        print(f"{r['seri']} | periode={r['periode']} | obs={r['jumlah_obs']} | irisan ({r['jumlah_irisan']} thn)={r['tahun_irisan']}")

    md_lines = [
        "# Profil Seri Pembanding Nasional (Tugas #6)",
        "",
        "Dokumen ini menyajikan hasil profiling empat seri pembanding nasional dari **ILOSTAT** (`SDG_0552_NOC_RT`, `SDG_T552_NOC_RT`) dan **World Bank WDI** (`SG.GEN.PARL.ZS`, `SP.M18.2024.FE.ZS`) pada cakupan wilayah **Indonesia (`IDN`)**, meliputi ketersediaan periode, rincian disaggregasi (jenis kelamin, kelompok umur, wilayah/daerah, dan klasifikasi), satuan pengukuran, serta tahun yang beririsan dengan seri utama BPS (`var1360` dan `var2003`, periode **2015–2025**).",
        "",
        "## 1. Acuan Seri Utama (BPS)",
        "",
        "| Kode Seri | Indikator Utama | Cakupan Wilayah | Satuan | Periode Tersedia (Kode Tahun BPS) |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| `var1360` | Proporsi kursi yang diduduki perempuan di parlemen tingkat pusat dan daerah (SDG 5.5.1) | 34–38 Provinsi + Nasional (`9999`) | Persen (`%`) | {min(tahun_v1360)}–{max(tahun_v1360)} (`115`–`125`, {len(tahun_v1360)} tahun) |",
        f"| `var2003` | Proporsi perempuan yang berada di posisi manajerial (SDG 5.5.2) | 34–38 Provinsi + Nasional (`9999`) | Persen (`%`) | {min(tahun_v2003)}–{max(tahun_v2003)} (`115`–`125`, {len(tahun_v2003)} tahun) |",
        "",
        "## 2. Tabel Ketersediaan Seri × Periode × Rincian (`IDN`)",
        "",
        "| Kode Seri | Sumber | Wilayah | Rincian (Jenis Kelamin, Umur, Daerah, Klasifikasi) | Satuan | Periode Tersedia | Tahun Beririsan dgn Seri Utama (2015–2025) | Rentang Nilai |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in rows:
        irisan_str = f"{', '.join(map(str, r['tahun_irisan']))} (**{r['jumlah_irisan']} thn**)" if r["tahun_irisan"] else "Tidak ada"
        md_lines.append(
            f"| `{r['seri']}` | {r['sumber']} | {r['wilayah']} | {r['rincian']} | {r['satuan']} | {r['periode']} ({r['jumlah_obs']} obs) | {irisan_str} | {r['nilai_min']} – {r['nilai_max']} |"
        )

    md_lines.extend([
        "",
        "## 3. Rincian Daftar Tahun Observasi & Catatan Kualitas Data",
        "",
    ])

    for r in rows:
        md_lines.append(f"- **`{r['seri']}`** ({r['sumber']}): Tahun tersedia = `{r['daftar_tahun']}`. *{r['catatan_status']}*.")

    md_lines.extend([
        "",
        "## 4. Penandaan Kandidat Rincian yang Sebanding (Untuk Tahap Integrasi)",
        "",
        "| Kode Seri Pembanding | Pasangan Seri Utama BPS | Status Kandidat | Rincian Dipilih untuk Integrasi | Alasan Metodologis |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **`SG.GEN.PARL.ZS`** (WDI) | `var1360` (Proporsi Kursi Perempuan di Parlemen) | **[TERPILIH] KANDIDAT SEBANDING UTAMA** | `countryiso3code=IDN`, Perempuan (`Female`), Agregat Parlemen Nasional, Satuan Persen (`%`) | Mengukur *Proportion of seats held by women in national parliaments (%)* yang selaras secara definisi dengan `var1360` level nasional (`wilayah_id=9999`), menggunakan satuan persen yang sama, dan memiliki **irisan penuh 11 tahun (2015–2025)** tanpa jeda. |",
        "| **`SDG_T552_NOC_RT`** (ILOSTAT) | `var2003` (Proporsi Perempuan di Posisi Manajerial) | **[TERPILIH] KANDIDAT SEBANDING UTAMA** | `REF_AREA=IDN`, `MEASURE=SDG_T552_RT`, Agregat Total (`NOC`), Satuan Persen (`PT`) | Mengukur proporsi perempuan dalam posisi manajerial total (*Total management*, ISCO-08 kategori 1) dari survei Sakernas (*LFS*) dalam satuan persen, sebanding dengan `var2003` level nasional (`wilayah_id=9999`) dengan **8 tahun beririsan (2015–2017, 2019–2023)**. Perlu catatan *break in series* tahun 2021 saat analisis tren. |",
        "| **`SDG_0552_NOC_RT`** (ILOSTAT) | `var2003` (Proporsi Perempuan di Posisi Manajerial) | **[CADANGAN / SEKUNDER] SEBANDING SECARA KONSEP, MINIM IRISAN** | `REF_AREA=IDN`, `MEASURE=SDG_0552_RT`, Agregat Total (`NOC`), Satuan Persen (`PT`) | Mengukur proporsi perempuan di posisi manajerial senior dan menengah (*Senior and middle management*, ISCO-08 sub-kategori 11–13) dalam satuan persen. Definisi lebih sempit dibanding `SDG_T552_NOC_RT` dan **hanya beririsan 1 tahun (`2023`)** dengan periode seri utama BPS (2015–2025), sehingga hanya dipakai sebagai pembanding titik tahun 2023. |",
        "| **`SP.M18.2024.FE.ZS`** (WDI) | *Tidak ada pasangan (`var1360` maupun `var2003`)* | **[DIKECUALIKAN] BUKAN KANDIDAT SEBANDING** | — (Tidak digabungkan ke tabel integrasi) | Mengukur *Women who were first married by age 18 (% of women ages 20–24)* (SDG 5.3.1), yaitu prevalensi perkawinan anak pada kelompok umur 20–24 tahun. Tidak relevan secara konseptual dengan representasi politik (`var1360`) maupun kepemimpinan manajerial (`var2003`), serta hanya memiliki 1 titik irisan (`2017`). |",
    ])

    out_path = "reports/profil_seri_pembanding.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"\n[SUKSES] Laporan final tersimpan di {out_path}")


if __name__ == "__main__":
    main()