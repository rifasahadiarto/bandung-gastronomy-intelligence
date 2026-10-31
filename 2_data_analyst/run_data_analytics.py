"""
=============================================================================
STAGE 2: DATA ANALYST (SQL ANALYTICS & INSIGHT EXTRACTION)
Project: Bandung Gastronomy Intelligence
Module: CTEs, Window Functions & Business KPI Aggregations
Author: Rifasa Hadiarto (Data Analyst)
=============================================================================
"""

import sqlite3
import pandas as pd
import os

def run_analytics():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'bandung_gastronomy.db')
    output_dir = os.path.dirname(os.path.abspath(__file__))

    conn = sqlite3.connect(db_path)

    print(">>> Executing Data Analyst SQL Queries on bandung_gastronomy.db...\n")

    # Query 1: Market Saturation & Blue Ocean Ranking (CTE + Window Functions)
    query_blue_ocean = """
    WITH ZoneMetrics AS (
        SELECT 
            f.zona_kawasan,
            d.klasifikasi_area,
            COUNT(f.outlet_id) AS total_outlets,
            ROUND(AVG(f.estimasi_omzet_juta), 2) AS avg_monthly_omzet,
            ROUND(SUM(f.estimasi_omzet_juta), 2) AS total_market_value_juta,
            ROUND(AVG(f.skor_rating), 2) AS avg_rating
        FROM fact_kuliner_bandung f
        JOIN dim_kawasan d ON f.zona_kawasan = d.nama_kawasan
        GROUP BY f.zona_kawasan, d.klasifikasi_area
    )
    SELECT 
        zona_kawasan,
        klasifikasi_area,
        total_outlets,
        avg_monthly_omzet,
        total_market_value_juta,
        RANK() OVER (ORDER BY total_outlets DESC) AS competition_rank,
        RANK() OVER (ORDER BY avg_monthly_omzet DESC) AS revenue_rank,
        CASE 
            WHEN total_outlets > 500 THEN 'Red Ocean (High Competition)'
            WHEN avg_monthly_omzet >= 34.0 THEN 'Blue Ocean (Prime Opportunity)'
            ELSE 'Moderate Growth'
        END AS strategic_recommendation
    FROM ZoneMetrics
    ORDER BY avg_monthly_omzet DESC;
    """

    df_blue_ocean = pd.read_sql_query(query_blue_ocean, conn)
    print("--- [INSIGHT 1: BLUE OCEAN VS RED OCEAN ZONE RANKING] ---")
    print(df_blue_ocean.to_string(index=False))

    # Query 2: Category Unit Economics
    query_category = """
    SELECT 
        kategori_kuliner,
        COUNT(outlet_id) AS total_outlets,
        ROUND(AVG(kapasitas_kursi), 1) AS avg_seating_capacity,
        ROUND(AVG(estimasi_omzet_juta), 2) AS avg_omzet_juta,
        ROUND(AVG(estimasi_omzet_juta * 1000000.0 / kapasitas_kursi), 2) AS revenue_per_seat_rp,
        ROUND(AVG(skor_rating), 2) AS avg_rating
    FROM fact_kuliner_bandung
    GROUP BY kategori_kuliner
    ORDER BY avg_omzet_juta DESC;
    """
    df_cat = pd.read_sql_query(query_category, conn)
    print("\n--- [INSIGHT 2: CATEGORY UNIT ECONOMICS & REVENUE PER SEAT] ---")
    print(df_cat.to_string(index=False))

    # Save results to CSV for reporting
    df_blue_ocean.to_csv(os.path.join(output_dir, 'kpi_zone_strategy.csv'), index=False)
    df_cat.to_csv(os.path.join(output_dir, 'kpi_category_unit_economics.csv'), index=False)
    print(f"\n[SUCCESS] Analytical results exported to: {output_dir}")

    conn.close()

if __name__ == '__main__':
    run_analytics()
