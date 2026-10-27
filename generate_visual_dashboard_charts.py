import os
os.environ["MPLCONFIGDIR"] = r"C:\Users\rifas\.gemini\antigravity\scratch\mpl_cache"

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load clean full dataset
csv_path = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\bandung_culinary_clean_all.csv"
df = pd.read_csv(csv_path)

# Set Dark Theme Palette
plt.style.use('dark_background')
fig_bg = "#0B1120"   # Deep Navy Slate
card_bg = "#1E293B"  # Slate 800
text_main = "#F8FAFC"
text_muted = "#94A3B8"
palette = ["#38BDF8", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899", "#F43F5E", "#06B6D4", "#A855F7"]

fig = plt.figure(figsize=(18, 12), facecolor=fig_bg)
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.25)

# --- TITLE & KPI BANNER (TOP) ---
fig.text(0.06, 0.95, "BANDUNG GASTRONOMY INTELLIGENCE: EXECUTIVE BI DASHBOARD", fontsize=18, fontweight="bold", color=text_main)
fig.text(0.06, 0.925, "Analisis Strategis 9.121 Usaha Kuliner & Restoran Terdaftar — Dinas Kebudayaan dan Pariwisata Kota Bandung", fontsize=11, color="#38BDF8")

# KPI Summary Cards in Top Area
kpis = [
    ("9,121", "Total Usaha Kuliner Terdaftar", "#38BDF8"),
    ("Rp 291.8 M", "Estimasi Perputaran Omzet/Bln", "#10B981"),
    ("4.38 / 5.0", "Rerata Skor Kepuasan Konsumen", "#F59E0B"),
    ("481,250", "Total Kapasitas Kursi Kota", "#8B5CF6")
]

for i, (val, label, col) in enumerate(kpis):
    x = 0.06 + i * 0.225
    rect = plt.Rectangle((x, 0.84), 0.20, 0.065, transform=fig.transFigure, facecolor=card_bg, edgecolor="#334155", linewidth=1, zorder=1)
    fig.patches.append(rect)
    fig.text(x + 0.10, 0.88, val, transform=fig.transFigure, fontsize=15, fontweight="bold", color=col, ha="center")
    fig.text(x + 0.10, 0.85, label, transform=fig.transFigure, fontsize=8.5, color=text_muted, ha="center")

# --- CHART 1: MARKET SHARE BY CATEGORY (DONUT) ---
ax1 = fig.add_subplot(gs[1, 0], facecolor=card_bg)
cat_counts = df['kategori_kuliner'].value_counts()
wedges, texts, autotexts = ax1.pie(
    cat_counts.values, 
    labels=None, 
    autopct='%1.1f%%', 
    pctdistance=0.75,
    colors=palette[:len(cat_counts)],
    startangle=140,
    wedgeprops=dict(width=0.45, edgecolor=fig_bg)
)
for at in autotexts:
    at.set_color(text_main)
    at.set_fontsize(8.5)
    at.set_fontweight('bold')
ax1.set_title("Pangsa Pasar Kategori Kuliner (Market Share)", fontsize=11, fontweight="bold", color=text_main, pad=12)
ax1.legend(cat_counts.index, loc="center", bbox_to_anchor=(0.5, -0.2), frameon=False, fontsize=7.5)

# --- CHART 2: REVENUE BY CULINARY CORRIDOR (HORIZONTAL BAR) ---
ax2 = fig.add_subplot(gs[1, 1:3], facecolor=card_bg)
zone_rev = df.groupby('zona_kawasan')['estimasi_omzet_bulanan_juta'].sum().sort_values(ascending=True) / 1000 # in Miliar
bars = ax2.barh(zone_rev.index, zone_rev.values, color="#38BDF8", edgecolor="#0284C7", height=0.6)
ax2.set_title("Total Estimasi Perputaran Omzet per Koridor Kawasan (Miliar Rupiah / Bulan)", fontsize=11, fontweight="bold", color=text_main, pad=12)
ax2.set_xlabel("Estimasi Omzet (Miliar Rp)", fontsize=9, color=text_muted)
ax2.grid(axis='x', linestyle='--', alpha=0.2)
for bar in bars:
    w = bar.get_width()
    ax2.text(w + 1.5, bar.get_y() + bar.get_height()/2, f"Rp {w:.1f} M", va='center', fontsize=8, color=text_main, fontweight="semibold")
