import pandas as pd
import numpy as np
from faker import Faker
import random

# ── Reproducibility ──────────────────────────────────────────────────────────
# Setting a seed means you get the SAME data every time you run this script.
# Important for a project — your analysis stays consistent.
np.random.seed(42)
random.seed(42)
fake = Faker('en_IN')   # Indian locale — gives Indian names & phone numbers

# ── Config ───────────────────────────────────────────────────────────────────
N = 50_000   # 50,000 resellers

# ── Step 1: Basic reseller identity ─────────────────────────────────────────
reseller_ids   = [f"MSH{str(i).zfill(6)}" for i in range(1, N + 1)]
names          = [fake.name() for _ in range(N)]
phone_numbers  = [fake.phone_number() for _ in range(N)]

# Signup dates spread across 18 months (Jan 2022 – Jun 2023)
signup_dates = pd.to_datetime(
    np.random.choice(pd.date_range('2022-01-01', '2023-06-30'), size=N)
)

# ── Step 2: Geography ────────────────────────────────────────────────────────
# Based on Meesho's publicly stated focus: majority Tier 2/3 cities
city_tiers = np.random.choice([1, 2, 3], size=N, p=[0.15, 0.30, 0.55])

states = np.random.choice(
    ['Uttar Pradesh', 'Maharashtra', 'Rajasthan', 'Bihar',
     'West Bengal', 'Tamil Nadu', 'Madhya Pradesh', 'Gujarat',
     'Karnataka', 'Odisha'],
    size=N,
    p=[0.18, 0.14, 0.10, 0.09, 0.09, 0.08, 0.08, 0.08, 0.08, 0.08]
)

# ── Step 3: Business profile ─────────────────────────────────────────────────
# Fashion dominates Meesho — 42% of resellers primarily sell fashion
primary_category = np.random.choice(
    ['Fashion', 'Home Decor', 'Kitchen', 'Beauty', 'Electronics'],
    size=N,
    p=[0.42, 0.22, 0.15, 0.13, 0.08]
)

# Age group — Meesho's core reseller is a homemaker/young adult
age_group = np.random.choice(
    ['18-25', '26-35', '36-45', '45+'],
    size=N,
    p=[0.25, 0.40, 0.25, 0.10]
)

# ── Step 4: Business activity ────────────────────────────────────────────────
# Monthly GMV — lognormal because income is always right-skewed
# (most earn modest amounts, a few earn a lot)
# np.exp(9.5) ≈ ₹13,000 — realistic average monthly GMV
monthly_gmv = np.random.lognormal(mean=9.5, sigma=0.7, size=N).clip(500, 150_000)
monthly_gmv = monthly_gmv.round(2)

# Monthly orders — correlated with GMV (more GMV = more orders, roughly)
monthly_orders = np.random.poisson(lam=(monthly_gmv / 800).clip(1, 80))

# Average order value derived from GMV / orders (avoid division by zero)
avg_order_value = (monthly_gmv / monthly_orders.clip(1)).round(2)

# Return rate — beta distribution naturally stays between 0 and 1
# Beta(2, 8) peaks around 18–20%, which matches fashion/home decor platforms
return_rate = np.random.beta(a=2, b=8, size=N).round(4)

# Support tickets raised in last 6 months
support_tickets = np.random.poisson(lam=1.5, size=N)

# WhatsApp activity (Meesho heavily uses WhatsApp for reseller engagement)
whatsapp_active = np.random.choice([0, 1], size=N, p=[0.35, 0.65])

# Reseller tenure in days (from signup to analysis date: 2023-12-31)
analysis_date = pd.Timestamp('2023-12-31')
tenure_days = (analysis_date - signup_dates).days

# ── Step 5: Churn label — THE MOST IMPORTANT PART ───────────────────────────
# Churn is NOT assigned randomly. It is a function of real behaviour signals.
# This is what makes the analysis meaningful.
#
# Churn definition: no orders for 60+ consecutive days after being active 30 days
#
# Churn probability formula — each factor adds risk:
churn_prob = (
    0.05                                          # base rate (everyone has some risk)
    + 0.25 * (return_rate > 0.22).astype(int)    # high returns = frustrated reseller
    + 0.20 * (city_tiers == 3).astype(int)       # Tier 3 = less support, more dropout
    + 0.15 * (tenure_days < 90).astype(int)      # new resellers churn most
    + 0.10 * (monthly_orders < 3).astype(int)    # low activity = disengaged
    + 0.08 * (whatsapp_active == 0).astype(int)  # inactive on WhatsApp = less engaged
    + 0.05 * (support_tickets > 3).astype(int)   # unresolved issues = churn signal
)

# Cap probability at 0.92 so it stays realistic
churn_prob = churn_prob.clip(0, 0.92)

# Now randomly draw the actual churn label using that probability
churn_label = np.random.binomial(n=1, p=churn_prob)

# Days since last order — churned resellers have higher values
days_since_last_order = np.where(
    churn_label == 1,
    np.random.randint(60, 365, size=N),    # churned: 60–365 days ago
    np.random.randint(0, 30, size=N)       # active: within last 30 days
)

# ── Step 6: Build the DataFrame ──────────────────────────────────────────────
df = pd.DataFrame({
    'reseller_id':           reseller_ids,
    'name':                  names,
    'phone':                 phone_numbers,
    'signup_date':           signup_dates.strftime('%Y-%m-%d'),
    'state':                 states,
    'city_tier':             city_tiers,
    'age_group':             age_group,
    'primary_category':      primary_category,
    'monthly_gmv':           monthly_gmv,
    'monthly_orders':        monthly_orders,
    'avg_order_value':       avg_order_value,
    'return_rate':           return_rate,
    'support_tickets':       support_tickets,
    'whatsapp_active':       whatsapp_active,
    'tenure_days':           tenure_days,
    'days_since_last_order': days_since_last_order,
    'churn_label':           churn_label
})

# ── Step 7: Save to CSV ───────────────────────────────────────────────────────
df.to_csv('meesho_resellers.csv', index=False)

# ── Step 8: Quick sanity check — print this and verify it looks right ────────
print("=" * 50)
print(f"Total resellers     : {len(df):,}")
print(f"Churned resellers   : {churn_label.sum():,} ({churn_label.mean()*100:.1f}%)")
print(f"Avg monthly GMV     : ₹{monthly_gmv.mean():,.0f}")
print(f"Avg return rate     : {return_rate.mean()*100:.1f}%")
print(f"Tier 3 resellers    : {(city_tiers == 3).sum():,} ({(city_tiers==3).mean()*100:.0f}%)")
print("=" * 50)
print("\nFirst 3 rows preview:")
print(df.head(3).to_string())
print("\nCSV saved as: meesho_resellers.csv")