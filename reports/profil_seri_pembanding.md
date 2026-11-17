# Profil Seri Pembanding Nasional (Tugas #6)

Dokumen ini menyajikan hasil profiling empat seri pembanding nasional dari **ILOSTAT** (`SDG_0552_NOC_RT`, `SDG_T552_NOC_RT`) dan **World Bank WDI** (`SG.GEN.PARL.ZS`, `SP.M18.2024.FE.ZS`) pada cakupan wilayah **Indonesia (`IDN`)**, meliputi ketersediaan periode, rincian disaggregasi (jenis kelamin, kelompok umur, wilayah/daerah, dan klasifikasi), satuan pengukuran, serta tahun yang beririsan dengan seri utama BPS (`var1360` dan `var2003`, periode **2015–2025**).

## 1. Acuan Seri Utama (BPS)

| Kode Seri | Indikator Utama | Cakupan Wilayah | Satuan | Periode Tersedia (Kode Tahun BPS) |
| :--- | :--- | :--- | :--- | :--- |
| `var1360` | Proporsi kursi yang diduduki perempuan di parlemen tingkat pusat dan daerah (SDG 5.5.1) | 34–38 Provinsi + Nasional (`9999`) | Persen (`%`) | 2015–2025 (`115`–`125`, 11 tahun) |
| `var2003` | Proporsi perempuan yang berada di posisi manajerial (SDG 5.5.2) | 34–38 Provinsi + Nasional (`9999`) | Persen (`%`) | 2015–2025 (`115`–`125`, 11 tahun) |

## 2. Tabel Ketersediaan Seri × Periode × Rincian (`IDN`)

