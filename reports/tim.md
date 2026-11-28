
# Laporan Tim 10 — Kasus 10: Kesetaraan Gender (SDG 5)

## Ringkasan

Tim 10 mengolah data indikator kesetaraan gender (SDG 5) dari tiga sumber, yaitu Badan Pusat Statistik (BPS), World Development Indicators (WDI), dan ILOSTAT. Kasus ini mencakup dua indikator utama, yaitu perkawinan anak perempuan (SDG 5.3.1) dan proporsi perempuan pada posisi manajerial (SDG 5.5.2).

Seri utama tingkat provinsi terdiri atas `var1360` dari BPS untuk indikator perkawinan anak perempuan dan `var2003` dari BPS untuk indikator perempuan pada posisi manajerial. Data pembanding nasional berasal dari WDI dan ILOSTAT. Hasil pengolahan menghasilkan **840 baris data Silver, 6 seri, dan 39 wilayah**. Temuan utama menunjukkan bahwa perbedaan definisi indikator, cakupan wilayah, format, dan status pengamatan perlu diperhatikan agar integrasi data tidak menghasilkan interpretasi yang keliru.

## Data dan lineage

Data mentah berasal dari tiga sumber dengan rincian berikut.

| Sumber | Berkas yang dibaca | Format |
|---|---:|---|
| BPS | 4 | CSV dan JSON |
| WDI | 5 | JSON |
| ILOSTAT | 5 | CSV dan JSON |
| **Total** | **14** | **CSV dan JSON** |

Berdasarkan `data/raw/MANIFEST.csv`, terdapat 15 berkas dalam manifest. Satu berkas tambahan berupa `manifest_asal.json` merupakan catatan asal unduhan, bukan tabel sumber yang dibaca oleh komponen ekstraksi. Dengan demikian, terdapat 14 berkas sumber yang diproses.

Setiap tabel hasil pembacaan dilengkapi dua atribut lineage, yaitu `_berkas_raw` dan `_sha256_raw`. Atribut `_berkas_raw` menyimpan informasi berkas asal, sedangkan `_sha256_raw` menyimpan hash SHA-256 untuk memeriksa integritas dan memastikan asal data dapat ditelusuri kembali.

Hasil penggabungan ekstraksi dari ketiga sumber menghasilkan **1.799 baris dengan 61 kolom**. Data mentah dipertahankan tanpa pembersihan pada tahap ekstraksi. Perubahan data dilakukan pada tahap berikutnya dan dicatat dalam `log-keputusan.csv`, yang memuat 14 keputusan dari K-001 sampai K-014.

Snapshot data mentah yang digunakan bertanggal 20 Oktober 2026. Setiap perubahan hasil tarik ulang API perlu dibandingkan dengan snapshot tersebut berdasarkan isi data dan hash berkas, bukan hanya berdasarkan waktu pengunduhan.

## Masalah data dan penanganannya

Pemeriksaan kualitas data dilakukan melalui profiling seri utama dan pembanding, pemeriksaan anomali, serta pencatatan keputusan pembersihan. Beberapa aspek yang diperhatikan meliputi:

| Aspek pemeriksaan | Temuan dan penanganan |
|---|---|
| Metadata indikator | `var1360` merupakan indikator perkawinan anak perempuan (SDG 5.3.1), sedangkan `var2003` merupakan indikator perempuan pada posisi manajerial (SDG 5.5.2). Keduanya dibedakan berdasarkan definisi indikator. |
| Missing data | Kelengkapan pengamatan diperiksa berdasarkan seri, tahun, dan wilayah. Nilai yang tidak tersedia tidak langsung dianggap sebagai nol. |
| Outlier | Nilai pengamatan diperiksa berdasarkan rentang dan konteks indikator sebelum ditentukan penanganannya. |
| Patahan seri | Status pengamatan ILOSTAT dari struktur SDMX dipertahankan sebagai informasi penting agar perubahan atau patahan seri tidak hilang saat pengolahan. |
| Duplikasi | Pemeriksaan dilakukan untuk mengidentifikasi pengamatan yang tercatat lebih dari satu kali berdasarkan kunci data. |
| Format data | Data BPS, WDI, dan ILOSTAT memiliki struktur dan format berbeda sehingga perlu diseragamkan sebelum integrasi. |
| Wilayah | Pemetaan wilayah diperiksa agar identitas wilayah konsisten, terutama dalam penyusunan data tingkat provinsi. |

