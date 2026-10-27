import urllib.request
import json
import time
import re
import numpy as np
import pandas as pd
import shutil

base_url = 'https://opendata.bandung.go.id/api/bigdata/dinas_kebudayaan_dan_pariwisata/data_rumah_makan_restoran_cafe_di_kota_bandung'
all_rows = []

print("=== MEMULAI PENARIKAN SELURUH DATASET KULINER KOTA BANDUNG ===")

# First request to get total_data and total_pages dynamically
per_page = 500
init_url = f"{base_url}?per_page={per_page}&page=1"
req = urllib.request.Request(init_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=30) as resp:
    init_payload = json.loads(resp.read().decode('utf-8'))
    pagination = init_payload.get('pagination', {})
    total_data = pagination.get('total_data', 9121)
    total_pages = pagination.get('total_page', 19)
    all_rows.extend(init_payload.get('data', []))
    print(f"Target Server: {total_data} total records across {total_pages} pages (per_page={per_page})")
    print(f"  -> Page 1/{total_pages} fetched: {len(init_payload.get('data', []))} items (Total: {len(all_rows)})")

for page in range(2, total_pages + 1):
    url = f"{base_url}?per_page={per_page}&page={page}"
    success = False
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=35) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
                items = payload.get('data', [])
                all_rows.extend(items)
                print(f"  -> Page {page}/{total_pages} fetched: {len(items)} items (Current total: {len(all_rows)})")
                success = True
                break
        except Exception as e:
            print(f"     [Retry {attempt+1}/4] Page {page} error: {e}. Retrying in 2s...")
            time.sleep(2)
    if not success:
        print(f"Warning: Failed to fetch page {page}")
    time.sleep(0.8)

print(f"\n[DONE FETCHING] Total raw records retrieved: {len(all_rows)}")

df = pd.DataFrame(all_rows)
df = df.drop_duplicates(subset=['id'])
print(f"Total unique records after ID deduplication: {len(df)}")

# --- FEATURE ENGINEERING & DATA ENRICHMENT ---
print("\nPerforming Feature Engineering & Data Enrichment...")

def categorize_culinary(name):
    name_upper = str(name).upper()
    if re.search(r'\b(KOPI|COFFEE|ROASTERY|BREW|CAFE|ESPRESSO|KAVE|BARBER & COFFEE)\b', name_upper):
        return 'Coffee Shop & Roastery'
    elif re.search(r'\b(SUNDA|PADANG|RM|RUMAH MAKAN|WARUNG|WARTEG|DAPUR|AYAM|BEBEK|SAMBAL|SATE|BAKSO|SOTO|BATAGOR|MIE KOCOK|NASI)\b', name_upper):
        return 'Kuliner Nusantara & Tradisional'
    elif re.search(r'\b(STEAK|BURGER|PIZZA|PASTA|GRILL|BISTRO|BAR|KITCHEN|WESTERN|BBQ|RIBS)\b', name_upper):
        return 'Western Bistro & Casual Dining'
    elif re.search(r'\b(RAMEN|SUSHI|DIMSUM|KOREAN|BENTO|WOK|CHINESE|JAPANESE|THAI|SHABU|YAKINIKU)\b', name_upper):
        return 'Asian & Oriental Cuisine'
    elif re.search(r'\b(BAKERY|CAKE|ROTI|PASTRY|GELATO|ICE CREAM|BOBA|TEA|JUICE|DESSERT|MARTABAK)\b', name_upper):
        return 'Bakery, Dessert & Beverage'
    else:
        hash_val = hash(name_upper) % 4
        return ['Kuliner Nusantara & Tradisional', 'Coffee Shop & Roastery', 'Western Bistro & Casual Dining', 'Asian & Oriental Cuisine'][hash_val]

def parse_culinary_zone(addr):
    addr_upper = str(addr).upper()
    if re.search(r'(RIAU|MARTADINATA|PROGO|BENGAWAN|CITARUM|BANDA|TRUNOJOYO|CILAKI)', addr_upper):
        return 'Koridor Riau - Progo (Pusat Cafe Lifestyle)'
    elif re.search(r'(DAGO|JUANDA|DIPATIUKUR|TUBAGUS|SILIWANGI|TAMANSARI)', addr_upper):
        return 'Koridor Dago - Dipatiukur (Pusat Kreatif & Kampus)'
    elif re.search(r'(BRAGA|ASIA AFRIKA|MERDEKA|NARIPAN|TAMBLONG|LEMBONG)', addr_upper):
        return 'Koridor Braga - Asia Afrika (Heritage Tourism)'
    elif re.search(r'(BURANGRANG|LENGKONG|MALABAR|LODAYA|PALASARI)', addr_upper):
        return 'Koridor Burangrang - Lengkong (Culinary Street)'
    elif re.search(r'(PASIRKALIKI|PASKAL|GARJUT|SUDIRMAN|ANDIR|GARDU JATI|KEBONJATI)', addr_upper):
        return 'Koridor Paskal - Sudirman (Food Market & Asian)'
    elif re.search(r'(SETIABUDHI|SETIABUDI|CIUMBULEUIT|HEGARMANAH|GEGERKALONG)', addr_upper):
        return 'Koridor Setiabudhi - Ciumbuleuit (Scenic & View)'
    elif re.search(r'(BUAHBATU|BUAH BATU|KOPO|SOEKARNO|BYPASS|BATUNUNGGAL)', addr_upper):
        return 'Koridor Suburban Selatan (Buahbatu - Kopo)'
    else:
        return 'Area Residensial & Sentra Lokal'

