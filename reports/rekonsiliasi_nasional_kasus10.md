# Persiapan tahap 6 — Rekonsiliasi nasional Kasus 10

[Tabel nasional](../data/gold/rekonsiliasi_nasional_kasus10.csv) memuat enam seri dalam 31 periode tahunan. Tahun yang memiliki minimal satu nilai dipertahankan. Sel kosong berarti snapshot tidak menyediakan observasi untuk seri dan tahun itu. Semua nilai dinyatakan dalam persen dan dipertahankan sesuai hasil ekstraksi.

## Pasangan dan keterbandingan

| Seri BPS (Indonesia) | Pembanding | Tahun dengan nilai pada kedua seri | Catatan keterbandingan |
| --- | --- | --- | --- |
| `var2003` | ILO `SDG_T552_NOC_RT` | 2015–2017, 2019–2023 (8) | Pembanding utama. DSD mencakup seluruh manajemen, yaitu golongan utama 1 ISCO-08 atau ISCO-88. Cakupannya paling dekat dengan seri Sakernas BPS, yang menyebut posisi manajerial lintas lapangan usaha KBLI 2015 tanpa pembatasan tingkat jabatan dalam metadata snapshot. KBLI mengklasifikasikan lapangan usaha, sehingga catatan BPS itu sendiri belum membuktikan kesamaan kode pekerjaan. ILO mengolah mikrodata LFS dan mencatat perubahan metodologi pada 2008, 2013, dan 2021 (`OBS_STATUS=B`). Nilai 2016 tetap 44,78% pada ILO dan 23,60% pada BPS. |
| `var2003` | ILO `SDG_0552_NOC_RT` | 2023 (1) | Pembanding sekunder untuk manajemen senior dan menengah. DSD mengeluarkan kelompok 14 dari ISCO-08 atau kelompok 13 dari ISCO-88, sehingga pembilang dan penyebut lebih sempit. ILO menandai perubahan metodologi pada 2008. Pada 2023, ILO mencatat 24,895% untuk senior dan menengah dan 33,133% untuk seluruh manajemen. BPS mencatat 35,02%. |
| `var1360` | WDI `SP.M18.2024.FE.ZS` | 2017 (1) | Penyebutnya perempuan umur 20–24 tahun. BPS Susenas menghitung perkawinan pertama atau awal hidup bersama sebelum ulang tahun ke-18. Label ringkas WDI memakai *by age 18*, dan metadata sumbernya merujuk UNICEF `PT_F_20-24_MRD_U18` (*before age 18*) serta DHS dengan ambang usia tepat 18 tahun. Ambang operasional sebanding, dengan kemungkinan perbedaan pengukuran dan survei. Nilai 2017 adalah 11,54% (BPS) dan 16,30% (WDI). [BPS](https://www.bps.go.id/en/statistics-table/2/MTM2MCMy/pr) · [Metadata WDI](https://databank.worldbank.org/metadataglossary/health-nutrition-and-population-statistics/series/SP.M18.2024.FE.ZS) · [UNICEF](https://data.unicef.org/topic/child-protection/child.marriage/) |

Definisi manajemen dan peringatan tentang perbedaan sumber atau tahun rujukan dibaca dari deskripsi DSD kedua seri. Catatan perubahan metodologi berasal dari `NOTE_INDICATOR` pada CSV observasi ILO. [Metodologi ILOSTAT](https://ilostat.ilo.org/methods/concepts-and-definitions/description-sustainable-development-labour-market-indicators/)

`SG.GEN.PARL.ZS` memberi konteks keterwakilan perempuan di parlemen nasional (kamar tunggal atau kamar rendah, berdasarkan data IPU). Seri ini hadir sebagai kolom konteks di tabel. `var1360` adalah indikator perkawinan anak SDG 5.3.1, sehingga pemetaan pasangan di laporan persiapan ini mengikuti metadata BPS asli. [Metadata WDI untuk parlemen](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SG.GEN.PARL.ZS)

## Rincian ekstraksi dan reproduksi

- BPS menggunakan CSV `sdg5_5_5_2_v2003.csv` dan `sdg5_5_3_1_v1360.csv` dengan `wilayah_id=9999`, `turvar_id=0` dan `periode_id=0` (tahunan). Definisi diambil dari berkas JSON pendamping.
- ILO menggunakan CSV `DF_SDG_T552_NOC_RT.csv` dan `DF_SDG_0552_NOC_RT.csv` dengan `REF_AREA=IDN`, `FREQ=A`, `UNIT_MEASURE=PT`, `UNIT_MULT=0`, sumber `LFS - National Labour Force Survey`, dan `MEASURE` masing-masing `SDG_T552_RT` dan `SDG_0552_RT`. DSD kedua seri ada di folder `dsd/` snapshot ILO.
- WDI menggunakan `kelompok-05-hal-01.json` dan `kelompok-07-hal-01.json` dengan `countryiso3code=IDN` dan kode indikator persis seperti di tabel. Tahun dengan nilai null dikeluarkan dari seri.

```sh
python unduh_data.py --kasus 10
python -m src.gold.rekonsiliasi
python -m src.common.hasil 124450082 pasangan_rekonsiliasi=3 periode_beririsan=8
```

`periode_beririsan` menghitung tahun unik yang memiliki nilai pada kedua sisi minimal satu pasangan. Tahun 2017 dan 2023 masing-masing muncul pada dua pasangan. Ada 10 observasi pasangan-tahun pada 8 tahun unik. Seri parlemen berada di luar perhitungan metrik pasangan.

Sumber data adalah Badan Pusat Statistik, ILOSTAT (CC BY 4.0), dan World Bank, World Development Indicators (CC BY 4.0), snapshot 20 Oktober 2026 dari paket Kasus 10. Tabel turunan berlisensi [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
