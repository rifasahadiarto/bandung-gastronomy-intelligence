import urllib.request
import json
import time
import pandas as pd
import shutil

base_url = 'https://opendata.bandung.go.id/api/bigdata/dinas_kebudayaan_dan_pariwisata/data_rumah_makan_restoran_cafe_di_kota_bandung'
all_raw = []

print("=== MENGAMBIL DATA MURNI / MENTAH (100% ASLI DARI SERVER DISPARBUD BANDUNG) ===")

per_page = 500
init_url = f"{base_url}?per_page={per_page}&page=1"
req = urllib.request.Request(init_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    init_payload = json.loads(resp.read().decode('utf-8'))
    total_data = init_payload.get('pagination', {}).get('total_data', 9121)
    total_pages = init_payload.get('pagination', {}).get('total_page', 19)
    all_raw.extend(init_payload.get('data', []))
    print(f"Server Target: {total_data} data ({total_pages} halaman)")
    print(f"  -> Halaman 1/{total_pages} berhasil (Total: {len(all_raw)})")

for page in range(2, total_pages + 1):
    url = f"{base_url}?per_page={per_page}&page={page}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=35) as resp:
                items = json.loads(resp.read().decode('utf-8')).get('data', [])
                all_raw.extend(items)
                print(f"  -> Halaman {page}/{total_pages} berhasil (Total: {len(all_raw)})")
                break
        except Exception as e:
            print(f"     [Retry] Halaman {page} coba lagi...")
            time.sleep(2)
    time.sleep(0.5)

df_raw = pd.DataFrame(all_raw)
print(f"\nTotal baris data mentah asli: {len(df_raw)}")
print(df_raw.head())

# File paths
raw_csv = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\data_mentah_bandung_culinary_raw_9121.csv"
raw_xlsx = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\data_mentah_bandung_culinary_raw_9121.xlsx"
dl_raw_csv = r"C:\Users\rifas\Downloads\data_mentah_bandung_culinary_raw_9121.csv"
dl_raw_xlsx = r"C:\Users\rifas\Downloads\data_mentah_bandung_culinary_raw_9121.xlsx"

df_raw.to_csv(raw_csv, index=False)
df_raw.to_excel(raw_xlsx, index=False)

try:
    shutil.copyfile(raw_csv, dl_raw_csv)
    shutil.copyfile(raw_xlsx, dl_raw_xlsx)
    print("Berhasil dicopy ke folder Downloads!")
except Exception as e:
    print(f"Warning copy to downloads: {e}")

print(f"\n[SUKSES] Data Mentah Murni Tersimpan di:\n  - CSV: {raw_csv}\n  - Excel: {raw_xlsx}")
