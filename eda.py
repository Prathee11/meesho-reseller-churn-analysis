import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Setup ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('meesho_resellers.csv')

# Create a folder to save all charts automatically
os.makedirs('charts', exist_ok=True)

# Global style — makes all charts look clean and professional
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150

# ── Chart 1: Churn Rate by City Tier (Bar Chart) ─────────────────────────────
# SQL Finding: Tier 3 churn = 37.5% vs Tier 1 = 17.2%
# This chart makes that gap visual and impossible to ignore

churn_by_tier = (
    df.groupby('city_tier')['churn_label']
    .mean()
    .mul(100)
    .round(1)
    .reset_index()
)
churn_by_tier.columns = ['city_tier', 'churn_rate']
churn_by_tier['city_tier'] = churn_by_tier['city_tier'].map(
    {1: 'Tier 1', 2: 'Tier 2', 3: 'Tier 3'}
)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    churn_by_tier['city_tier'],
    churn_by_tier['churn_rate'],
    color=['#4CAF50', '#FFC107', '#F44336'],
    width=0.5,
    edgecolor='white'
)

# Add value labels on top of each bar
for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{bar.get_height():.1f}%",
        ha='center', va='bottom',
        fontsize=12, fontweight='bold'
    )

ax.set_title('Churn Rate by City Tier', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('City Tier', fontsize=12)
ax.set_ylabel('Churn Rate (%)', fontsize=12)
ax.set_ylim(0, 50)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
plt.tight_layout()
plt.savefig('charts/01_churn_by_tier.png')
plt.close()
print("Chart 1 saved")

# ── Chart 2: Return Rate Tipping Point (Line + Area Chart) ───────────────────
# SQL Finding: Churn doubles after 21.2% return rate
# Line chart shows the flat-flat-flat-SPIKE pattern clearly

return_buckets = pd.cut(
    df['return_rate'],
    bins=5,
    labels=['0–9%', '9–15%', '15–21%', '21–30%', '30–80%']
)
df['return_bucket'] = return_buckets

tipping_data = (
    df.groupby('return_bucket', observed=True)['churn_label']
    .mean()
    .mul(100)
    .round(1)
    .reset_index()
)
tipping_data.columns = ['return_rate_range', 'churn_rate']

fig, ax = plt.subplots(figsize=(9, 5))

# Area fill under the line
ax.fill_between(
    range(len(tipping_data)),
    tipping_data['churn_rate'],
    alpha=0.15,
    color='#F44336'
)

# Line
ax.plot(
    range(len(tipping_data)),
    tipping_data['churn_rate'],
    color='#F44336',
    linewidth=2.5,
    marker='o',
    markersize=8,
    markerfacecolor='white',
    markeredgewidth=2
)

# Annotate the tipping point
ax.annotate(
    '⚠ Tipping Point\n21.2% return rate',
    xy=(3, tipping_data['churn_rate'].iloc[3]),
    xytext=(3.2, tipping_data['churn_rate'].iloc[3] - 8),
    fontsize=10,
    color='#D32F2F',
    fontweight='bold',
    arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5)
)

# Value labels
for i, row in tipping_data.iterrows():
    ax.text(i, row['churn_rate'] + 1, f"{row['churn_rate']}%",
            ha='center', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(tipping_data)))
ax.set_xticklabels(tipping_data['return_rate_range'], fontsize=10)
ax.set_title('Return Rate Tipping Point — Where Churn Doubles',
             fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Return Rate Range', fontsize=12)
ax.set_ylabel('Churn Rate (%)', fontsize=12)
ax.set_ylim(0, 55)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
plt.tight_layout()
plt.savefig('charts/02_return_rate_tipping_point.png')
plt.close()
print("Chart 2 saved")

# ── Chart 3: Churn Heatmap — Category vs City Tier ───────────────────────────
# SQL Finding: Tier 3 dominates all categories
# Heatmap shows the full picture in one visual

heatmap_data = (
    df.groupby(['primary_category', 'city_tier'])['churn_label']
    .mean()
    .mul(100)
    .round(1)
    .unstack()
)
heatmap_data.columns = ['Tier 1', 'Tier 2', 'Tier 3']

fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt='.1f',
    cmap='RdYlGn_r',       # Red = high churn, Green = low churn
    linewidths=0.5,
    linecolor='white',
    annot_kws={'size': 12, 'weight': 'bold'},
    cbar_kws={'label': 'Churn Rate (%)'},
    ax=ax
)
ax.set_title('Churn Rate Heatmap — Category vs City Tier',
             fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('City Tier', fontsize=12)
ax.set_ylabel('Product Category', fontsize=12)
ax.tick_params(axis='x', rotation=0)
ax.tick_params(axis='y', rotation=0)
plt.tight_layout()
plt.savefig('charts/03_churn_heatmap.png')
plt.close()
print("Chart 3 saved")

# ── Chart 4: GMV Distribution — Churned vs Active (Box Plot) ─────────────────
# Business question: Do high GMV resellers churn less?
# Box plot shows spread of GMV for both groups side by side

df['status'] = df['churn_label'].map({0: 'Active', 1: 'Churned'})

# Cap GMV at 95th percentile to remove extreme outliers for cleaner visual
gmv_cap = df['monthly_gmv'].quantile(0.95)
df_capped = df[df['monthly_gmv'] <= gmv_cap].copy()

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=df_capped,
    x='status',
    y='monthly_gmv',
    palette={'Active': '#4CAF50', 'Churned': '#F44336'},
    width=0.4,
    linewidth=1.5,
    ax=ax
)

ax.set_title('Monthly GMV Distribution — Active vs Churned Resellers',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Reseller Status', fontsize=12)
ax.set_ylabel('Monthly GMV (₹)', fontsize=12)
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}')
)
plt.tight_layout()
plt.savefig('charts/04_gmv_distribution.png')
plt.close()
print("Chart 4 saved")

print("\nAll 4 charts saved in the 'charts' folder.")
print("Open the folder and check each one.")