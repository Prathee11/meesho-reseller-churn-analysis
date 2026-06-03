import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import os

# ── Setup ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('meesho_resellers.csv')
os.makedirs('charts', exist_ok=True)
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.dpi'] = 150

# ══════════════════════════════════════════════════════════════════════════════
# TEST 1: Does WhatsApp activity affect churn?
# Method: Chi-Square Test
# Why: Both variables are categorical (yes/no type)
#      whatsapp_active = 0 or 1
#      churn_label = 0 or 1
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("TEST 1: WhatsApp Activity vs Churn")
print("=" * 60)

# Step 1: Build a contingency table
# This counts how many resellers fall into each combination:
# Active WhatsApp + Churned, Active WhatsApp + Not Churned, etc.
contingency_table = pd.crosstab(
    df['whatsapp_active'],
    df['churn_label'],
    rownames=['WhatsApp Active'],
    colnames=['Churned']
)
print("\nContingency Table:")
print(contingency_table)

# Step 2: Run the chi-square test
chi2, p_value_1, dof, expected = stats.chi2_contingency(contingency_table)

print(f"\nChi-Square Statistic : {chi2:.4f}")
print(f"P-Value              : {p_value_1:.6f}")
print(f"Degrees of Freedom   : {dof}")

# Step 3: Interpret the result
if p_value_1 < 0.05:
    print("\n✅ RESULT: Reject H0 — WhatsApp activity significantly affects churn")
    print("   WhatsApp inactive resellers churn at a statistically higher rate")
else:
    print("\n❌ RESULT: Cannot reject H0 — No significant relationship found")

# Step 4: Calculate churn rates for both groups to show the actual difference
whatsapp_churn = df.groupby('whatsapp_active')['churn_label'].mean().mul(100).round(1)
print(f"\nChurn rate — WhatsApp Inactive : {whatsapp_churn[0]}%")
print(f"Churn rate — WhatsApp Active   : {whatsapp_churn[1]}%")
print(f"Difference                     : {(whatsapp_churn[0] - whatsapp_churn[1]):.1f}%")

# Step 5: Visualise Test 1 — Grouped bar chart
fig, ax = plt.subplots(figsize=(8, 5))

whatsapp_labels = ['WhatsApp Inactive', 'WhatsApp Active']
churn_rates = [whatsapp_churn[0], whatsapp_churn[1]]
colors = ['#F44336', '#4CAF50']

bars = ax.bar(whatsapp_labels, churn_rates, color=colors, width=0.4, edgecolor='white')

for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{bar.get_height():.1f}%",
        ha='center', va='bottom',
        fontsize=13, fontweight='bold'
    )

# Add p-value annotation to the chart
ax.text(
    0.98, 0.95,
    f"Chi-Square p-value = {p_value_1:.4f}\n{'Statistically Significant ✅' if p_value_1 < 0.05 else 'Not Significant ❌'}",
    transform=ax.transAxes,
    fontsize=10,
    ha='right', va='top',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9C4', edgecolor='#F9A825')
)

