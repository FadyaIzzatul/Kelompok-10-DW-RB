
"""
Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver.

Kasus 10: SDG 5 — Kesetaraan Gender.

Keluaran:
    data/silver/silver.parquet

Satu baris = satu seri x wilayah x periode x rincian x berkas sumber.

Rincian dari setiap sumber dipertahankan dalam bentuk JSON.
Pemilihan rincian yang sebanding dilakukan pada tahap Gold.
"""

import json
import re
from pathlib import Path

import pandas as pd

from src.common.skema import KOLOM, KUNCI


# ============================================================
# 1. KONSTANTA
# ============================================================

OUTPUT_SILVER = Path("data/silver/silver.parquet")

SUMBER = {
    "bps": "bps",
    "ilostat": "ilostat",
    "wdi": "wdi",
}


# ============================================================
# 2. FUNGSI PEMBANTU
# ============================================================

def nilai_kosong(nilai):
    """Memeriksa apakah sebuah nilai kosong."""
    if nilai is None:
        return True

    try:
        return bool(pd.isna(nilai))
    except (TypeError, ValueError):
        return False


def normalisasi_teks(nilai, default="Tidak tersedia"):
    """Membersihkan nilai teks tanpa mengubah informasi yang tersedia."""
    if nilai_kosong(nilai):
        return default

    teks = str(nilai).strip()

    if teks == "":
        return default

    return teks


def konversi_numerik(nilai):
    """Mengubah nilai observasi menjadi numerik."""

    if nilai_kosong(nilai):
        return None

    teks = str(nilai).strip()

    if teks == "":
        return None

    hasil = pd.to_numeric(teks, errors="coerce")

    if pd.isna(hasil):
        raise ValueError(
            f"Nilai observasi tidak dapat dikonversi: {nilai!r}"
        )

    return float(hasil)


def normalisasi_tahun(nilai):
    """Menyeragamkan periode tahunan menjadi YYYY."""

    if nilai_kosong(nilai):
        raise ValueError("Periode tahun tidak boleh kosong.")

    teks = str(nilai).strip()

    if not re.fullmatch(r"\d{4}", teks):
        raise ValueError(
            f"Format tahun tidak valid: {nilai!r}"
        )

    return teks


def konversi_kode_wilayah(nilai):
    """Mengubah kode wilayah menjadi integer."""

    if nilai_kosong(nilai):
        raise ValueError("Kode wilayah tidak boleh kosong.")

    return int(str(nilai).strip())


def buat_rincian(data):
    """
    Menyimpan seluruh atribut rincian sumber sebagai JSON.

    Tidak memilih rincian tertentu yang dianggap sebanding.
    Pemilihan rincian dilakukan pada tahap Gold.
    """

    rincian = {}

    for kolom, nilai in data.items():

        if nilai_kosong(nilai):
            rincian[kolom] = None

        elif isinstance(nilai, str):
            rincian[kolom] = nilai.strip()

        elif hasattr(nilai, "item"):
            rincian[kolom] = nilai.item()

        else:
            rincian[kolom] = nilai

    return json.dumps(
        rincian,
        ensure_ascii=False,
        sort_keys=True
    )


def ambil_lineage(baris):
    """
    Mengambil informasi asal data dari hasil ekstraksi.

    Hash tidak ditulis manual karena sudah disediakan
    oleh modul ekstraksi melalui MANIFEST.csv.
    """

    berkas = normalisasi_teks(
        baris.get("_berkas_raw"),
        default=""
    )

    sha = normalisasi_teks(
        baris.get("_sha256_raw"),
        default=""
    )

    if not berkas or not sha:
        raise ValueError(
            "Informasi lineage berkas atau SHA-256 tidak tersedia."
        )

    return berkas, sha


def buat_baris_silver(
    sumber,
    seri_kode,
    wilayah_kode,
    nama_wilayah,
    periode,
    rincian,
    nilai,
    satuan,
    lineage
):
    """Membentuk satu observasi dengan skema minimal Silver."""

    angka = konversi_numerik(nilai)

    # Silver hanya menyimpan observasi yang benar-benar tersedia.
    if angka is None:
        return None

    berkas, sha = lineage

    return {
        "sumber": sumber,
        "seri_kode": str(seri_kode),
        "wilayah_kode": konversi_kode_wilayah(wilayah_kode),
        "nama_wilayah": normalisasi_teks(nama_wilayah),
        "periode": normalisasi_tahun(periode),
        "jenis_periode": "tahun",
        "rincian": buat_rincian(rincian),
        "nilai": angka,
        "satuan": normalisasi_teks(satuan),
        "_berkas_raw": berkas,
        "_sha256_raw": sha,
    }


# ============================================================
# 3. NORMALISASI DATA BPS
# ============================================================

