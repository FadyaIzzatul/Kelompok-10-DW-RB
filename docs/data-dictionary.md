# Data dictionary — <Nama tim>

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | |
| wilayah_kode | int | kode BPS x 100 | tidak | 9999 atau 1100–9600 | log K-… | |

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

## Hasil audit metadata seri

| Kode seri | Kode SDG | Satuan | Jenis periode | Dasar penetapan |
|---|---|---|---|---|
| var1360 | 5.3.1 | Persen | tahun | Metadata JSON dan CSV BPS |
| var2003 | 5.5.2 | Persen | tahun | Definisi indikator dan skala observasi BPS |
| SDG_0552_NOC_RT | 5.5.2 | Persen | tahun | DSD ILO dan UNIT_MEASURE PT |
| SDG_T552_NOC_RT | 5.5.2 | Persen | tahun | DSD ILO dan UNIT_MEASURE PT |
| SG.GEN.PARL.ZS | 5.5.1 | Persen | tahun | Metadata WDI dan metadata SDG UN |
| SP.M18.2024.FE.ZS | 5.3.1 | Persen | tahun | Metadata WDI dan metadata SDG UN |

## Catatan periode

Seluruh seri menggunakan periode tahunan.
Tidak dilakukan konversi periode tahunan menjadi semester
atau bulanan.

## Catatan lineage

Setiap observasi tetap merujuk pada berkas mentah
dan SHA256 yang tercatat pada data/raw/MANIFEST.csv.

Koreksi metadata katalog dicatat pada log-keputusan.csv.