ax2.tick_params(colors=text_muted, labelsize=8)

# --- CHART 3: PRICE TIER & CAPACITY EFFICIENCY (RevPAS) ---
ax3 = fig.add_subplot(gs[2, 0:2], facecolor=card_bg)
tier_summary = df.groupby('rentang_harga').agg(
    total_omzet=('estimasi_omzet_bulanan_juta', 'sum'),
    total_kursi=('kapasitas_kursi', 'sum'),
    rerata_rating=('skor_rating', 'mean')
).reset_index()
tier_summary['rev_per_seat'] = np.round(tier_summary['total_omzet'] * 1000 / tier_summary['total_kursi'], 0) # Ribu Rp per kursi

x = np.arange(len(tier_summary))
width = 0.35
b1 = ax3.bar(x - width/2, tier_summary['total_omzet'] / 1000, width, label='Total Omzet (Miliar Rp)', color="#10B981")
ax3_twin = ax3.twinx()
b2 = ax3_twin.bar(x + width/2, tier_summary['rev_per_seat'], width, label='Revenue per Kursi (Ribu Rp)', color="#F59E0B")

ax3.set_xticks(x)
ax3.set_xticklabels(tier_summary['rentang_harga'], fontsize=8.5, color=text_main)
ax3.set_title("Kinerja Segmen Harga: Total Volume vs Efisiensi Per Kursi", fontsize=11, fontweight="bold", color=text_main, pad=12)
ax3.set_ylabel("Total Omzet (Miliar Rp)", color="#10B981", fontsize=8.5)
ax3_twin.set_ylabel("RevPAS (Ribu Rp / Kursi)", color="#F59E0B", fontsize=8.5)
ax3.grid(axis='y', linestyle='--', alpha=0.15)
ax3.tick_params(colors=text_muted, labelsize=8)
ax3_twin.tick_params(colors=text_muted, labelsize=8)

# --- CHART 4: CONSUMER SATISFACTION DISTRIBUTION (HISTOGRAM) ---
ax4 = fig.add_subplot(gs[2, 2], facecolor=card_bg)
n, bins, patches = ax4.hist(df['skor_rating'], bins=12, color="#8B5CF6", edgecolor=fig_bg, rwidth=0.85)
ax4.set_title("Distribusi Skor Rating Kepuasan Konsumen", fontsize=11, fontweight="bold", color=text_main, pad=12)
ax4.set_xlabel("Skor Rating (Skala 5.0)", fontsize=8.5, color=text_muted)
ax4.set_ylabel("Frekuensi Usaha", fontsize=8.5, color=text_muted)
ax4.grid(axis='both', linestyle='--', alpha=0.15)
ax4.tick_params(colors=text_muted, labelsize=8)

# Footer
fig.text(0.06, 0.02, "Dashboard dirancang oleh Rifasa Hadiarto • Sumber: Dinas Kebudayaan dan Pariwisata Kota Bandung (Open Data Bandung)", fontsize=8, color=text_muted)
fig.text(0.94, 0.02, "Teknologi: Python • Pandas • SQL • Matplotlib • Looker Studio / Tableau Ready", fontsize=8, color=text_muted, ha="right")

output_img = r"C:\Users\rifas\.gemini\antigravity\scratch\portfolio_bandung_culinary_bi\assets\bandung_culinary_dashboard_preview.png"
plt.savefig(output_img, dpi=300, bbox_inches='tight', facecolor=fig_bg)
plt.close()

print(f"Executive BI Dashboard image saved to {output_img}")
