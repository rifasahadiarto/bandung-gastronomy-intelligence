-- ==============================================================================
-- BANDUNG GASTRONOMY INTELLIGENCE: ADVANCED SQL ANALYTICAL QUERIES
-- Dataset: 9,121 Verified Culinary & Hospitality Establishments (Disparbud Kota Bandung)
-- Author: Rifasa Hadiarto (Certified Data Analyst & Analytics Engineer)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. ANALISIS KORIDOR STRATEGIS: Peringkat Zona Kuliner Berdasarkan Estimasi Omzet & Kapasitas
-- Menjawab: Kawasan mana yang menjadi pusat perputaran uang dan konsentrasi kapasitas kuliner?
-- ------------------------------------------------------------------------------
WITH CorridorAggregates AS (
    SELECT 
        zona_kawasan,
        COUNT(id) AS total_unit_usaha,
        SUM(kapasitas_kursi) AS total_kapasitas_kursi,
        ROUND(AVG(skor_rating), 2) AS rerata_skor_rating,
        ROUND(SUM(estimasi_omzet_bulanan_juta), 1) AS total_omzet_bulanan_juta,
        ROUND(AVG(estimasi_omzet_bulanan_juta), 1) AS rerata_omzet_per_unit_juta
    FROM bandung_culinary_clean
    GROUP BY zona_kawasan
)
SELECT 
    zona_kawasan,
    total_unit_usaha,
    total_kapasitas_kursi,
    rerata_skor_rating,
    total_omzet_bulanan_juta,
    rerata_omzet_per_unit_juta,
    -- Menghitung persentase kontribusi omzet koridor terhadap total kota Bandung
    ROUND(
        total_omzet_bulanan_juta * 100.0 / SUM(total_omzet_bulanan_juta) OVER(), 
        2
    ) AS kontribusi_omzet_persen,
    DENSE_RANK() OVER (ORDER BY total_omzet_bulanan_juta DESC) AS rank_omzet
FROM CorridorAggregates
ORDER BY total_omzet_bulanan_juta DESC;


-- ------------------------------------------------------------------------------
-- 2. MARKET SHARE & PENETRASI KATEGORI: Dominasi Coffee Shop vs Makanan Tradisional
-- Menjawab: Berapa pangsa pasar masing-masing kategori usaha dalam ekosistem kuliner Bandung?
-- ------------------------------------------------------------------------------
SELECT 
    kategori_kuliner,
    COUNT(id) AS jumlah_usaha,
    ROUND(COUNT(id) * 100.0 / SUM(COUNT(id)) OVER(), 2) AS market_share_unit_persen,
    ROUND(SUM(estimasi_omzet_bulanan_juta), 1) AS total_omzet_juta,
    ROUND(SUM(estimasi_omzet_bulanan_juta) * 100.0 / SUM(SUM(estimasi_omzet_bulanan_juta)) OVER(), 2) AS market_share_omzet_persen,
    ROUND(AVG(skor_rating), 2) AS rerata_rating,
    ROUND(AVG(kapasitas_kursi), 0) AS rerata_kapasitas_kursi
FROM bandung_culinary_clean
GROUP BY kategori_kuliner
ORDER BY total_omzet_juta DESC;


-- ------------------------------------------------------------------------------
-- 3. WINDOW FUNCTION DENSE_RANK(): Top 3 Usaha Kuliner Terbaik per Kategori (Leaderboard)
-- Menjawab: Siapa pemimpin pasar dengan rating dan kredibilitas ulasan tertinggi di tiap segmen?
-- ------------------------------------------------------------------------------
WITH RankedEstablishments AS (
    SELECT 
        kategori_kuliner,
        nama_usaha,
        zona_kawasan,
        rentang_harga,
        skor_rating,
        jumlah_ulasan,
        estimasi_omzet_bulanan_juta,
        -- Peringkat berdasarkan rating tertinggi dan jumlah ulasan terbanyak
        DENSE_RANK() OVER (
            PARTITION BY kategori_kuliner 
            ORDER BY skor_rating DESC, jumlah_ulasan DESC
        ) AS rank_dalam_kategori
    FROM bandung_culinary_clean
    WHERE status_perizinan = 'Terverifikasi Aktif (TDUP)'
)
SELECT 
    kategori_kuliner,
    rank_dalam_kategori,
    nama_usaha,
    zona_kawasan,
    rentang_harga,
    skor_rating,
    jumlah_ulasan,
    estimasi_omzet_bulanan_juta
FROM RankedEstablishments
WHERE rank_dalam_kategori <= 3
ORDER BY kategori_kuliner, rank_dalam_kategori;


-- ------------------------------------------------------------------------------
-- 4. PRICE TIER & CAPACITY ELASTICITY ANALYSIS: Korelasi Segmen Harga terhadap Kinerja
-- Menjawab: Apakah restoran segmen premium menghasilkan omzet lebih efisien dibanding budget?
-- ------------------------------------------------------------------------------
SELECT 
    rentang_harga,
    COUNT(id) AS jumlah_resto,
    ROUND(AVG(kapasitas_kursi), 1) AS rerata_kursi,
    ROUND(AVG(skor_rating), 2) AS rerata_rating,
    ROUND(SUM(estimasi_omzet_bulanan_juta), 1) AS total_omzet_juta,
    ROUND(AVG(estimasi_omzet_bulanan_juta), 1) AS rerata_omzet_per_resto_juta,
    -- Metrik Revenue Per Available Seat (RevPAS)
    ROUND(AVG(estimasi_omzet_bulanan_juta * 1000000.0 / kapasitas_kursi), 0) AS estimasi_omzet_per_kursi_rupiah
FROM bandung_culinary_clean
GROUP BY rentang_harga
ORDER BY rerata_omzet_per_resto_juta DESC;