| Kode Seri | Sumber | Wilayah | Rincian (Jenis Kelamin, Umur, Daerah, Klasifikasi) | Satuan | Periode Tersedia | Tahun Beririsan dgn Seri Utama (2015–2025) | Rentang Nilai |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SDG_0552_NOC_RT` | ILOSTAT | IDN (Indonesia) | Measure: `SDG_0552_RT`; Klasifikasi: `NOC` (Agregat Total / Tanpa Rincian Sub-kategori); Jenis Kelamin: Perempuan (rasio terhadap total); Level: Nasional (`IDN`) | Persen (`PT` / `RT`) | 2007–2023 (5 obs) | 2023 (**1 thn**) | 15.815 – 24.895 |
| `SDG_T552_NOC_RT` | ILOSTAT | IDN (Indonesia) | Measure: `SDG_T552_RT`; Klasifikasi: `NOC` (Agregat Total / Tanpa Rincian Sub-kategori); Jenis Kelamin: Perempuan (rasio terhadap total); Level: Nasional (`IDN`) | Persen (`PT` / `RT`) | 2007–2023 (15 obs) | 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023 (**8 thn**) | 19.204 – 44.78 |
| `SG.GEN.PARL.ZS` | World Bank WDI | IDN (Indonesia) | Jenis Kelamin: Perempuan (`Female`); Lingkup: Parlemen Nasional (Single/Lower House); Umur/Daerah: Agregat Nasional (`IDN`) | Persen (`%`, kode indikator `.ZS`) | 1997–2025 (28 obs) | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 (**11 thn**) | 8.0 – 21.913 |
| `SP.M18.2024.FE.ZS` | World Bank WDI | IDN (Indonesia) | Jenis Kelamin: Perempuan (`Female`); Kelompok Umur: 20–24 tahun (menikah pertama kali sebelum usia 18 tahun); Daerah: Agregat Nasional (`IDN`) | Persen (`%`, kode indikator `.ZS`) | 1987–2017 (8 obs) | 2017 (**1 thn**) | 16.3 – 35.1 |

## 3. Rincian Daftar Tahun Observasi & Catatan Kualitas Data

- **`SDG_0552_NOC_RT`** (ILOSTAT): Tahun tersedia = `[2007, 2008, 2009, 2010, 2023]`. *Sumber survei: LFS - National Labour Force Survey; Break in series pada tahun [2008]*.
- **`SDG_T552_NOC_RT`** (ILOSTAT): Tahun tersedia = `[2007, 2008, 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023]`. *Sumber survei: LFS - National Labour Force Survey; Break in series pada tahun [2008, 2013, 2021]*.
- **`SG.GEN.PARL.ZS`** (World Bank WDI): Tahun tersedia = `[1997, 1998, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]`. *Nama resmi: Proportion of seats held by women in national parliaments (%) (total record IDN mentah: 66, non-null: 28)*.
- **`SP.M18.2024.FE.ZS`** (World Bank WDI): Tahun tersedia = `[1987, 1991, 1994, 1997, 2003, 2007, 2012, 2017]`. *Nama resmi: Women who were first married by age 18 (% of women ages 20-24) (total record IDN mentah: 66, non-null: 8)*.

## 4. Penandaan Kandidat Rincian yang Sebanding (Untuk Tahap Integrasi)

| Kode Seri Pembanding | Pasangan Seri Utama BPS | Status Kandidat | Rincian Dipilih untuk Integrasi | Alasan Metodologis |
| :--- | :--- | :--- | :--- | :--- |
| **`SG.GEN.PARL.ZS`** (WDI) | `var1360` (Proporsi Kursi Perempuan di Parlemen) | **[TERPILIH] KANDIDAT SEBANDING UTAMA** | `countryiso3code=IDN`, Perempuan (`Female`), Agregat Parlemen Nasional, Satuan Persen (`%`) | Mengukur *Proportion of seats held by women in national parliaments (%)* yang selaras secara definisi dengan `var1360` level nasional (`wilayah_id=9999`), menggunakan satuan persen yang sama, dan memiliki **irisan penuh 11 tahun (2015–2025)** tanpa jeda. |
| **`SDG_T552_NOC_RT`** (ILOSTAT) | `var2003` (Proporsi Perempuan di Posisi Manajerial) | **[TERPILIH] KANDIDAT SEBANDING UTAMA** | `REF_AREA=IDN`, `MEASURE=SDG_T552_RT`, Agregat Total (`NOC`), Satuan Persen (`PT`) | Mengukur proporsi perempuan dalam posisi manajerial total (*Total management*, ISCO-08 kategori 1) dari survei Sakernas (*LFS*) dalam satuan persen, sebanding dengan `var2003` level nasional (`wilayah_id=9999`) dengan **8 tahun beririsan (2015–2017, 2019–2023)**. Perlu catatan *break in series* tahun 2021 saat analisis tren. |
| **`SDG_0552_NOC_RT`** (ILOSTAT) | `var2003` (Proporsi Perempuan di Posisi Manajerial) | **[CADANGAN / SEKUNDER] SEBANDING SECARA KONSEP, MINIM IRISAN** | `REF_AREA=IDN`, `MEASURE=SDG_0552_RT`, Agregat Total (`NOC`), Satuan Persen (`PT`) | Mengukur proporsi perempuan di posisi manajerial senior dan menengah (*Senior and middle management*, ISCO-08 sub-kategori 11–13) dalam satuan persen. Definisi lebih sempit dibanding `SDG_T552_NOC_RT` dan **hanya beririsan 1 tahun (`2023`)** dengan periode seri utama BPS (2015–2025), sehingga hanya dipakai sebagai pembanding titik tahun 2023. |
| **`SP.M18.2024.FE.ZS`** (WDI) | *Tidak ada pasangan (`var1360` maupun `var2003`)* | **[DIKECUALIKAN] BUKAN KANDIDAT SEBANDING** | — (Tidak digabungkan ke tabel integrasi) | Mengukur *Women who were first married by age 18 (% of women ages 20–24)* (SDG 5.3.1), yaitu prevalensi perkawinan anak pada kelompok umur 20–24 tahun. Tidak relevan secara konseptual dengan representasi politik (`var1360`) maupun kepemimpinan manajerial (`var2003`), serta hanya memiliki 1 titik irisan (`2017`). |
