import pandas as pd
from pathlib import Path

BASE = Path(".")

# Load flood datasets
area = pd.read_csv(BASE / "District_FloodedArea.csv")
impact = pd.read_csv(BASE / "District_FloodImpact.csv")
inventory = pd.read_csv(BASE / "India_Flood_Inventory_v3.csv")

print("Area:", area.shape)
print("Impact:", impact.shape)
print("Inventory:", inventory.shape)

# Clean column names
for df in [area, impact, inventory]:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

# Find district/state columns automatically
def find_col(df, names):
    for name in names:
        if name in df.columns:
            return name
    return None

area_dist = find_col(area, ["dist_name", "district", "district_name", "dist"])
impact_dist = find_col(impact, ["dist_name", "district", "district_name", "dist"])
inv_dist = find_col(inventory, ["district", "district_name", "dist_name", "dist"])

area_state = find_col(area, ["state", "state_name"])
impact_state = find_col(impact, ["state", "state_name"])
inv_state = find_col(inventory, ["state", "state_name"])

print("District columns:", area_dist, impact_dist, inv_dist)
print("State columns:", area_state, impact_state, inv_state)

# Create normalized district names
for df, col in [(area, area_dist), (impact, impact_dist), (inventory, inv_dist)]:
    if col:
        df["district_key"] = (
            df[col].astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"[^a-z0-9]", "", regex=True)
        )

# Aggregate inventory district-wise
if inv_dist:
    inv_agg = inventory.groupby("district_key", as_index=False).agg(
        flood_events=("district_key", "size")
    )
else:
    inv_agg = pd.DataFrame(columns=["district_key", "flood_events"])

# Merge the three flood datasets
master = area.copy()

if impact_dist:
    impact_keep = impact.copy()
    master = master.merge(
        impact_keep,
        on="district_key",
        how="outer",
        suffixes=("_area", "_impact")
    )

master = master.merge(
    inv_agg,
    on="district_key",
    how="left"
)

master["flood_events"] = master["flood_events"].fillna(0)

# Save
Path("data/processed").mkdir(parents=True, exist_ok=True)

out = "data/processed/flood_master.csv"
master.to_csv(out, index=False)

print("\nDONE!")
print("Final flood dataset:", master.shape)
print("Saved:", out)
print("\nColumns:")
print(master.columns.tolist())