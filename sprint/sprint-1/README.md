# Sprint 1 — Tim 10, Kasus Kesetaraan Gender

## Sprint Goal

Menghasilkan Silver pertama Kasus 10 yang dapat direproduksi dari snapshot BPS, ILOSTAT, dan World Bank WDI, dengan jejak sumber setiap observasi, keputusan kualitas data yang terdokumentasi, dan validasi dasar yang lulus. Siapkan pemuatan SQLite dan tabel pembanding nasional sebagai dasar pekerjaan Sprint 2.

## Standup mingguan

Gunakan satu utas Sprint 1 di Papan Tim. Setiap anggota menulis tiga baris berisi hasil minggu ini dan tautan bukti, pekerjaan berikutnya, serta hambatan atau bantuan yang dibutuhkan. Koordinator mencatat hambatan yang perlu ditindaklanjuti dan memeriksa kelengkapan Log Sprint sebelum **23 November 2026 pukul 23.59 WIB**.

| NIM | Kontribusi yang ditautkan saat memeriksa log |
| --- | --- |
| 124450070 | [Ekstraksi dan lineage](../../src/ekstraksi/__init__.py) |
| 124450062 | [Profil dan pembersihan](../../reports/anomali_deduplikasi_tugas8.md) |
| 124450130 | [Kamus data Silver](../../docs/data-dictionary.md) |
| 124450082 | [Catatan koordinator](124450082.md), [pemuatan SQLite](../../reports/penyimpanan_silver_tahap5.md), dan [persiapan rekonsiliasi](../../reports/rekonsiliasi_nasional_kasus10.md) |
| 124450051 | [Validasi Silver pertama](../../reports/validasi.md) |

Status Log Sprint anggota diperiksa pada Papan Tim. Tautan di atas menunjukkan bukti kontribusi di repo.

## Jejak Definition of Done

| Butir | Bukti |
| --- | --- |
| Sprint Goal Sprint 1 | Teks tujuan di atas untuk dicatat di Papan Tim. |
| Log Sprint semua anggota | Lima entri tiga baris, masing-masing atas nama anggota terkait. Status pengisian perlu diperiksa di Papan Tim. |
| Demo Sprint 1 paling lambat 22 November 2026 WIB | [Video demo Sprint 1 (MP4)](demo-sprint-1.mp4) menampilkan keluaran aktual pemeriksaan Silver, pemuatan SQLite, dan irisan pasangan nasional. Status unggah perlu diperiksa di Papan Tim. |
| Hasil Sprint 1 bisa ditelusuri | [Silver pertama](../../data/silver/silver.parquet), [validasi dasar 5/5](../../reports/validasi.md), [log keputusan](../../log-keputusan.csv), dan [laporan tim](../../reports/tim.md). |

Saat menautkan bukti di Papan Tim, cantumkan tautan commit dan berkas yang menunjukkan hasil setiap butir.
