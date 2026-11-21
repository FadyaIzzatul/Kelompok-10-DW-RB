# Persiapan tahap 5 — Penyimpanan Silver Kasus 10

Untuk persiapan ini, SQLite dipilih untuk menyimpan salinan Silver yang dapat dikueri dengan SQL. Snapshot pertama berisi 840 observasi dan dapat dimuat ke satu berkas lokal dengan modul `sqlite3` bawaan Python. SQLite mendukung kunci primer gabungan dan transaksi, sehingga setiap pemuatan ulang mengganti snapshot secara utuh. Pilihan ini cocok untuk uji lokal dengan satu pemuat. PostgreSQL dapat dipertimbangkan jika beberapa pengguna perlu menulis ke basis data yang sama secara bersamaan.

Tabel `silver` memakai [DDL](../src/silver/silver.sql) dengan kunci primer `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)` sesuai skema tim. `wilayah_kode` bertipe `INTEGER`, `nilai` bertipe `REAL`, dan atribut lain bertipe `TEXT`. Tipe teks mempertahankan format periode seperti `2025`, `2025-S1`, `2025-Q3`, dan `2025-07`. Kolom wajib memakai `NOT NULL`. Dua kolom tambahan, `obs_status` dan `definisi_indikator`, disalin bila tersedia. `_berkas_raw` dan `_sha256_raw` membawa jejak asal data dari Parquet ke SQL.

Respons JSON mentah cocok disimpan sebagai dokumen Bronze karena satu berkas dapat mempertahankan struktur bersarang, metadata sumber, dan bentuk asli respons untuk audit atau ekstraksi ulang. Silver di SQL menyimpan satu observasi per baris dengan tipe dan kunci yang konsisten, sehingga penggabungan seri, pemeriksaan duplikat, dan agregasi dapat dilakukan langsung dengan SQL. Kedua bentuk penyimpanan dihubungkan oleh nama berkas mentah dan hash SHA-256.

## Reproduksi

Jalankan dari akar repositori setelah paket Kasus 10 tersedia. Tabel `STRICT` memerlukan SQLite 3.37 atau lebih baru dalam runtime Python.

```sh
python unduh_data.py --kasus 10
python pipeline.py
python -m src.common.skema data/silver/silver.parquet
python -m src.silver.muat_sqlite
```

Pemuat membaca `data/silver/silver.parquet` dan membuat `data/silver/silver.sqlite3`. Opsi `--parquet` dan `--basis-data` dapat memilih berkas lain. Setiap pemuatan yang berhasil mengganti seluruh isi tabel `silver` dengan snapshot masukan dalam satu transaksi. Jika penulisan gagal, transaksi mempertahankan isi tabel sebelumnya.

## Hasil uji pemuatan pertama

Uji lokal dengan SQLite 3.50.4 menghasilkan 840 observasi, terdiri dari 784 baris BPS, 20 ILOSTAT, dan 36 WDI. Tabel mencakup 6 seri, 39 wilayah (termasuk Indonesia), dan 6 berkas sumber. Pemeriksaan skema Silver dan `PRAGMA integrity_check` lulus. Pemuatan ulang tetap menghasilkan 840 baris dan seluruh nilai dari 13 kolom cocok dengan Parquet. Simulasi kegagalan saat penyisipan pada salinan uji memastikan seluruh baris sebelumnya tetap utuh.

```sql
SELECT sumber, COUNT(*) AS jumlah_observasi
FROM silver
GROUP BY sumber
ORDER BY sumber;
```