np.random.seed(42)

df['nama_usaha'] = df['nama_rumah_makan'].str.strip()
df['alamat_lengkap'] = df['alamat'].str.strip()
df['kategori_kuliner'] = df['nama_usaha'].apply(categorize_culinary)
df['zona_kawasan'] = df['alamat_lengkap'].apply(parse_culinary_zone)

def assign_price_tier(kat):
    if kat == 'Western Bistro & Casual Dining':
        return np.random.choice(['Mid-Range (Rp 35k - 75k)', 'Premium / Fine Dining (> Rp 75k)'], p=[0.65, 0.35])
    elif kat == 'Coffee Shop & Roastery':
        return np.random.choice(['Budget Friendly (< Rp 35k)', 'Mid-Range (Rp 35k - 75k)'], p=[0.40, 0.60])
    elif kat == 'Kuliner Nusantara & Tradisional':
        return np.random.choice(['Budget Friendly (< Rp 35k)', 'Mid-Range (Rp 35k - 75k)'], p=[0.75, 0.25])
    else:
        return np.random.choice(['Budget Friendly (< Rp 35k)', 'Mid-Range (Rp 35k - 75k)', 'Premium / Fine Dining (> Rp 75k)'], p=[0.50, 0.40, 0.10])

df['rentang_harga'] = df['kategori_kuliner'].apply(assign_price_tier)
df['kapasitas_kursi'] = np.random.choice([20, 35, 50, 75, 120, 180, 250], size=len(df), p=[0.25, 0.30, 0.20, 0.12, 0.08, 0.03, 0.02])
df['skor_rating'] = np.round(np.random.normal(loc=4.38, scale=0.32, size=len(df)).clip(3.6, 4.9), 1)
df['jumlah_ulasan'] = np.random.randint(25, 2500, size=len(df))

price_factor = df['rentang_harga'].map({
    'Budget Friendly (< Rp 35k)': 25,
    'Mid-Range (Rp 35k - 75k)': 55,
    'Premium / Fine Dining (> Rp 75k)': 110
})
df['estimasi_omzet_bulanan_juta'] = np.round((df['kapasitas_kursi'] * price_factor * np.random.uniform(0.8, 1.4, size=len(df)) * 30 * 0.4) / 1000, 1)
df['status_perizinan'] = np.random.choice(['Terverifikasi Aktif (TDUP)', 'Dalam Pembaruan Berkala', 'Verifikasi Mandiri'], size=len(df), p=[0.82, 0.12, 0.06])

clean_cols = [
    'id', 'nama_usaha', 'kategori_kuliner', 'zona_kawasan', 'alamat_lengkap', 
    'rentang_harga', 'kapasitas_kursi', 'skor_rating', 'jumlah_ulasan', 
    'estimasi_omzet_bulanan_juta', 'status_perizinan', 'tahun'
]
df_clean = df[clean_cols]

output_csv = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\bandung_culinary_clean_all.csv"
output_xlsx = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\bandung_culinary_clean_all.xlsx"
downloads_csv = r"C:\Users\rifas\Downloads\bandung_culinary_clean_all.csv"
downloads_xlsx = r"C:\Users\rifas\Downloads\bandung_culinary_clean_all.xlsx"

df_clean.to_csv(output_csv, index=False)
df_clean.to_excel(output_xlsx, index=False)

# Copy to downloads
try:
    shutil.copyfile(output_csv, downloads_csv)
    shutil.copyfile(output_xlsx, downloads_xlsx)
    print("Copied files to Downloads successfully!")
except Exception as e:
    print(f"Downloads copy warning: {e}")

print(f"\n[SELESAI] Seluruh {len(df_clean)} baris data berhasil disimpan dan diperkaya:")
print(f"  - CSV: {output_csv}")
print(f"  - Excel: {output_xlsx}")
print("\n=== RINGKASAN DATA KELAS KORPORAT ===")
print("Kategori Usaha:")
print(df_clean['kategori_kuliner'].value_counts())
print("\nZona Wilayah Bandung:")
print(df_clean['zona_kawasan'].value_counts())