def normalisasi_bps(tabel_bps):
    """
    Mengubah hasil ekstraksi BPS menjadi struktur Silver.

    Menggunakan CSV sebagai observasi utama.
    JSON paralel tidak dimasukkan kembali agar observasi
    yang sama tidak tergandakan.
    """

    hasil = []

    nama_tabel = [
        "var1360_csv",
        "var2003_csv",
    ]

    for nama in nama_tabel:

        if nama not in tabel_bps:
            raise KeyError(
                f"Tabel BPS tidak ditemukan: {nama}"
            )

        df = tabel_bps[nama]

        for baris in df.to_dict("records"):

            seri = f"var{baris['var_id']}"

            # Satuan mengikuti keputusan K-002 dan K-003.
            if seri in ("var1360", "var2003"):
                satuan = "Persen"
            else:
                satuan = baris.get("satuan")

            # Seluruh rincian sumber dipertahankan.
            rincian = {
                "turvar_id": baris.get("turvar_id"),
                "turvar": baris.get("turvar"),
                "tahun_id": baris.get("tahun_id"),
                "periode_id": baris.get("periode_id"),
                "periode": baris.get("periode"),
            }

            lineage = ambil_lineage(baris)

            observasi = buat_baris_silver(
                sumber="bps",
                seri_kode=seri,
                wilayah_kode=baris.get("wilayah_id"),
                nama_wilayah=baris.get("wilayah"),
                periode=baris.get("tahun"),
                rincian=rincian,
                nilai=baris.get("nilai"),
                satuan=satuan,
                lineage=lineage,
            )

            if observasi is not None:
                hasil.append(observasi)

    return pd.DataFrame(hasil, columns=KOLOM)


# ============================================================
# 4. NORMALISASI DATA ILOSTAT
# ============================================================

def normalisasi_ilostat(tabel_ilostat):
    """
    Mengubah hasil ekstraksi ILOSTAT menjadi struktur Silver.

    Hanya mengambil observasi Indonesia (IDN).

    Dimensi dan atribut sumber dipertahankan dalam rincian.
    """

    hasil = []

    nama_seri = [
        "SDG_0552_NOC_RT",
        "SDG_T552_NOC_RT",
    ]

    kolom_identitas = {
        "DATAFLOW",
        "REF_AREA",
        "TIME_PERIOD",
        "OBS_VALUE",
        "_berkas_raw",
        "_sha256_raw",
    }

    for seri in nama_seri:

        nama_tabel = f"{seri}_data"

        if nama_tabel not in tabel_ilostat:
            raise KeyError(
                f"Tabel ILOSTAT tidak ditemukan: {nama_tabel}"
            )

        df = tabel_ilostat[nama_tabel]

        for baris in df.to_dict("records"):

            # Mempertahankan observasi nasional Indonesia.
            if str(baris.get("REF_AREA", "")).strip() != "IDN":
                continue

            # Semua dimensi selain kolom identitas dipertahankan.
            rincian = {
                kolom: nilai
                for kolom, nilai in baris.items()
                if kolom not in kolom_identitas
            }

            # UNIT_MEASURE PT berarti percentage.
            unit = str(
                baris.get("UNIT_MEASURE", "")
            ).strip()

            satuan = (
                "Persen"
                if unit == "PT"
                else unit
            )

            lineage = ambil_lineage(baris)

            observasi = buat_baris_silver(
                sumber="ilostat",
                seri_kode=seri,
                wilayah_kode=9999,
                nama_wilayah="Indonesia",
                periode=baris.get("TIME_PERIOD"),
                rincian=rincian,
                nilai=baris.get("OBS_VALUE"),
                satuan=satuan,
                lineage=lineage,
            )

            if observasi is not None:
                hasil.append(observasi)

    return pd.DataFrame(hasil, columns=KOLOM)


# ============================================================
# 5. NORMALISASI DATA WORLD BANK (WDI)
# ============================================================

def normalisasi_wdi(tabel_wdi):
    """
    Mengubah hasil ekstraksi WDI menjadi struktur Silver.

    Hanya mengambil data Indonesia (IDN).

    Metadata indikator tidak dimasukkan sebagai observasi.
    Atribut data yang tersedia tetap dipertahankan.
    """

    hasil = []

    nama_tabel = [
        "kelompok_05",
        "kelompok_07",
    ]

    kolom_identitas = {
        "indicator_id",
        "countryiso3code",
        "tahun",
        "nilai",
        "_berkas_raw",
        "_sha256_raw",
    }

    for nama in nama_tabel:

        if nama not in tabel_wdi:
            raise KeyError(
                f"Tabel WDI tidak ditemukan: {nama}"
            )

        df = tabel_wdi[nama]

        for baris in df.to_dict("records"):

            # Memastikan hanya observasi Indonesia.
            if str(
                baris.get("countryiso3code", "")
            ).strip() != "IDN":
                continue

            seri = normalisasi_teks(
                baris.get("indicator_id"),
                default=""
            )

            if not seri:
                continue

            # Menyimpan atribut indikator dan observasi.
            rincian = {
                kolom: nilai
                for kolom, nilai in baris.items()
                if kolom not in kolom_identitas
            }

            lineage = ambil_lineage(baris)

            observasi = buat_baris_silver(
                sumber="wdi",
                seri_kode=seri,
                wilayah_kode=9999,
                nama_wilayah="Indonesia",
                periode=baris.get("tahun"),
                rincian=rincian,
                nilai=baris.get("nilai"),
                satuan="Persen",
                lineage=lineage,
            )

            if observasi is not None:
                hasil.append(observasi)

    return pd.DataFrame(hasil, columns=KOLOM)


