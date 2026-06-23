"""
03_seller_scorecard.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Builds a composite performance scorecard for every seller, ranks them,
and segments into performance tiers.

Input  : data/seller_summary.csv, data/cleaned_orders.csv
Outputs: data/seller_scorecard.csv
         outputs/chart_seller_performance.png
         outputs/chart_review_vs_laterate.png
         outputs/chart_seller_revenue_concentration.png
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import os

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'input')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'outputs')

BG    = '#0f1117'
PANEL = '#1a1d27'
GREEN = '#2ecc71'
RED   = '#e74c3c'
BLUE  = '#3498db'
ORANGE= '#e67e22'
PURPLE= '#9b59b6'
GREY  = '#aaaaaa'
WHITE = 'white'

def styled_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=GREY, labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333')
    ax.spines['bottom'].set_color('#333')
    ax.grid(axis='y', color='#252535', linewidth=0.8)
    if title:  ax.set_title(title,  color=WHITE, fontsize=11, fontweight='bold', pad=10)
    if xlabel: ax.set_xlabel(xlabel, color=GREY,  fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=GREY,  fontsize=9)

# ── Load ──────────────────────────────────────────────────────────────────────
sellers = pd.read_csv(f'{DATA_DIR}/seller_summary.csv')
df      = pd.read_csv(f'{DATA_DIR}/cleaned_orders.csv')
print(f"Sellers loaded: {len(sellers):,}")

# ── Focus on sellers with 10+ orders for statistical reliability ──────────────
sellers = sellers[sellers['total_orders'] >= 10].copy()
print(f"Sellers with 10+ orders: {len(sellers):,}")

# ── Composite Score (0-100) ───────────────────────────────────────────────────
# On-time rate (40%), Review score (35%), Revenue volume (25%)
sellers['on_time_rate'] = 100 - sellers['late_rate_pct']

# Normalize each component 0-1
def norm(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

sellers['score_delivery'] = norm(sellers['on_time_rate'])    * 40
sellers['score_review']   = norm(sellers['avg_review_score'])* 35
sellers['score_revenue']  = norm(sellers['total_revenue'])   * 25
sellers['composite_score']= (sellers['score_delivery'] +
                              sellers['score_review']   +
                              sellers['score_revenue']).round(1)

# ── Rank and tier ─────────────────────────────────────────────────────────────
sellers = sellers.sort_values('composite_score', ascending=False).reset_index(drop=True)
sellers['rank'] = sellers.index + 1

def tier(score):
    if score >= 75: return 'Elite'
    if score >= 55: return 'Good'
    if score >= 35: return 'Average'
    return 'At Risk'

sellers['performance_tier'] = sellers['composite_score'].apply(tier)

sellers.to_csv(f'{DATA_DIR}/seller_scorecard.csv', index=False)

# Print summary
print("\nSeller Performance Tier Distribution:")
print(sellers['performance_tier'].value_counts())
print(f"\nTop seller score   : {sellers['composite_score'].max():.1f}")
print(f"Bottom seller score: {sellers['composite_score'].min():.1f}")
print(f"Avg composite score: {sellers['composite_score'].mean():.1f}")

# ── CHART 1: Top 20 vs Bottom 20 sellers by composite score ──────────────────
fig, (ax_top, ax_bot) = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(BG)

top20 = sellers.head(20)
bot20 = sellers.tail(20).sort_values('composite_score')

styled_ax(ax_top, 'Top 20 Sellers — Composite Score', 'Score', '')
bars = ax_top.barh(range(len(top20)), top20['composite_score'],
                   color=GREEN, edgecolor='none', height=0.6)
ax_top.set_yticks(range(len(top20)))
ax_top.set_yticklabels([f"Rank {r}" for r in top20['rank']], color=WHITE, fontsize=8)
for bar, val in zip(bars, top20['composite_score']):
    ax_top.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=8, color=WHITE)

styled_ax(ax_bot, 'Bottom 20 Sellers — Composite Score\n(At Risk)', 'Score', '')
bars2 = ax_bot.barh(range(len(bot20)), bot20['composite_score'],
                    color=RED, edgecolor='none', height=0.6)
ax_bot.set_yticks(range(len(bot20)))
ax_bot.set_yticklabels([f"Rank {r}" for r in bot20['rank']], color=WHITE, fontsize=8)
for bar, val in zip(bars2, bot20['composite_score']):
    ax_bot.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=8, color=WHITE)

plt.suptitle('Seller Performance Scorecard', color=WHITE, fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_seller_performance.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  chart_seller_performance.png saved")

# ── CHART 2: Review score vs Late rate (scatter) ──────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(PANEL)

tier_colors = {'Elite': GREEN, 'Good': BLUE, 'Average': ORANGE, 'At Risk': RED}
for t, grp in sellers.groupby('performance_tier'):
    ax.scatter(grp['late_rate_pct'], grp['avg_review_score'],
               c=tier_colors[t], label=t, alpha=0.7, s=40, edgecolors='none')

ax.set_xlabel('Late Delivery Rate (%)', color=GREY, fontsize=10)
ax.set_ylabel('Avg Review Score (/ 5.0)', color=GREY, fontsize=10)
ax.set_title('Seller Late Rate vs Customer Review Score\n(Each dot = one seller)',
             color=WHITE, fontsize=12, fontweight='bold', pad=12)
ax.tick_params(colors=GREY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333')
ax.spines['bottom'].set_color('#333')
ax.legend(facecolor=PANEL, labelcolor=WHITE, fontsize=9, title='Tier',
          title_fontsize=9)
ax.axhline(4.0, color='#555', linestyle='--', linewidth=1, alpha=0.6)
ax.text(ax.get_xlim()[1]*0.7, 4.05, 'Score = 4.0 threshold',
        color='#aaa', fontsize=8)

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_review_vs_laterate.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  chart_review_vs_laterate.png saved")

# ── CHART 3: Revenue concentration (top 20 sellers % of total) ───────────────
fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'Revenue Concentration — Top 20 Sellers vs Rest', '', 'Revenue (R$)')

total_rev = sellers['total_revenue'].sum()
top20_rev = sellers.head(20)['total_revenue'].sum()
rest_rev  = total_rev - top20_rev

ax.barh(['Rest of Sellers\n(all others)', 'Top 20 Sellers'],
        [rest_rev, top20_rev],
        color=[BLUE, GREEN], edgecolor='none', height=0.4)
ax.text(top20_rev + total_rev*0.005, 1,
        f'R${top20_rev:,.0f} ({top20_rev/total_rev*100:.1f}%)',
        va='center', color=WHITE, fontweight='bold', fontsize=10)
ax.text(rest_rev + total_rev*0.005, 0,
        f'R${rest_rev:,.0f} ({rest_rev/total_rev*100:.1f}%)',
        va='center', color=WHITE, fontweight='bold', fontsize=10)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
ax.tick_params(axis='y', colors=WHITE)

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_seller_revenue_concentration.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("  chart_seller_revenue_concentration.png saved")
print(f"\n[03] Seller scorecard complete. -> data/seller_scorecard.csv")
