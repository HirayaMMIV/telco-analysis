"""
Telco Network Dataset Analyzer
Author: Magno Grijaldo dataset
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 1. LOAD THE DATA
# -----------------------------
CSV_FILE = "TelcoNetwork_Dataset_MagnoGrijaldo.csv"

df = pd.read_csv(CSV_FILE, on_bad_lines="skip")

# Clean column names (strip whitespace)
df.columns = [c.strip() for c in df.columns]

print("=== SHAPE ===")
print(df.shape)
print("\n=== COLUMNS ===")
print(df.columns.tolist())
print("\n=== DTYPES ===")
print(df.dtypes)
print("\n=== FIRST 5 ROWS ===")
print(df.head())

# -----------------------------
# 2. CLEAN DATA
# -----------------------------
# Fix timestamp
df["Current Date Time"] = pd.to_datetime(df["Current Date Time"], errors="coerce")

# Fix latitude/longitude glitches like -60013, -3066, -2891
def fix_coord(val, ref):
    """Repair truncated coordinates missing a decimal."""
    if pd.isna(val):
        return val
    try:
        v = float(val)
    except (TypeError, ValueError):
        return np.nan
    if abs(v) > 180:  # invalid as-is, needs decimal insertion
        s = str(int(abs(v)))
        if len(s) >= 5:
            # Insert decimal after 1st digit (e.g. 60013 -> 60.013)
            fixed = float(s[0] + "." + s[1:])
        else:
            fixed = abs(v) / 1000
        return -fixed if ref < 0 else fixed
    return v

df["Latitude"] = df.apply(lambda r: fix_coord(r["Latitude"], -1), axis=1)
df["Longitude"] = df.apply(lambda r: fix_coord(r["Longitude"], -1), axis=1)

# Drop bad coordinate rows
df = df.dropna(subset=["Latitude", "Longitude"])

print("\n=== AFTER CLEANING ===")
print(df.shape)
print(df[["Latitude", "Longitude"]].describe())

# -----------------------------
# 3. BASIC STATISTICS
# -----------------------------
print("\n=== SIGNAL STRENGTH (dBm) STATS ===")
print(df["dBm"].describe())

print("\n=== NETWORK TYPE COUNT ===")
print(df["Network Type"].value_counts())

print("\n=== NETWORK OPERATOR COUNT ===")
print(df["Network Operator"].value_counts())

print("\n=== BAND COUNT ===")
print(df["Band"].value_counts())

# -----------------------------
# 4. VISUALIZATIONS
# -----------------------------
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (a) dBm histogram
axes[0, 0].hist(df["dBm"].dropna(), bins=30, color="steelblue", edgecolor="black")
axes[0, 0].set_title("Signal Strength Distribution (dBm)")
axes[0, 0].set_xlabel("dBm")
axes[0, 0].set_ylabel("Count")

# (b) Operator vs Network Type
sns.countplot(data=df, x="Network Operator", hue="Network Type", ax=axes[0, 1])
axes[0, 1].set_title("Records per Operator & Network Type")

# (c) Boxplot dBm per Operator
sns.boxplot(data=df, x="Network Operator", y="dBm", ax=axes[1, 0])
axes[1, 0].set_title("Signal Strength by Operator")

# (d) Scatter of lat/long colored by dBm
sc = axes[1, 1].scatter(df["Longitude"], df["Latitude"], c=df["dBm"],
                        cmap="viridis", s=15, alpha=0.7)
axes[1, 1].set_title("Sample Locations (color = dBm)")
axes[1, 1].set_xlabel("Longitude")
axes[1, 1].set_ylabel("Latitude")
plt.colorbar(sc, ax=axes[1, 1], label="dBm")

plt.tight_layout()
plt.savefig("telco_overview.png", dpi=150)
plt.show()

# -----------------------------
# 5. EXPORT CLEANED DATA
# -----------------------------
df.to_csv("telco_cleaned.csv", index=False)
print("\nSaved cleaned dataset -> telco_cleaned.csv")
print("Saved plots        -> telco_overview.png")