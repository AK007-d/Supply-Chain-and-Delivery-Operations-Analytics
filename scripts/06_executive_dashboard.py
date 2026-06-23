"""
06_executive_dashboard.py
Supply Chain & Delivery Operations Analytics — Olist Brazilian E-commerce
---------------------------------------------------------------------------
Generates individual chart exports for Power BI and presentation use.

Input  : outputs/q*.csv
Outputs: outputs/chart_*.png
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

BG     = '#0f1117'
PANEL  = '#1a1d27'
GREEN  = '#2ecc71'
RED    = '#e74c3c'
BLUE   = '#3498db'
ORANGE = '#e67e22'
PURPLE = '#9b59b6'
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

# ── Load query results ─────────────────────────────────────────────────────
q1 = pd.read_csv(f'{OUT_DIR}/q1_monthly_volume.csv')
q2 = pd.read_csv(f'{OUT_DIR}/q2_state_performance.csv')
q3 = pd.read_csv(f'{OUT_DIR}/q3_seller_ranking.csv')
q4 = pd.read_csv(f'{OUT_DIR}/q4_category_freight.csv')
q5 = pd.read_csv(f'{OUT_DIR}/q5_satisfaction_speed.csv')
q7 = pd.read_csv(f'{OUT_DIR}/q7_pareto_analysis.csv')

# ── CHART: On-Time Rate trend + Order Volume ───────────────────────────────
plot_q1 = q1[q1['YearMonth'] >= '2017-01'].copy()
fig, ax1 = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor(BG)
styled_ax(ax1, 'Monthly Order Volume & On-Time Delivery Rate (2017-2018)',
          'Month', 'Orders')
x = range(len(plot_q1))
ax1.fill_between(x, plot_q1['total_orders'], alpha=0.2, color=BLUE)
ax1.plot(x, plot_q1['total_orders'], color=BLUE, linewidth=2, marker='o', markersize=4, label='Total Orders')
ax1.set_xticks(list(x)[::2])
ax1.set_xticklabels(plot_q1['YearMonth'].iloc[::2], rotation=45, ha='right', fontsize=8)
ax2 = ax1.twinx()
ax2.plot(x, plot_q1['on_time_rate_pct'], color=GREEN, linewidth=2.5, marker='s', markersize=5, label='On-Time Rate %')
ax2.set_ylabel('On-Time Rate %', color=GREY, fontsize=9)
ax2.tick_params(colors=GREY, labelsize=8)
ax2.spines[:].set_visible(False)
ax2.set_ylim(80, 100)
ax1.legend(facecolor=PANEL, labelcolor=WHITE, fontsize=8, loc='upper left')
ax2.legend(facecolor=PANEL, labelcolor=WHITE, fontsize=8, loc='upper right')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_ontime_trend.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("chart_ontime_trend.png saved")

# ── CHART: SLA Breach by State (Top 15) ────────────────────────────────────
top_breach = q2[q2['total_orders'] >= 100].nlargest(15, 'sla_breach_rate_pct')
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'SLA Breach Rate by State — Top 15\n(% Orders Delivered Late)', 'Breach Rate %', '')
colors = [RED if v > 15 else ORANGE if v > 8 else GREEN for v in top_breach['sla_breach_rate_pct']]
bars = ax.barh(top_breach['customer_state'], top_breach['sla_breach_rate_pct'],
               color=colors, edgecolor='none', height=0.6)
for bar, val in zip(bars, top_breach['sla_breach_rate_pct']):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, color=WHITE, fontweight='bold')
ax.tick_params(axis='y', colors=WHITE)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_sla_breach_state.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("chart_sla_breach_state.png saved")

# ── CHART: Satisfaction by Delivery Speed ──────────────────────────────────
fig, (ax_rev, ax_ord) = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor(BG)
colors_speed = [GREEN, BLUE, ORANGE, RED]
styled_ax(ax_rev, 'Avg Review Score by Delivery Speed', 'Speed Bucket', 'Avg Review Score (/5)')
bars = ax_rev.bar(range(len(q5)), q5['avg_review'], color=colors_speed, edgecolor='none', width=0.6)
ax_rev.set_xticks(range(len(q5)))
ax_rev.set_xticklabels([b.replace('_', '\n') for b in q5['delivery_bucket']], color=WHITE, fontsize=8)
ax_rev.set_ylim(3.5, 5.0)
for bar, val in zip(bars, q5['avg_review']):
    ax_rev.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', fontsize=9, color=WHITE, fontweight='bold')
styled_ax(ax_ord, 'Order Volume by Delivery Speed', 'Speed Bucket', 'Orders')
ax_ord.bar(range(len(q5)), q5['orders'], color=colors_speed, edgecolor='none', width=0.6)
ax_ord.set_xticks(range(len(q5)))
ax_ord.set_xticklabels([b.replace('_', '\n') for b in q5['delivery_bucket']], color=WHITE, fontsize=8)
plt.suptitle('Customer Satisfaction vs Delivery Speed', color=WHITE, fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_satisfaction_speed.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("chart_satisfaction_speed.png saved")

# ── CHART: Freight burden by category (top 15) ─────────────────────────────
top_freight = q4.nlargest(15, 'freight_pct_of_order').sort_values('freight_pct_of_order')
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'Freight Cost as % of Order Value — Top 15 Categories', 'Freight %', '')
colors_f = [RED if v > 30 else ORANGE if v > 20 else BLUE for v in top_freight['freight_pct_of_order']]
bars = ax.barh(top_freight['category'], top_freight['freight_pct_of_order'],
               color=colors_f, edgecolor='none', height=0.6)
for bar, val in zip(bars, top_freight['freight_pct_of_order']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, color=WHITE, fontweight='bold')
ax.tick_params(axis='y', colors=WHITE, labelsize=8)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_freight_by_category.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("chart_freight_by_category.png saved")

# ── CHART: Pareto — cumulative revenue by seller ──────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor(BG)
styled_ax(ax, 'Seller Revenue Pareto — Cumulative Revenue Share\n(Top 50 Sellers)',
          'Revenue Rank', 'Cumulative Revenue Share (%)')
ax.fill_between(q7['revenue_rank'], q7['cumulative_revenue_share_pct'],
                alpha=0.25, color=PURPLE)
ax.plot(q7['revenue_rank'], q7['cumulative_revenue_share_pct'],
        color=PURPLE, linewidth=2.5, marker='o', markersize=4)
ax.axhline(80, color=ORANGE, linestyle='--', linewidth=1.2, alpha=0.7)
ax.text(q7['revenue_rank'].max() * 0.6, 81, '80% revenue threshold',
        color=ORANGE, fontsize=9)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.tick_params(colors=GREY)
ax.set_ylim(0, 105)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/chart_seller_pareto.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("chart_seller_pareto.png saved")

print(f"\n[06] All charts complete -> outputs/")
