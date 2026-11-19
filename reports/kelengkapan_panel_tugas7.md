# Laporan Kelengkapan Panel Provinsi × Periode (Tugas #7)

## 1. Aturan Pemetaan Wilayah & Pemisahan Nasional
- **Pemetaan Wilayah:** Mengacu pada keputusan `K-001` (`log-keputusan.csv`), seluruh kode wilayah diselaraskan ke standar **38 provinsi BPS (kode 2-digit × 100)**.
- **Pemisahan Nasional:** Baris dengan `wilayah_kode = 9999` (**Indonesia**) dipisahkan dari tabel panel provinsi agar tidak terjadi penghitungan ganda (*double counting*) saat agregasi.
- **Definisi Missing vs Belum Terbit:** Empat provinsi Daerah Otonomi Baru (DOB) Papua hasil pemekaran tahun 2022 (`9200` Papua Barat Daya, `9500` Papua Selatan, `9600` Papua Tengah, `9700` Papua Pegunungan) belum memiliki entitas administratif sebelum tahun 2023. Oleh karena itu, sel kosong pada 4 provinsi tersebut untuk tahun `< 2023` diklasifikasikan sebagai **belum terbit (structural)** dan **bukan missing**.

## 2. Kelengkapan Panel Seri `var1360`
- **Rentang Periode:** 2015–2025 (11 tahun)
- **Total Grid (38 provinsi × 11 tahun):** 418 sel
- **Sel Terisi (Masuk Silver):** 382 sel
- **Sel Belum Terbit (4 DOB Papua < 2023):** 32 sel
- **Sel Missing Aktual:** 4 sel

| Tahun | Total Grid | Prov. Aktif | Terisi | Belum Terbit (DOB) | Missing Aktual | Kelengkapan vs 38 Prov (%) | Kelengkapan vs Prov. Aktif (%) | Nasional (9999) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2015 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2016 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2017 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2018 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2019 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2020 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2021 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2022 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2023 | 38 | 38 | 34 | 0 | 4 | 89.47% | 89.47% | Ada |
| 2024 | 38 | 38 | 38 | 0 | 0 | 100.00% | 100.00% | Ada |
| 2025 | 38 | 38 | 38 | 0 | 0 | 100.00% | 100.00% | Ada |

### Rincian Sel Missing Aktual (`var1360`)
| Kode Wilayah | Nama Provinsi | Tahun |
| :---: | :--- | :---: |
| 9200 | Papua Barat Daya | 2023 |
| 9500 | Papua Selatan | 2023 |
| 9600 | Papua Tengah | 2023 |
| 9700 | Papua Pegunungan | 2023 |

## 2. Kelengkapan Panel Seri `var2003`
- **Rentang Periode:** 2015–2025 (11 tahun)
- **Total Grid (38 provinsi × 11 tahun):** 418 sel
- **Sel Terisi (Masuk Silver):** 380 sel
- **Sel Belum Terbit (4 DOB Papua < 2023):** 32 sel
- **Sel Missing Aktual:** 6 sel

| Tahun | Total Grid | Prov. Aktif | Terisi | Belum Terbit (DOB) | Missing Aktual | Kelengkapan vs 38 Prov (%) | Kelengkapan vs Prov. Aktif (%) | Nasional (9999) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2015 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2016 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2017 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2018 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2019 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2020 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2021 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2022 | 38 | 34 | 34 | 4 | 0 | 89.47% | 100.00% | Ada |
| 2023 | 38 | 38 | 34 | 0 | 4 | 89.47% | 89.47% | Ada |
| 2024 | 38 | 38 | 38 | 0 | 0 | 100.00% | 100.00% | Ada |
| 2025 | 38 | 38 | 36 | 0 | 2 | 94.74% | 94.74% | Ada |

### Rincian Sel Missing Aktual (`var2003`)
| Kode Wilayah | Nama Provinsi | Tahun |
| :---: | :--- | :---: |
| 9200 | Papua Barat Daya | 2023 |
| 9500 | Papua Selatan | 2023 |
| 9600 | Papua Tengah | 2023 |
| 9600 | Papua Tengah | 2025 |
| 9700 | Papua Pegunungan | 2023 |
| 9700 | Papua Pegunungan | 2025 |