# ============================================================
# 6. PEMERIKSAAN KUNCI SILVER
# ============================================================

def periksa_kunci(df):
    """
    Memastikan kombinasi kunci Silver tidak memiliki konflik.

    Duplikasi identik boleh disatukan.
    Duplikasi dengan nilai atau satuan berbeda menghasilkan error.
    """

    duplikat = df.duplicated(KUNCI, keep=False)

    if not duplikat.any():
        return df

    data_duplikat = df.loc[duplikat]

    konflik_nilai = (
        data_duplikat
        .groupby(KUNCI, dropna=False)["nilai"]
        .nunique(dropna=False)
    )

    konflik_satuan = (
        data_duplikat
        .groupby(KUNCI, dropna=False)["satuan"]
        .nunique(dropna=False)
    )

    if (konflik_nilai > 1).any() or (konflik_satuan > 1).any():
        raise ValueError(
            "Ditemukan kunci Silver yang memiliki nilai "
            "atau satuan berbeda. Periksa sumber data."
        )

    # Hanya membuang duplikasi identik pada kunci.
    return df.drop_duplicates(
        subset=KUNCI,
        keep="first"
    ).copy()


# ============================================================
# 7. PEMERIKSAAN STRUKTUR DATA
# ============================================================

def periksa_dataframe(df):
    """Memastikan struktur dasar DataFrame Silver benar."""

    if df.empty:
        raise ValueError(
            "Data Silver kosong. Periksa hasil ekstraksi."
        )

    # Memastikan semua kolom wajib tersedia.
    kurang = [
        kolom
        for kolom in KOLOM
        if kolom not in df.columns
    ]

    if kurang:
        raise ValueError(
            f"Kolom Silver belum lengkap: {kurang}"
        )

    # Mengatur urutan kolom.
    df = df[KOLOM].copy()

    # Mengatur tipe data.
    df["wilayah_kode"] = df["wilayah_kode"].astype("int64")

    df["nilai"] = pd.to_numeric(
        df["nilai"],
        errors="raise"
    ).astype("float64")

    # Memeriksa nilai kosong.
    kosong = df.isna().sum()

    kolom_kosong = kosong[kosong > 0]

    if not kolom_kosong.empty:
        raise ValueError(
            "Ditemukan nilai kosong:\n"
            f"{kolom_kosong}"
        )

    return df


# ============================================================
# 8. FUNGSI UTAMA SILVER
# ============================================================

def jalankan(mentah):
    """
    Menerima hasil ekstraksi, membentuk Silver,
    menyimpan silver.parquet, dan mengembalikan DataFrame.
    """

    print("\nMemulai pembentukan Silver...")

    # Memastikan seluruh sumber tersedia.
    for sumber in SUMBER:

        if sumber not in mentah:
            raise KeyError(
                f"Hasil ekstraksi sumber {sumber} tidak ditemukan."
            )

    # Tahap 1: Normalisasi setiap sumber.
    print("Normalisasi BPS...")
    bps = normalisasi_bps(mentah["bps"])

    print("Normalisasi ILOSTAT...")
    ilostat = normalisasi_ilostat(mentah["ilostat"])

    print("Normalisasi WDI...")
    wdi = normalisasi_wdi(mentah["wdi"])

    # Tahap 2: Menggabungkan struktur observasi.
    # Bukan menggabungkan nilai antarindikator.
    silver = pd.concat(
        [bps, ilostat, wdi],
        ignore_index=True
    )

    print(f"Total observasi sebelum deduplikasi: {len(silver)}")

    # Tahap 3: Pemeriksaan kunci.
    silver = periksa_kunci(silver)

    # Tahap 4: Pemeriksaan struktur.
    silver = periksa_dataframe(silver)

    # Tahap 5: Pengurutan.
    silver = silver.sort_values(
        by=[
            "sumber",
            "seri_kode",
            "wilayah_kode",
            "periode",
            "rincian",
        ],
        kind="stable"
    ).reset_index(drop=True)

    # Tahap 6: Membuat folder output.
    OUTPUT_SILVER.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Tahap 7: Menyimpan Parquet.
    silver.to_parquet(
        OUTPUT_SILVER,
        index=False,
        engine="pyarrow"
    )

    print("\nPembentukan Silver berhasil.")
    print(f"Lokasi output : {OUTPUT_SILVER}")
    print(f"Jumlah baris  : {len(silver):,}")
    print(f"Jumlah kolom  : {len(silver.columns)}")
    print(f"Jumlah seri   : {silver['seri_kode'].nunique()}")
    print(f"Jumlah sumber : {silver['sumber'].nunique()}")

    return silver
