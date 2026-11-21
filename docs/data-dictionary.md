# Data dictionary — Kelompok 10

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| `sumber` | string | — | tidak | `bps`, `ilostat`, `wdi` | nama folder `data/raw/` | Identitas instansi penyedia dataset mentah. |
| `wilayah_kode` | int | kode BPS × 100 | tidak | `9999` atau `1100`–`9600` | `log-keputusan.csv` | `9999` = Indonesia; `1100`–`9600` = kode provinsi BPS × 100. |
| `seri_kode` | string | kode seri | tidak | `var1360`, `var2003`, `SDG_0552_NOC_RT`, `SDG_T552_NOC_RT`, `SG.GEN.PARL.ZS`, `SP.M18.2024.FE.ZS` | metadata API/CSV BPS, DSD ILO, dan WDI | Kode unik indikator; tidak ada dua definisi berbeda yang berbagi kode sama. |
| `nama_wilayah` | string | teks kapital | tidak | `INDONESIA` atau nama 38 provinsi (misal `ACEH`, `SUMATERA UTARA`, `LAMPUNG`) | normalisasi nama wilayah pada `log-keputusan.csv` | Nama resmi tingkat nasional atau provinsi yang telah diseragamkan. |
| `periode` | string | `YYYY` (4 digit) | tidak | `1987`–`2025` (pola `^\d{4}$`) | kolom tahun/periode pada berkas mentah `data/raw/` | Tahun referensi pengamatan indikator. |
| `jenis_periode` | string | teks | tidak | `tahun` | penetapan frekuensi pada `log-keputusan.csv` | Seluruh seri pada Kasus 10 menggunakan frekuensi tahunan. |
| `rincian` | string | teks / kode dimensi | tidak | `Tidak ada`, `Agregat Nasional (IDN)`, `CLASSIF1=NOC;SEX=F`, dll. | ekstraksi dimensi klasifikasi pada metadata berkas mentah | Rincian sub-kelompok demografi atau klasifikasi pengamatan. |
| `nilai` | float | sesuai kolom `satuan` | tidak | `0.0`–`100.0` (untuk satuan `Persen`) | kolom nilai observasi pada berkas mentah `data/raw/` | Nilai numerik hasil observasi; Silver hanya memuat observasi yang tersedia. |
| `satuan` | string | unit ukur | tidak | `Persen` | standardisasi `UNIT_MEASURE` / metadata berkas mentah | Satuan pengukuran indikator yang telah diseragamkan. |
| `obs_status` | string | kode SDMX | ya (kosong `""`) | Kode standar DSD ILO (`A`, `B`, `E`, `F`, `I`, `L`, `M`, `O`, `P`, `Q`, `S`, `U`) atau kosong | kolom `OBS_STATUS` pada berkas mentah ILOSTAT | Penanda status/kualitas observasi khusus data ILOSTAT (kosong pada BPS/WDI). |
| `definisi_indikator` | string | teks | tidak | Deskripsi lengkap indikator sesuai katalog | metadata judul/definisi pada berkas mentah `data/raw/` | Penjelasan definisi indikator untuk memverifikasi keunikan `seri_kode`. |
| `_berkas_raw` | string | path relatif | tidak | Jalur berkas di bawah `data/raw/` (misal `bps/2026-10-20/sdg5_5_3_1_v1360.csv`) | pencatatan otomatis tahap ekstraksi (`src/ekstraksi/`) | Nama berkas mentah asal tempat observasi diekstrak. |
| `_sha256_raw` | string | hash hex (64 char) | tidak | String heksadesimal SHA-256 yang terdaftar di `data/raw/MANIFEST.csv` | checksum SHA-256 berkas mentah pada `data/raw/` | Sidik jari kriptografis untuk memverifikasi integritas berkas sumber. |

## data/gold/<tabel>.parquet

*(Kolom dataset Gold akan ditambahkan pada Sprint 2–3 setelah tahap pemodelan analitik selesai.)*

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

### Contoh Penelusuran Satu Baris Silver ke Berkas Mentah

```json
{
  "sumber": "bps",
  "seri_kode": "var1360",
  "wilayah_kode": 1100,
  "nama_wilayah": "ACEH",
  "periode": "2015",
  "jenis_periode": "tahun",
  "rincian": "Tidak ada",
  "nilai": 24.5,
  "satuan": "Persen",
  "obs_status": "",
  "definisi_indikator": "Proporsi kursi yang diduduki perempuan di parlemen tingkat pusat dan daerah",
  "_berkas_raw": "bps/2026-10-20/sdg5_5_3_1_v1360.csv",
  "_sha256_raw": "c7464fff80ae9413ac4084092f180d58c6745ba25215d38861dd411cd8c0fa0f"
}