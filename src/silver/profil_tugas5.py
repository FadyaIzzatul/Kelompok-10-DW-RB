import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Buat folder output jika belum ada
os.makedirs("reports/gambar", exist_ok=True)

# 2. Lokasi file dataset BPS seri utama
files = {
    "var1360": "data/raw/bps/2026-10-20/sdg5_5_3_1_v1360.csv",
    "var2003": "data/raw/bps/2026-10-20/sdg5_5_5_2_v2003.csv",
}

def analisis_seri(nama_seri, path_csv):
    df = pd.read_csv(path_csv)
    df["nilai_num"] = pd.to_numeric(df["nilai"], errors="coerce")
    
    # Cek kategori turvar
    turvar_unik = df["turvar"].dropna().unique().tolist()
    
    # A. Statistik Deskriptif Per Seri
    s = df["nilai_num"].dropna()
    q1, med, q3 = s.quantile([0.25, 0.50, 0.75])
    iqr = q3 - q1
    batas_bawah = q1 - 1.5 * iqr
    batas_atas = q3 + 1.5 * iqr
    mean_val = s.mean()
    std_val = s.std()
    
    stat_seri = {
        "Seri": nama_seri,
        "Total Baris": len(df),
        "Valid": len(s),
        "Missing": int(df["nilai_num"].isna().sum()),
        "Jumlah Wilayah": df["wilayah"].nunique(),
        "Rentang Tahun": f"{df['tahun'].min()} - {df['tahun'].max()}",
        "Turvar": ", ".join(map(str, turvar_unik)),
        "Mean": round(mean_val, 3),
        "Std": round(std_val, 3),
        "Min": round(s.min(), 3),
        "Q1": round(q1, 3),
        "Median": round(med, 3),
        "Q3": round(q3, 3),
        "Max": round(s.max(), 3),
        "IQR": round(iqr, 3),
        "Batas Bawah IQR": round(batas_bawah, 3),
        "Batas Atas IQR": round(batas_atas, 3),
    }
    
    # B. Statistik Deskriptif Per Provinsi
    stat_prov = (
        df.groupby(["wilayah_id", "wilayah"])["nilai_num"]
        .agg(
            count="count",
            missing=lambda x: int(x.isna().sum()),
            mean=lambda x: round(x.mean(), 2),
            std=lambda x: round(x.std(), 2),
            min=lambda x: round(x.min(), 2),
            q1=lambda x: round(x.quantile(0.25), 2),
            median=lambda x: round(x.median(), 2),
            q3=lambda x: round(x.quantile(0.75), 2),
            max=lambda x: round(x.max(), 2),
        )
        .reset_index()
    )
    
    # C. Deteksi Calon Anomali (IQR & Z-score)
    df["z_score"] = (df["nilai_num"] - mean_val) / std_val if std_val > 0 else 0
    anomali_list = []
    
    for _, row in df.iterrows():
        val = row["nilai_num"]
        alasan = []
        if pd.isna(val):
            alasan.append("Nilai kosong / NaN")
        else:
            if val < batas_bawah:
                alasan.append(f"Outlier bawah IQR (< {batas_bawah:.2f})")
            if val > batas_atas:
                alasan.append(f"Outlier atas IQR (> {batas_atas:.2f})")
            if abs(row["z_score"]) > 3:
                alasan.append(f"|Z-score| > 3 (z={row['z_score']:.2f})")
            if val < 0 or val > 100:
                alasan.append("Di luar rentang persentase wajar (0-100)")
                
        if alasan:
            anomali_list.append({
                "Seri": nama_seri,
                "Wilayah": row["wilayah"],
                "Turvar": row["turvar"],
                "Periode": row["tahun"],
                "Nilai": row["nilai"],
                "Z-Score": round(row["z_score"], 2) if pd.notna(val) else "-",
                "Alasan Ditandai": "; ".join(alasan)
            })
            
    df_anomali = pd.DataFrame(anomali_list)
    
    # D. Visualisasi 1: Boxplot Per Provinsi
    plt.figure(figsize=(14, 7))
    prov_order = (
        df.groupby("wilayah")["nilai_num"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    data_box = [df[df["wilayah"] == p]["nilai_num"].dropna().values for p in prov_order]
    plt.boxplot(data_box, tick_labels=prov_order, vert=True, patch_artist=True)
    plt.axhline(batas_atas, color="red", linestyle="--", linewidth=1, label=f"Batas Atas IQR ({batas_atas:.2f})")
    if batas_bawah > 0:
        plt.axhline(batas_bawah, color="orange", linestyle="--", linewidth=1, label=f"Batas Bawah IQR ({batas_bawah:.2f})")
    plt.title(f"Boxplot Distribusi Nilai {nama_seri} per Provinsi")
    plt.ylabel("Nilai")
    plt.xticks(rotation=90, fontsize=8)
    plt.legend()
    plt.tight_layout()
    path_box = f"reports/gambar/boxplot_{nama_seri}.png"
    plt.savefig(path_box, dpi=150)
    plt.close()
    
    # E. Visualisasi 2: Deret Waktu (Time Series)
    plt.figure(figsize=(13, 6))
    ts_nasional = df.groupby("tahun")["nilai_num"].agg(["mean", "median", "min", "max"]).reset_index()
    
    for prov, grp in df.groupby("wilayah"):
        grp_sorted = grp.sort_values("tahun")
        plt.plot(grp_sorted["tahun"], grp_sorted["nilai_num"], color="gray", alpha=0.25, linewidth=1)
        
    plt.plot(ts_nasional["tahun"], ts_nasional["mean"], color="blue", marker="o", linewidth=2.2, label="Rata-rata Lintas Wilayah")
    plt.plot(ts_nasional["tahun"], ts_nasional["median"], color="green", marker="s", linewidth=2, linestyle="--", label="Median Lintas Wilayah")
    plt.plot(ts_nasional["tahun"], ts_nasional["max"], color="red", linestyle=":", linewidth=1.5, label="Maksimum Tahunan")
    plt.plot(ts_nasional["tahun"], ts_nasional["min"], color="purple", linestyle=":", linewidth=1.5, label="Minimum Tahunan")
    
    plt.title(f"Deret Waktu (Time Series) {nama_seri} (2015 - 2025)")
    plt.xlabel("Tahun")
    plt.ylabel("Nilai")
    plt.xticks(sorted(ts_nasional["tahun"].unique()))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    path_ts = f"reports/gambar/timeseries_{nama_seri}.png"
    plt.savefig(path_ts, dpi=150)
    plt.close()
    
    return stat_seri, stat_prov, df_anomali

# Jalankan analisis untuk kedua seri
hasil_seri = []
detail_prov = {}
detail_anomali = {}

for seri, path in files.items():
    st_seri, st_prov, df_anom = analisis_seri(seri, path)
    hasil_seri.append(st_seri)
    detail_prov[seri] = st_prov
    detail_anomali[seri] = df_anom

df_ringkasan_seri = pd.DataFrame(hasil_seri)

# 3. Tulis otomatis ke laporan Markdown: reports/profil_seri_utama.md
with open("reports/profil_seri_utama.md", "w", encoding="utf-8") as f:
    f.write("# Profil dan Calon Anomali Seri Utama (`var1360`, `var2003`)\n\n")
    f.write("Dokumen ini berisi hasil *profiling* tahap pembersihan (Sprint 1 — Tugas #5) terhadap dua seri utama BPS tanpa melakukan modifikasi data mentah.\n\n")
    
    f.write("## 1. Ringkasan Statistik Deskriptif per Seri\n\n")
    f.write(df_ringkasan_seri.to_markdown(index=False) + "\n\n")
    
    for seri in files.keys():
        f.write(f"---\n\n## 2. Analisis Seri `{seri}`\n\n")
        f.write(f"### Visualisasi Grafik `{seri}`\n")
        f.write(f"![Boxplot {seri}](gambar/boxplot_{seri}.png)\n\n")
        f.write(f"![Deret Waktu {seri}](gambar/timeseries_{seri}.png)\n\n")
        
        f.write(f"### Calon Anomali Terdeteksi (`{seri}`)\n\n")
        df_a = detail_anomali[seri]
        if df_a.empty:
            f.write("_Tidak ditemukan calon anomali berdasarkan kriteria IQR (1.5x) maupun |Z-score| > 3._\n\n")
        else:
            f.write(f"Ditemukan **{len(df_a)}** baris calon anomali:\n\n")
            f.write(df_a.to_markdown(index=False) + "\n\n")
            
        f.write(f"### Statistik Deskriptif per Provinsi (`{seri}`)\n\n")
        f.write(detail_prov[seri].to_markdown(index=False) + "\n\n")

print("SELESAI!")
print("1. Laporan tersimpan di: reports/profil_seri_utama.md")
print("2. Grafik tersimpan di : reports/gambar/")
print("\nRingkasan Seri:")
print(df_ringkasan_seri.to_string(index=False))
for seri, df_a in detail_anomali.items():
    print(f"\nCalon Anomali {seri} ({len(df_a)} baris):")
    print(df_a.to_string(index=False) if not df_a.empty else "Tidak ada")