Keputusan yang mengubah, membuang, menambah, atau menafsirkan data dicatat dalam `log-keputusan.csv`. Terdapat 14 keputusan, yaitu K-001 sampai K-014. Setiap keputusan memuat alasan, alternatif yang ditolak, dan dampak terhadap jumlah baris melalui kolom `dampak_baris`.

Artefak pendukung pemeriksaan meliputi:

- `reports/profil_seri_utama.md`
- `reports/profil_seri_pembanding.md`
- `reports/anomali_deduplikasi_tugas8.md`
- `log-keputusan.csv`

Dengan pencatatan tersebut, proses penanganan masalah data dapat ditelusuri kembali berdasarkan keputusan yang telah dibuat.

## Integrasi dan rekonsiliasi

Integrasi dilakukan dengan membedakan seri utama tingkat provinsi dan seri pembanding nasional. Seri utama berasal dari BPS, yaitu `var1360` untuk SDG 5.3.1 dan `var2003` untuk SDG 5.5.2.

Seri pembanding nasional yang digunakan meliputi:

| Sumber | Kode seri | Keterangan |
|---|---|---|
| WDI | `SP.M18.2024.FE.ZS` | Pembanding indikator perkawinan anak perempuan |
| WDI | `SG.GEN.PARL.ZS` | Konteks proporsi perempuan di parlemen |
| ILOSTAT | `SDG_0552_NOC_RT` | Pembanding indikator SDG 5.5.2 |
| ILOSTAT | `SDG_T552_NOC_RT` | Definisi pembanding ILO lainnya untuk SDG 5.5.2 |

Kedua seri ILOSTAT tidak langsung digabungkan karena memiliki definisi yang perlu diperiksa melalui metadata dan Data Structure Definition (DSD). Pemilihan seri pembanding harus mempertimbangkan kesesuaian definisinya dengan data BPS.

Hasil rekonsiliasi nasional disimpan pada `data/gold/rekonsiliasi_nasional_kasus10.csv`, sedangkan penjelasan hasil perbandingan tersedia pada `reports/rekonsiliasi_nasional_kasus10.md`.

Perbedaan nilai antarseri perlu dianalisis berdasarkan definisi indikator, metode pengukuran, periode pembaruan atau vintage, serta cakupan dan granularitas data. Oleh karena itu, selisih antarseri tidak langsung dianggap sebagai kesalahan data. Khusus indikator perkawinan anak, batas umur yang digunakan pada seri BPS dan WDI perlu diperhatikan sebelum dilakukan perbandingan.

### Hasil Rekonsiliasi dan Analisis Selisih

Rekonsiliasi dilakukan dengan membandingkan seri utama BPS dengan seri pembanding nasional dari ILOSTAT dan WDI pada periode yang memiliki data di kedua sumber. Selisih dihitung menggunakan rumus nilai BPS dikurangi nilai pembanding dan dinyatakan dalam poin persentase (pp).

| Pasangan seri | Periode | Nilai BPS (%) | Nilai pembanding (%) | Selisih (pp) | Kategori |
|---|---:|---:|---:|---:|---|
| `var2003` – `SDG_T552_NOC_RT` | 2015 | 22,320 | 22,379 | -0,059 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2016 | 23,600 | 44,780 | -21,180 | Tidak terjelaskan |
| `var2003` – `SDG_T552_NOC_RT` | 2017 | 26,560 | 27,459 | -0,899 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2019 | 30,370 | 29,567 | +0,803 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2020 | 33,080 | 32,614 | +0,466 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2021 | 32,500 | 32,438 | +0,062 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2022 | 32,260 | 31,665 | +0,595 | Definisi |
| `var2003` – `SDG_T552_NOC_RT` | 2023 | 35,020 | 33,133 | +1,887 | Definisi |
| `var2003` – `SDG_0552_NOC_RT` | 2023 | 35,020 | 24,895 | +10,125 | Definisi |
| `var1360` – `SP.M18.2024.FE.ZS` | 2017 | 11,540 | 16,300 | -4,760 | Metode |

Perbedaan pada indikator `var2003` dan `SDG_T552_NOC_RT` berkaitan dengan definisi dan cakupan pengukuran posisi manajerial pada masing-masing sumber. Selisih terbesar terjadi pada 2016, yaitu -21,180 poin persentase. Penyebab khusus perbedaan tersebut belum dapat dipastikan berdasarkan metadata yang tersedia sehingga dikategorikan tidak terjelaskan. Sementara itu, `SDG_0552_NOC_RT` memiliki cakupan senior dan middle management, berbeda dengan `SDG_T552_NOC_RT` yang mencakup total management. Oleh karena itu, kedua seri ILOSTAT dipertahankan secara terpisah.

