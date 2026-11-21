
# Laporan Tim 10 — Kasus 10: Kesetaraan Gender (SDG 5)

## Ringkasan

Tim 10 mengolah data indikator kesetaraan gender dari sumber BPS, World Development Indicators (WDI), dan ILOSTAT. Pengolahan mencakup ekstraksi data mentah, profiling, penanganan masalah kualitas data, penyusunan data Silver, serta rekonsiliasi indikator nasional. Hasil pengolahan menghasilkan 840 baris data Silver yang mencakup 6 seri dan 39 wilayah. Data Gold disimpan dalam `data/gold/rekonsiliasi_nasional_kasus10.csv`.

## Data dan lineage

Data mentah berasal dari tiga sumber:

| Sumber | Berkas yang dibaca | Format |
|---|---:|---|
| BPS | 4 | CSV dan JSON |
| WDI | 5 | JSON |
| ILOSTAT | 5 | CSV dan JSON |

Sebanyak 14 berkas sumber dibaca oleh komponen ekstraksi. Setiap tabel hasil pembacaan dilengkapi atribut `_berkas_raw` dan `_sha256_raw` untuk mempertahankan informasi asal data dan integritas berkas.

Hasil ekstraksi menggabungkan 1.799 baris dengan 61 kolom. Data mentah dipertahankan tanpa melakukan pembersihan pada tahap ekstraksi. Informasi keputusan dan perubahan data dicatat dalam `log-keputusan.csv` dengan 14 keputusan, yaitu K-001 sampai K-014.

## Masalah data dan penanganannya

Permasalahan kualitas data ditangani melalui tahap profiling, pencatatan anomali, dan keputusan pembersihan. Rincian pemeriksaan dan penanganannya tersedia pada artefak berikut:

| Pemeriksaan | Artefak pendukung |
|---|---|
| Profil seri utama | `reports/profil_seri_utama.md` |
| Profil seri pembanding | `reports/profil_seri_pembanding.md` |
| Anomali dan duplikasi | `reports/anomali_deduplikasi_tugas8.md` |
| Keputusan penanganan | `log-keputusan.csv` |

Salah satu temuan penting adalah ketidaksesuaian metadata pada seri BPS `var1360`. Metadata mentahnya menunjukkan indikator perkawinan anak (SDG 5.3.1), sehingga tidak dapat langsung dianggap sebagai indikator keterwakilan perempuan di parlemen. Seri tersebut perlu dibedakan berdasarkan definisi indikator dan sumbernya agar tidak terjadi kesalahan interpretasi.

Setiap keputusan penanganan dicatat beserta alasan dan dampaknya agar proses pembersihan dapat ditelusuri kembali.

## Integrasi dan rekonsiliasi

Integrasi dilakukan dengan membedakan seri utama dan seri pembanding berdasarkan definisi indikator, sumber, serta cakupan datanya. Data WDI digunakan sebagai salah satu sumber pembanding, termasuk seri `SP.M18.2024.FE.ZS`.

Hasil rekonsiliasi nasional disimpan pada:

`data/gold/rekonsiliasi_nasional_kasus10.csv`

Rincian hasil perbandingan dan penjelasan rekonsiliasi tersedia pada `reports/rekonsiliasi_nasional_kasus10.md`. Perbedaan antarseri tidak langsung dianggap sebagai kesalahan data karena dapat dipengaruhi oleh perbedaan definisi, metode pengukuran, vintage, dan granularitas.

## Validasi dan reproduksibilitas

Validasi dasar telah menghasilkan 5 dari 5 pemeriksaan lolos. Artefak aturan dan hasil validasi tersedia pada `reports/validasi.md`.

Hasil pengolahan juga didukung oleh:
- Data Silver sebanyak 840 baris, 6 seri, dan 39 wilayah.
- Data Gold pada `data/gold/rekonsiliasi_nasional_kasus10.csv`.
- Catatan keputusan pada `log-keputusan.csv`.
- Informasi lineage dari `_berkas_raw` dan `_sha256_raw`.

Keterbatasan yang perlu diperhatikan adalah perbedaan definisi dan cakupan antarseri. Oleh karena itu, perbandingan indikator harus mempertimbangkan metadata dan sumber data masing-masing.

## Pembagian kerja

| Anggota | NIM | Komponen | Tugas sampingan |
|---|---|---|---|
| Fitra Pratama Mega | 124450070 | Ekstraksi dan lineage | Analis utama |
| Fadya Izzatul 'Aini | 124450051 | Profil dan pembersihan | Penjaga data dan evaluasi |
| Ahmad Zidane Rabbaanee | 124450062 | Transformasi dan panel | Integrator |
| Sekar Dini Widya Putri | 124450082 | Integrasi, penyimpanan, dan skala | Koordinator |
| Najla Nursyifa | 124450130 | Validasi dan dokumentasi | Reproduksi dan demo |

