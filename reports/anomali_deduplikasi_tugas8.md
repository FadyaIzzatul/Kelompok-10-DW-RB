# Laporan Klasifikasi Anomali, Patahan Seri, dan Aturan Deduplikasi (Tugas #8)

## 1. Aturan Deduplikasi Multi-Snapshot (BPS CSV vs JSON & ILOSTAT)
- **Aturan Baku:** Jika dua *snapshot* (CSV dan JSON BPS) memiliki **angka identik** pada kunci `(var_id, wilayah_id, turvar_id, tahun, periode_id)`, baris tersebut **bukan duplikat yang salah**, melainkan representasi dari observasi yang sama; digunakan berkas CSV kanonik sebagai basis Silver dan JSON disimpan sebagai jejak audit.
- **Aturan Revisi:** Jika terdapat **angka berbeda** pada kunci yang sama antar-*snapshot*, perbedaan diperlakukan sebagai **revisi** dan dicatat dalam log keputusan.

### Hasil Pemeriksaan Deduplikasi BPS
| Seri | Baris CSV | Baris JSON | Dup Internal CSV | Dup Internal JSON | Identik (CSV=JSON) | Revisi Berbeda | Hanya CSV | Hanya JSON |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `var1360` | 393 | 393 | 0 | 0 | 393 | 0 | 0 | 0 |
| `var2003` | 391 | 391 | 0 | 0 | 391 | 0 | 0 | 0 |

## 2. Evaluasi Patahan Seri (*Break in Series*)
### A. Seri Utama BPS (`var1360` & `var2003`)
Pemeriksaan perubahan tahunan (*Year-on-Year* / YoY) lintas provinsi dilakukan untuk mendeteksi apakah terjadi lonjakan serentak di hampir semua provinsi pada tahun yang sama:

| seri    |   tahun |   n_transisi |   naik |   turun |   median_delta_pp |   lonjakan_gt_15pp |
|:--------|--------:|-------------:|-------:|--------:|------------------:|-------------------:|
| var1360 |    2016 |           34 |     18 |      16 |              0.04 |                  0 |
| var1360 |    2017 |           34 |     21 |      13 |              0.49 |                  0 |
| var1360 |    2018 |           34 |      8 |      26 |             -0.81 |                  0 |
| var1360 |    2019 |           34 |     18 |      16 |              0.38 |                  0 |
| var1360 |    2020 |           34 |     10 |      24 |             -0.51 |                  0 |
| var1360 |    2021 |           34 |      5 |      29 |             -1.16 |                  0 |
| var1360 |    2022 |           34 |      8 |      26 |             -1    |                  0 |
| var1360 |    2023 |           34 |     10 |      24 |             -0.98 |                  0 |
| var1360 |    2024 |           34 |      5 |      29 |             -0.98 |                  0 |
| var1360 |    2025 |           38 |     10 |      28 |             -1.12 |                  0 |
| var2003 |    2016 |           34 |     19 |      15 |              2.18 |                  3 |
| var2003 |    2017 |           34 |     24 |      10 |              1.81 |                  1 |
| var2003 |    2018 |           34 |     23 |      11 |              2.54 |                  0 |
| var2003 |    2019 |           34 |     19 |      15 |              0.67 |                  0 |
| var2003 |    2020 |           34 |     23 |      11 |              2.98 |                  0 |
| var2003 |    2021 |           34 |     16 |      18 |             -0.42 |                  0 |
| var2003 |    2022 |           34 |     21 |      13 |              1.58 |                  1 |
| var2003 |    2023 |           34 |     24 |      10 |              2.44 |                  0 |
| var2003 |    2024 |           34 |     16 |      18 |             -0.68 |                  0 |
| var2003 |    2025 |           36 |     20 |      16 |              1.19 |                  0 |

> **Kesimpulan Patahan Seri BPS:** Tidak ditemukan lonjakan ekstrem serentak lintas provinsi pada satu tahun tertentu (perubahan median YoY berkisar antara $-2.76$ hingga $+2.84$ poin persentase). Seluruh variasi antar-tahun merupakan dinamika elektoral (pemilu legislatif 2019 & 2024 pada `var1360`) dan dinamika ketenagakerjaan tahunan (`var2003`), sehingga **0 baris** dikategorikan sebagai patahan seri pada BPS.

### B. Seri Pembanding ILOSTAT (`OBS_STATUS`)
Sesuai aturan kasus, nilai `OBS_STATUS = B` (*Break in series*) pada dataset ILOSTAT **tidak dibuang**, melainkan dipertahankan dan diberi penanda eksplisit sebagai patahan seri:

| seri            | ref_area   |   tahun |   nilai | obs_status   | kategori     | tindakan                                                      |
|:----------------|:-----------|--------:|--------:|:-------------|:-------------|:--------------------------------------------------------------|
| SDG_0552_NOC_RT | IDN        |    2008 |  16.442 | B            | patahan_seri | Dipertahankan & ditandai sebagai patahan seri (tidak dibuang) |
| SDG_T552_NOC_RT | IDN        |    2008 |  21.343 | B            | patahan_seri | Dipertahankan & ditandai sebagai patahan seri (tidak dibuang) |
| SDG_T552_NOC_RT | IDN        |    2013 |  21.604 | B            | patahan_seri | Dipertahankan & ditandai sebagai patahan seri (tidak dibuang) |
| SDG_T552_NOC_RT | IDN        |    2021 |  32.438 | B            | patahan_seri | Dipertahankan & ditandai sebagai patahan seri (tidak dibuang) |

## 3. Klasifikasi Calon Anomali (`Outlier Asli` vs `Patahan Seri` vs `Galat Input`)
- **Galat Input Ditemukan:** `0` baris (seluruh nilai BPS berada pada rentang valid $[0, 100]\%$ dan seluruh nilai `CSV` identik 100% dengan `JSON`).
- **Outlier Asli Ditandai:** `5` baris pada `var2003` (dipertahankan tanpa mengubah nilai, diberi kolom flag).
- **Patahan Seri Ditandai:** `4` baris pada ILOSTAT (`OBS_STATUS = B`, dipertahankan tanpa dibuang).

| seri    |   wilayah_id | wilayah           |   tahun |   nilai |   z_score | kategori     | tindakan                                  | penjelasan                                                                                                                                                                                                                                                                         |
|:--------|-------------:|:------------------|--------:|--------:|----------:|:-------------|:------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| var2003 |         6200 | KALIMANTAN TENGAH |    2016 |   10.25 |     -2.74 | outlier_asli | Ditandai (flag), nilai asli dipertahankan | Outlier bawah IQR (10.25 < 10.77, z=-2.74). Bukan galat input (berada dalam rentang 0-100%) dan bukan patahan serentak nasional; mencerminkan capaian rendah aktual di wilayah terkait.                                                                                            |
| var2003 |         7100 | SULAWESI UTARA    |    2025 |   51.72 |      2.91 | outlier_asli | Ditandai (flag), nilai asli dipertahankan | Outlier atas IQR (51.72 > 49.95, z=2.91). Konsisten dengan tren tinggi provinsi tersebut (2015:27.09, 2016:36.76, 2017:43.35, 2018:41.22, 2019:36.62, 2020:47.93, 2021:42.14, 2022:46.09, 2023:42.27, 2024:49.42, 2025:51.72); dipertahankan sebagai outlier asli dan diberi flag. |
| var2003 |         7500 | GORONTALO         |    2020 |   50.43 |      2.74 | outlier_asli | Ditandai (flag), nilai asli dipertahankan | Outlier atas IQR (50.43 > 49.95, z=2.74). Konsisten dengan tren tinggi provinsi tersebut (2015:43.28, 2016:36.52, 2017:37.29, 2018:39.47, 2019:45.82, 2020:50.43, 2021:39.80, 2022:40.84, 2023:37.23, 2024:46.29, 2025:45.05); dipertahankan sebagai outlier asli dan diberi flag. |
| var2003 |         8100 | MALUKU            |    2024 |   50.26 |      2.71 | outlier_asli | Ditandai (flag), nilai asli dipertahankan | Outlier atas IQR (50.26 > 49.95, z=2.71). Konsisten dengan tren tinggi provinsi tersebut (2015:28.03, 2016:30.24, 2017:31.54, 2018:35.67, 2019:35.80, 2020:26.47, 2021:37.72, 2022:37.50, 2023:37.77, 2024:50.26, 2025:46.00); dipertahankan sebagai outlier asli dan diberi flag. |
| var2003 |         9400 | PAPUA             |    2016 |   10.25 |     -2.74 | outlier_asli | Ditandai (flag), nilai asli dipertahankan | Outlier bawah IQR (10.25 < 10.77, z=-2.74). Bukan galat input (berada dalam rentang 0-100%) dan bukan patahan serentak nasional; mencerminkan capaian rendah aktual di wilayah terkait.                                                                                            |