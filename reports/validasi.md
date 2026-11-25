# Laporan Validasi Silver Pertama (Tahap 8)

- **Total Baris Silver:** `840` baris (`6` seri, `39` wilayah)
- **Pemeriksaan Skema Dasar (`src.common.skema`):** `LOLOS (0 pelanggaran)`
- **Ringkasan Aturan Validasi:** **5/5 aturan LOLOS**

| No | Nama Aturan Validasi | Status | Keterangan Hasil |
| :---: | :--- | :---: | :--- |
| 1 | `1_rentang_nilai_persen_0_100` | **LOLOS** | Diperiksa 840 baris bersatuan Persen; pelanggaran di luar [0, 100] = 0 baris. |
| 2 | `2_keunikan_kunci_silver` | **LOLOS** | Kunci ['sumber', 'seri_kode', 'wilayah_kode', 'periode', 'rincian', '_berkas_raw']: total 840 baris unik, duplikat = 0 baris. |
| 3 | `3_konsistensi_satuan_per_seri` | **LOLOS** | Diperiksa 6 seri_kode; seri dengan satuan ganda = []. |
| 4 | `4_pemisahan_seri_kode_definisi_ilo` | **LOLOS** | Seri ILO terpisah = ['SDG_0552_NOC_RT', 'SDG_T552_NOC_RT']. |
| 5 | `5_validitas_obs_status_ilo_dsd` | **LOLOS** | Kode OBS_STATUS di data ILO = ['', 'B']; terdaftar di DSD/kosong, ilegal = 0 baris. |