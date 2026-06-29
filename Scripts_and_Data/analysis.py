def summarize(df, label, AREA_LABELS):
    counts = df["area"].value_counts(normalize=True).mul(100).round(1)

    print(f"\n=== {label} ===")
    for area in AREA_LABELS:
        print(f"  {area}: {counts.get(area, 0.0)} %")
        

def hazard_rate(df):
    return (df["area"] != "Area 1 (known safe)").mean() * 100

def area_rate(df, area):
    return (df["area"] == area).mean() * 100