Pada indikator perkawinan anak, perbandingan `var1360` dengan `SP.M18.2024.FE.ZS` pada 2017 menghasilkan selisih -4,760 poin persentase. Perbedaan dikategorikan sebagai metode karena data berasal dari sumber survei dan proses pengukuran yang berbeda. Indikator WDI mengukur perempuan usia 20–24 tahun yang pertama kali menikah sebelum usia 18 tahun.

Secara keseluruhan, terdapat 10 observasi perbandingan pada 8 periode unik. Seri `SG.GEN.PARL.ZS` digunakan sebagai indikator konteks keterwakilan perempuan di parlemen dan tidak dimasukkan ke dalam perhitungan selisih. Perbedaan antarseri tetap dipertahankan dan tidak dipaksakan agar bernilai sama karena setiap sumber memiliki definisi, metode, dan cakupan pengukuran masing-masing.

### Penelusuran Asal Data dan Keputusan

Setiap angka dalam hasil rekonsiliasi dapat ditelusuri melalui kombinasi kode seri dan periode pada `data/gold/tabel_nasional_gold.csv`. Tabel tersebut mencatat kolom `sumber` dan `asal_nasional` untuk menunjukkan sumber serta cakupan asal observasi, `_berkas_raw` untuk menunjukkan berkas sumber, dan `_sha256_raw` sebagai identitas hash berkas untuk pemeriksaan integritas data.

Keputusan penyeragaman kode dan satuan seri dapat diperiksa pada `log-keputusan.csv`, khususnya K-003 sampai K-007. Pemisahan definisi seri ILOSTAT tercatat pada K-018, sedangkan aturan seleksi dan pembentukan Gold tercatat pada K-015 sampai K-017. Dengan pencatatan tersebut, angka dan keputusan yang digunakan dalam rekonsiliasi dapat diperiksa kembali berdasarkan sumbernya.

## Validasi dan reproduksibilitas

Validasi dasar yang tercatat pada `reports/validasi.md` menunjukkan **5 dari 5 pemeriksaan berhasil lolos**. Pemeriksaan ini digunakan untuk memastikan data hasil pengolahan memenuhi aturan validasi yang telah ditetapkan.

Ringkasan hasil pengolahan adalah sebagai berikut.

| Komponen | Hasil |
|---|---|
| Berkas sumber yang dibaca | 14 berkas |
| Hasil ekstraksi | 1.799 baris dan 61 kolom |
| Data Silver | 840 baris |
| Jumlah seri pada Silver | 6 seri |
| Jumlah wilayah pada Silver | 39 wilayah |
| Keputusan dalam log | 14 keputusan |
| Validasi dasar | 5 dari 5 pemeriksaan lolos |

Reproduksibilitas didukung oleh penyimpanan data mentah, pencatatan lineage melalui `_berkas_raw` dan `_sha256_raw`, serta dokumentasi keputusan pada `log-keputusan.csv`. Data Silver dan Gold juga disimpan sebagai artefak hasil pengolahan sehingga proses dapat ditelusuri kembali.

Pengujian pipeline dari awal dilakukan dengan menjalankan `python unduh_data.py --kasus 10`, kemudian dilanjutkan dengan `python pipeline.py`. Waktu eksekusi dari kondisi klon bersih serta perbandingan waktu dan penggunaan memori antara pandas dengan DuckDB atau Dask perlu dicatat berdasarkan hasil pengujian aktual.

Keterbatasan yang perlu diperhatikan adalah perbedaan definisi antarseri, kemungkinan ketidaklengkapan pengamatan pada beberapa periode atau wilayah, serta perbedaan cakupan data nasional dan provinsi. Oleh karena itu, metadata dan sumber data perlu diperhatikan dalam proses integrasi maupun penarikan kesimpulan.

## Pembagian kerja

| Anggota | NIM | Komponen | Tugas sampingan |
|---|---|---|---|
| Fitra Pratama Mega | 124450070 | Ekstraksi dan lineage | Analis utama |
| Fadya Izzatul 'Aini | 124450062 | Profil dan pembersihan | Penjaga data dan evaluasi |
| Ahmad Zidane Rabbaanee | 124450130 | Transformasi dan panel | Integrator |
| Sekar Dini Widya Putri | 124450082 | Integrasi, penyimpanan, dan skala | Koordinator |
| Najla Nursyifa | 124450051 | Validasi dan dokumentasi | Reproduksi dan demo |