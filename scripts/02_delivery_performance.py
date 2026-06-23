"""
02_delivery_performance.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Analyses delivery performance across states, product categories, and time.
Produces delivery KPI exports and visualisations.

Input  : data/cleaned_orders.csv
Outputs: data/delivery_performance.csv
         data/state_performance.csv
         data/category_performance.csv
         outputs/chart_delivery_trend.png
         outputs/chart_state_sla_breach.png
         outputs/chart_category_freight.png
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
os.makedirs(OUT_DIR, exist_ok=True)

BG     = '#0f1117'
PANEL  = '#1a1d27'
GREEN  = '#2ecc71'
RED    = '#e74c3c'
BLUE   = '#3498db'
ORANGE = '#e67e22'
GREY   = '#aaaaaa'
WHITE  = 'white'

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
df = pd.read_csv(f'{DATA_DIR}/cleaned_orders.csv', parse_dates=['order_purchase_timestamp'])
print(f"Loaded {len(df):,} orders")

# ── 1. Monthly delivery performance ──────────────────────────────────────────
monthly = df.groupby('YearMonth').agg(
    total_orders    = ('order_id',              'count'),
    on_time_orders  = ('is_on_time',            'sum'),
    late_orders     = ('is_late',               'sum'),
    avg_delay_days  = ('delay_days',            'mean'),
    avg_delivery    = ('delivery_days_actual',  'mean'),
    total_revenue   = ('order_value',           'sum'),
    avg_review      = ('review_score',          'mean')
).reset_index()

monthly['on_time_rate_pct'] = (monthly['on_time_orders'] / monthly['total_orders'] * 100).round(1)
monthly['late_rate_pct']    = (monthly['late_orders']    / monthly['total_orders'] * 100).round(1)
monthly['avg_delay_days']   = monthly['avg_delay_days'].round(1)
monthly['avg_delivery']     = monthly['avg_delivery'].round(1)
monthly['total_revenue']    = monthly['total_revenue'].round(2)
monthly['avg_review']       = monthly['avg_review'].round(2)
monthly.to_csv(f'{DATA_DIR}/delivery_performance.csv', index=False)
print(f"  Monthly performance: {len(monthly)} months")

# ── 2. State performance ──────────────────────────────────────────────────────
state = df.groupby('customer_state').agg(
    total_orders    = ('order_id',             'count'),
    late_orders     = ('is_late',              'sum'),
    avg_delay_days  = ('delay_days',           'mean'),
    avg_delivery    = ('delivery_days_actual', 'mean'),
    avg_review      = ('review_score',         'mean'),
    total_revenue   = ('order_value',          'sum')
).reset_index()

state['sla_breach_rate_pct'] = (state['late_orders'] / state['total_orders'] * 100).round(1)
state['avg_delay_days']      = state['avg_delay_days'].round(1)
state['avg_delivery']        = state['avg_delivery'].round(1)
state['avg_review']          = state['avg_review'].round(2)
state.to_csv(f'{DATA_DIR}/state_performance.csv', index=False)
print(f"  State performance: {len(state)} states")

# ── 3. Category performance ───────────────────────────────────────────────────
cat = df.dropna(subset=['product_category_name_english']).groupby(
    'product_category_name_english'
).agg(
    total_orders   = ('order_id',              'count'),
    late_orders    = ('is_late',               'sum'),
    avg_freight    = ('freight_value',         'mean'),
    avg_order_val  = ('order_value',           'mean'),
    avg_review     = ('review_score',          'mean'),
    avg_delivery   = ('delivery_days_actual',  'mean'),
    avg_weight_g   = ('product_weight_g',      'mean')
).reset_index()

cat['late_rate_pct']    = (cat['late_orders'] / cat['total_orders'] * 100).round(1)
cat['freight_ratio_pct']= (cat['avg_freight'] / cat['avg_order_val'] * 100).round(1)
cat['avg_freight']      = cat['avg_freight'].round(2)
cat['avg_order_val']    = cat['avg_order_val'].round(2)
cat['avg_review']       = cat['avg_review'].round(2)
cat['avg_delivery']     = cat['avg_delivery'].round(1)
cat = cat[cat['total_orders'] >= 50]
cat.to_csv(f'{DATA_DIR}/category_performance.csv', index=False)
print(f"  Category performance: {len(cat)} categories (>=50 orders)")

# ── CHART 1: Monthly delivery trend ──────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor(BG)
styled_ax(ax1, 'Monthly Order Volume & On-Time Delivery Rate', 'Month', 'Orders')

plot_m = monthly[monthly['YearMonth'] >= '2017-01'].copy()
x = range(len(plot_m))

ax1.bar(x, plot_m['total_orders'], color=BLUE, alpha=0.5, width=0.6, label='Total Orders')
ax1.bar(x, plot_m['on_time_orders'], color=GREEN, alpha=0.7, width=0.6, label='On-Time Orders')
ax1.set_xticks(list(x)[::2])
ax1.set_xticklabels(plot_m['YearMonth'].iloc[::2], rotation=45, ha='right', fontsize=8)
ax1.legend(facecolor=PANEL, labelcolor=WHITE, fontsize=8)

ax2 = ax1.twinx()
ax2.plot(x, plot_m['on_time_rate_pct'], color=ORANGE, linewidth=2.5, marker='o', markersize=4)
ax2.set_ylabel('On-Time Rate %', color=GREY, fontsize=9)
ax2.tick_params(colors=GREY, labelsize=8)
ax2.spines[:].set_visible(False)
ax2.set_ylim(70, 100)

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_delivery_trend.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  chart_delivery_trend.png saved")

# ── CHART 2: SLA breach rate by state (top 15) ───────────────────────────────
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'SLA Breach Rate by State\n(% of Orders Delivered Late)', '', 'State')

top_states = state[state['total_orders'] >= 100].nlargest(15, 'sla_breach_rate_pct')
colors = [RED if v > 10 else ORANGE if v > 5 else GREEN for v in top_states['sla_breach_rate_pct']]
bars = ax.barh(top_states['customer_state'], top_states['sla_breach_rate_pct'],
               color=colors, edgecolor='none', height=0.6)

for bar, val in zip(bars, top_states['sla_breach_rate_pct']):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, color=WHITE, fontweight='bold')

ax.set_xlabel('SLA Breach Rate (%)', color=GREY, fontsize=9)
ax.tick_params(axis='y', colors=WHITE)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_state_sla_breach.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  chart_state_sla_breach.png saved")

# ── CHART 3: Freight ratio by category (top 15 highest) ──────────────────────
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'Freight Cost as % of Order Value by Product Category\n(Top 15 Highest Freight Burden)', '', 'Category')

top_cat = cat.nlargest(15, 'freight_ratio_pct').sort_values('freight_ratio_pct')
colors  = [RED if v > 30 else ORANGE if v > 20 else BLUE for v in top_cat['freight_ratio_pct']]
bars = ax.barh(top_cat['product_category_name_english'], top_cat['freight_ratio_pct'],
               color=colors, edgecolor='none', height=0.6)

for bar, val in zip(bars, top_cat['freight_ratio_pct']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, color=WHITE, fontweight='bold')

ax.set_xlabel('Freight as % of Order Value', color=GREY, fontsize=9)
ax.tick_params(axis='y', colors=WHITE, labelsize=8)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_category_freight.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("  chart_category_freight.png saved")

print(f"\n[02] Delivery performance complete.")
print(f"     On-time rate overall : {df['is_on_time'].mean()*100:.1f}%")
print(f"     Worst state (breach) : {state.nlargest(1,'sla_breach_rate_pct')['customer_state'].values[0]} - {state.nlargest(1,'sla_breach_rate_pct')['sla_breach_rate_pct'].values[0]}%")
print(f"     Best state (breach)  : {state.nsmallest(1,'sla_breach_rate_pct')['customer_state'].values[0]} - {state.nsmallest(1,'sla_breach_rate_pct')['sla_breach_rate_pct'].values[0]}%")