ax.set_title('Churn Rate by WhatsApp Activity\n(Chi-Square Test)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('Churn Rate (%)', fontsize=12)
ax.set_ylim(0, 50)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
plt.tight_layout()
plt.savefig('charts/05_whatsapp_churn_test.png')
plt.close()
print("\nChart 5 saved")

# ══════════════════════════════════════════════════════════════════════════════
# TEST 2: Do Tier 3 resellers earn significantly less GMV than Tier 1?
# Method: Mann-Whitney U Test
# Why: GMV is a number (not categorical) and its distribution is skewed
#      (lognormal) — so we can't use a regular t-test
#      Mann-Whitney works on any distribution
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 2: Tier 1 vs Tier 3 Monthly GMV")
print("=" * 60)

# Step 1: Separate the two groups
tier1_gmv = df[df['city_tier'] == 1]['monthly_gmv']
tier3_gmv = df[df['city_tier'] == 3]['monthly_gmv']

print(f"\nTier 1 — Mean GMV : ₹{tier1_gmv.mean():,.0f} | Median: ₹{tier1_gmv.median():,.0f}")
print(f"Tier 3 — Mean GMV : ₹{tier3_gmv.mean():,.0f} | Median: ₹{tier3_gmv.median():,.0f}")

# Step 2: Run Mann-Whitney U Test
u_stat, p_value_2 = stats.mannwhitneyu(tier1_gmv, tier3_gmv, alternative='two-sided')

print(f"\nMann-Whitney U Statistic : {u_stat:.0f}")
print(f"P-Value                  : {p_value_2:.6f}")

# Step 3: Interpret the result
if p_value_2 < 0.05:
    print("\n✅ RESULT: Reject H0 — Tier 1 and Tier 3 GMV are significantly different")
else:
    print("\n❌ RESULT: Cannot reject H0 — No significant GMV difference found")

# Step 4: Calculate how much less Tier 3 earns
gmv_gap = tier1_gmv.median() - tier3_gmv.median()
pct_gap = (gmv_gap / tier1_gmv.median()) * 100
print(f"\nMedian GMV gap         : ₹{gmv_gap:,.0f}")
print(f"Tier 3 earns           : {pct_gap:.1f}% less than Tier 1 (median)")

# Step 5: Visualise Test 2 — KDE distribution plot
fig, ax = plt.subplots(figsize=(9, 5))

# Cap at 95th percentile for clean visual
gmv_cap = df['monthly_gmv'].quantile(0.95)
tier1_capped = tier1_gmv[tier1_gmv <= gmv_cap]
tier3_capped = tier3_gmv[tier3_gmv <= gmv_cap]

sns.kdeplot(tier1_capped, ax=ax, color='#4CAF50',
            fill=True, alpha=0.3, linewidth=2, label='Tier 1')
sns.kdeplot(tier3_capped, ax=ax, color='#F44336',
            fill=True, alpha=0.3, linewidth=2, label='Tier 3')

# Vertical median lines
ax.axvline(tier1_capped.median(), color='#2E7D32',
           linestyle='--', linewidth=1.5,
           label=f'Tier 1 Median: ₹{tier1_capped.median():,.0f}')
ax.axvline(tier3_capped.median(), color='#C62828',
           linestyle='--', linewidth=1.5,
           label=f'Tier 3 Median: ₹{tier3_capped.median():,.0f}')

# P-value annotation
ax.text(
    0.98, 0.95,
    f"Mann-Whitney p-value = {p_value_2:.4f}\n{'Statistically Significant ✅' if p_value_2 < 0.05 else 'Not Significant ❌'}",
    transform=ax.transAxes,
    fontsize=10,
    ha='right', va='top',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9C4', edgecolor='#F9A825')
)

ax.set_title('GMV Distribution — Tier 1 vs Tier 3 Resellers\n(Mann-Whitney U Test)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Monthly GMV (₹)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/06_tier_gmv_test.png')
plt.close()
print("Chart 6 saved")

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY — print all findings together
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("HYPOTHESIS TESTING SUMMARY")
print("=" * 60)
print(f"\n✅ Test 1 — WhatsApp vs Churn")
print(f"   WhatsApp inactive resellers churn {(whatsapp_churn[0] - whatsapp_churn[1]):.1f}% more")
print(f"   P-value: {p_value_1:.6f} → {'Significant' if p_value_1 < 0.05 else 'Not Significant'}")
print(f"\n✅ Test 2 — Tier 1 vs Tier 3 GMV")
print(f"   Tier 3 earns ₹{gmv_gap:,.0f} less per month (median)")
print(f"   P-value: {p_value_2:.6f} → {'Significant' if p_value_2 < 0.05 else 'Not Significant'}")
print("\nAll hypothesis testing complete. 2 charts saved in charts/ folder.")