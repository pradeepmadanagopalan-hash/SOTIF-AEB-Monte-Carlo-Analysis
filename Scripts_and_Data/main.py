

def run_pipeline():
    import os
    import numpy as np
    import pandas as pd

    from config import load_config
    from catalogue_loader import load_catalogue, get_catalogue_snapshots
    from scenario_generation import generate_scenarios
    from evaluation import evaluate
    from classification import classify_area
    from analysis import summarize, hazard_rate, area_rate
    from visualization import (
        setup_plot_style,
        area_legend,
        run_all_plots
    )

    cfg = load_config()
    os.makedirs("results", exist_ok=True)

    # ── Catalogue ─────────────────────────────
    catalogue = load_catalogue("triggering_conditions.yaml")
    CAT_V10, CAT_V11, CAT_V12 = get_catalogue_snapshots(catalogue)

    # ── Style ────────────────────────────────
    setup_plot_style(cfg["CB"], cfg["CG"])

    # ── Rounds ───────────────────────────────
    rounds = []

    # =========================
    # Round 0 — baseline
    # =========================
    r0 = generate_scenarios(
        cfg["N_SCENARIOS"],
        cfg["SPEED_RANGE_KMH"],
        cfg["FOG_SEVERITY_RANGE"],
        cfg["SENSOR_NOISE_RANGE"],
        cfg["ADDED_LATENCY_RANGE"]
    )

    r0 = evaluate(r0, cfg)
    r0["area"] = r0.apply(lambda row: classify_area(row, CAT_V10), axis=1)

    summarize(r0, "Round 0 — Baseline", [
        "Area 1 (known safe)",
        "Area 2 (known unsafe - documented trigger)",
        "Area 3 (unknown unsafe - undiscovered trigger)"
    ])

    rounds.append(r0)

    # =========================
    # Round 1 — fog ODD restriction
    # =========================
    r1 = generate_scenarios(
        cfg["N_SCENARIOS"],
        cfg["SPEED_RANGE_KMH"],
        cfg["FOG_SEVERITY_RANGE"],
        cfg["SENSOR_NOISE_RANGE"],
        cfg["ADDED_LATENCY_RANGE"],
        fog_cap=0.7
    )

    r1 = evaluate(r1, cfg)
    r1["area"] = r1.apply(lambda row: classify_area(row, CAT_V10), axis=1)

    summarize(r1, "Round 1 — Fog ODD restriction", [
        "Area 1 (known safe)",
        "Area 2 (known unsafe - documented trigger)",
        "Area 3 (unknown unsafe - undiscovered trigger)"
    ])

    rounds.append(r1)

    # =========================
    # Round 2 — noise filter
    # =========================
    r2 = generate_scenarios(
        cfg["N_SCENARIOS"],
        cfg["SPEED_RANGE_KMH"],
        cfg["FOG_SEVERITY_RANGE"],
        cfg["SENSOR_NOISE_RANGE"],
        cfg["ADDED_LATENCY_RANGE"],
        fog_cap=0.7,
        noise_cap=1.0
    )

    r2 = evaluate(r2, cfg)
    r2["area"] = r2.apply(lambda row: classify_area(row, CAT_V11), axis=1)

    summarize(r2, "Round 2 — Noise filter added", [
        "Area 1 (known safe)",
        "Area 2 (known unsafe - documented trigger)",
        "Area 3 (unknown unsafe - undiscovered trigger)"
    ])

    rounds.append(r2)

    # =========================
    # Round 3 — safety buffer
    # =========================
    r3 = generate_scenarios(
        cfg["N_SCENARIOS"],
        cfg["SPEED_RANGE_KMH"],
        cfg["FOG_SEVERITY_RANGE"],
        cfg["SENSOR_NOISE_RANGE"],
        cfg["ADDED_LATENCY_RANGE"],
        fog_cap=0.7,
        noise_cap=1.0
    )

    r3 = evaluate(r3, cfg, extra_buffer=5.0)
    r3["area"] = r3.apply(lambda row: classify_area(row, CAT_V12), axis=1)

    summarize(r3, "Round 3 — Safety buffer", [
        "Area 1 (known safe)",
        "Area 2 (known unsafe - documented trigger)",
        "Area 3 (unknown unsafe - undiscovered trigger)"
    ])

    rounds.append(r3)

    # ── Residual risk summary ────────────────
    print("\n=== Residual risk argument ===")
    for i, df in enumerate(rounds):
        print(
            f"Round {i}: "
            f"{hazard_rate(df):.1f}% hazard "
            f"(A2: {area_rate(df,'Area 2 (known unsafe - documented trigger)'):.1f}%, "
            f"A3: {area_rate(df,'Area 3 (unknown unsafe - undiscovered trigger)'):.1f}%)"
        )

    # ── Save outputs ─────────────────────────
    r0.to_csv("results/round0_baseline.csv", index=False)
    r3.to_csv("results/round3_mitigated.csv", index=False)

    # ── Run all plots ────────────────────────
    run_all_plots(rounds, cfg, CAT_V10, CAT_V12)

    print("\nPipeline complete. Outputs in /results")


if __name__ == "__main__":
    run_pipeline()
    
    

