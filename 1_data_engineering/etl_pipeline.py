"""
=============================================================================
STAGE 1: DATA ENGINEERING PIPELINE
Project: Bandung Gastronomy Intelligence
Module: Database Modeling, DDL Schema & Automated Ingestion
Author: Rifasa Hadiarto (Data Engineer)
=============================================================================
"""

import sqlite3
import pandas as pd
import os
import sys

def run_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'bandung_culinary_clean_all.csv')
    db_path = os.path.join(base_dir, 'bandung_gastronomy.db')

    print(">>> Starting Data Engineering ETL Pipeline...")
    print(f"[*] Target Database: {db_path}")

    # 1. Database Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. DDL Schema Definition (Star Schema: 1 Fact Table, 1 Dimension Table)
    print("[*] Creating relational database schema with constraints...")
    cursor.execute("DROP TABLE IF EXISTS fact_kuliner_bandung;")
    cursor.execute("DROP TABLE IF EXISTS dim_kawasan;")

    cursor.execute("""
    CREATE TABLE dim_kawasan (
        kawasan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_kawasan TEXT UNIQUE NOT NULL,
        klasifikasi_area TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE fact_kuliner_bandung (
        outlet_id INTEGER PRIMARY KEY,
        nama_usaha TEXT NOT NULL,
        kategori_kuliner TEXT NOT NULL,
        zona_kawasan TEXT NOT NULL,
        rentang_harga TEXT,
        kapasitas_kursi INTEGER,
        skor_rating REAL,
        jumlah_ulasan INTEGER,
        estimasi_omzet_juta REAL,
        status_perizinan TEXT,
        tahun_data INTEGER,
        FOREIGN KEY (zona_kawasan) REFERENCES dim_kawasan(nama_kawasan)
    );
    """)

    # 3. Ingestion & Transformation
    print(f"[*] Reading dataset from: {os.path.basename(csv_path)}")
    df = pd.read_csv(csv_path)

    # Populate Dimension Table
    zones = df['zona_kawasan'].unique()
    for z in zones:
        klasifikasi = 'Commercial Lifestyle' if 'Koridor' in z else 'Residential Sentra'
        cursor.execute("INSERT OR IGNORE INTO dim_kawasan (nama_kawasan, klasifikasi_area) VALUES (?, ?)", (z, klasifikasi))

    # Populate Fact Table
    print(f"[*] Ingesting {len(df):,} records into fact_kuliner_bandung...")
    records = []
    for _, row in df.iterrows():
        records.append((
            int(row['id']),
            str(row['nama_usaha']),
            str(row['kategori_kuliner']),
            str(row['zona_kawasan']),
            str(row['rentang_harga']),
            int(row['kapasitas_kursi']),
            float(row['skor_rating']),
            int(row['jumlah_ulasan']),
            float(row['estimasi_omzet_bulanan_juta']),
            str(row['status_perizinan']),
            int(row['tahun'])
        ))

    cursor.executemany("""
    INSERT INTO fact_kuliner_bandung (
        outlet_id, nama_usaha, kategori_kuliner, zona_kawasan,
        rentang_harga, kapasitas_kursi, skor_rating, jumlah_ulasan,
        estimasi_omzet_juta, status_perizinan, tahun_data
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    # 4. Create Indexes for Query Optimization
    print("[*] Building B-Tree indexes for fast analytical query performance...")
    cursor.execute("CREATE INDEX idx_kategori ON fact_kuliner_bandung(kategori_kuliner);")
    cursor.execute("CREATE INDEX idx_zona ON fact_kuliner_bandung(zona_kawasan);")
    cursor.execute("CREATE INDEX idx_omzet ON fact_kuliner_bandung(estimasi_omzet_juta);")

    conn.commit()

    # Validation
    cursor.execute("SELECT COUNT(*) FROM fact_kuliner_bandung;")
    total_fact = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dim_kawasan;")
    total_dim = cursor.fetchone()[0]

    print("\n[SUCCESS] Pipeline completed successfully!")
    print(f"   -> Dimension Rows: {total_dim}")
    print(f"   -> Fact Table Rows: {total_fact:,}")
    print(f"   -> Database File: bandung_gastronomy.db ({os.path.getsize(db_path) / 1024:.1f} KB)")
    
    conn.close()

if __name__ == '__main__':
    run_pipeline()
