def setup_plot_style(CB, CG):
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": CG,
        "axes.edgecolor": CB,
        "axes.labelcolor": CB,
        "xtick.color": CB,
        "ytick.color": CB,
        "text.color": CB,
        "grid.color": "white",
        "grid.linewidth": 0.8,
        "axes.grid": True,
    })


def area_legend(ax, SHORT_LABELS, COLORS, loc="upper right"):
    import matplotlib.patches as mpatches

    handles = [
        mpatches.Patch(color=c, label=l)
        for l, c in zip(SHORT_LABELS, COLORS)
    ]
    ax.legend(handles=handles, loc=loc, fontsize=8, framealpha=0.9)


def run_all_plots(rounds, cfg, CAT_V10, CAT_V12):
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    from scipy.stats import gaussian_kde
    from matplotlib.colors import LinearSegmentedColormap

    os.makedirs("results", exist_ok=True)

    r0, r1, r2, r3 = rounds

    COLOR_MAP = {
        "Area 1 (known safe)": cfg["C1"],
        "Area 2 (known unsafe - documented trigger)": cfg["C2"],
        "Area 3 (unknown unsafe - undiscovered trigger)": cfg["C3"],
    }

    SHORT_LABELS = [
        "Area 1 — Known Safe",
        "Area 2 — Known Unsafe",
        "Area 3 — Unknown Unsafe"
    ]

    CB = cfg["CB"]

    # marker shape + size/alpha per area, layered so Area 2/3 sit on top of
    # the dominant Area 1 background and don't get lost in color alone
    AREA_STYLE = {
        "Area 1 (known safe)":                            dict(marker="o", s=5,  alpha=0.30, z=2),
        "Area 2 (known unsafe - documented trigger)":      dict(marker="^", s=14, alpha=0.85, z=3),
        "Area 3 (unknown unsafe - undiscovered trigger)":  dict(marker="X", s=20, alpha=0.95, z=4),
    }

    def plot_round_scatter(ax, data):
        for area, style in AREA_STYLE.items():
            sub = data[data["area"] == area]
            ax.scatter(
                sub["fog_severity"], sub["sensor_noise_std"],
                c=COLOR_MAP[area], marker=style["marker"], s=style["s"],
                alpha=style["alpha"], linewidths=0, zorder=style["z"]
            )

    # =========================================================
    # VIZ 1 — Fog vs Noise (every round, not just baseline vs final)
    # =========================================================
    round_labels = cfg.get(
        "ROUND_LABELS",
        [f"Round {i}" for i in range(len(rounds))]
    )

    n = len(rounds)
    ncols = 2 if n > 1 else 1
    nrows = -(-n // ncols)  # ceil division

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(6.5 * ncols, 5.2 * nrows),
        sharex=True, sharey=True
    )
    axes = np.array(axes).reshape(-1)

    for ax, data, title in zip(axes, rounds, round_labels):
        plot_round_scatter(ax, data)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Fog severity (0 = clear, 1 = dense)")

    for ax in axes[:nrows * ncols:ncols]:
        ax.set_ylabel("Sensor noise standard deviation")

    area_legend(axes[0], SHORT_LABELS, [cfg["C1"], cfg["C2"], cfg["C3"]], loc="upper right")

    # hide any unused subplot slots (e.g. an odd number of rounds)
    for ax in axes[n:]:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig("results/viz1.png", dpi=150)
    plt.close()

    # ---------------------------------------------------------
    # VIZ 1b — same plot, also saved as 4 separate standalone figures
    # ---------------------------------------------------------
    import re

    def slugify(label):
        return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")

    for data, title in zip(rounds, round_labels):
        fig, ax = plt.subplots(figsize=(7, 5.5))
        plot_round_scatter(ax, data)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Fog severity (0 = clear, 1 = dense)")
        ax.set_ylabel("Sensor noise standard deviation")
        area_legend(ax, SHORT_LABELS, [cfg["C1"], cfg["C2"], cfg["C3"]], loc="upper right")
        plt.tight_layout()
        plt.savefig(f"results/viz1_{slugify(title.replace(chr(10), '_'))}.png", dpi=150)
        plt.close()

    # =========================================================
    # VIZ 2 — KDE Area 3 (Rounds 1, 2, 3 only — baseline excluded)
    # =========================================================
    viz2_rounds = rounds[1:4]
    viz2_labels = round_labels[1:4]
    n2 = len(viz2_rounds)
    ncols2 = n2
    nrows2 = 1

    fig, axes = plt.subplots(
        nrows2, ncols2, figsize=(6.5 * ncols2, 5.2 * nrows2),
        sharex=True, sharey=True
    )
    axes = np.array(axes).reshape(-1)

    cmap = LinearSegmentedColormap.from_list(
        "red_map", ["#ffffff", "#e74c3c", "#7f0000"]
    )

    for ax, data, title in zip(axes, viz2_rounds, viz2_labels):
        a3 = data[data["area"] == "Area 3 (unknown unsafe - undiscovered trigger)"]

        if len(a3) > 10:
            xy = np.vstack([a3["fog_severity"], a3["sensor_noise_std"]])
            kde = gaussian_kde(xy)

            xg = np.linspace(0, 1, 120)
            yg = np.linspace(0, 2, 120)
            XX, YY = np.meshgrid(xg, yg)
            ZZ = kde(np.vstack([XX.ravel(), YY.ravel()])).reshape(XX.shape)

            ax.contourf(XX, YY, ZZ, levels=12, cmap=cmap)
        else:
            ax.text(
                0.5, 0.5,
                f"Only {len(a3)} Area 3\nscenario(s) — too few\nfor a density estimate",
                ha="center", va="center", fontsize=9, color=CB,
                transform=ax.transAxes
            )

        ax.set_title(f"{title}  (n={len(a3)})", fontsize=11, fontweight="bold")
        ax.set_xlabel("Fog severity")

    axes[0].set_ylabel("Sensor noise std dev")

    plt.tight_layout()
    plt.savefig("results/viz2.png", dpi=150)
    plt.close()

    # =========================================================
    # VIZ 3 — Waterfall (Hazard breakdown)
    # =========================================================
    def area_rate(df, a):
        return (df["area"] == a).mean() * 100

    a2 = [area_rate(d, "Area 2 (known unsafe - documented trigger)") for d in rounds]
    a3 = [area_rate(d, "Area 3 (unknown unsafe - undiscovered trigger)") for d in rounds]

    x = np.arange(4)

    plt.figure(figsize=(9, 5))
    plt.bar(x, a2, label="Area 2 (Known Unsafe)")
    plt.bar(x, a3, bottom=a2, label="Area 3 (Unknown Unsafe)")

    plt.xticks(x, ["R0", "R1", "R2", "R3"])
    plt.ylabel("Hazard rate (%)")
    plt.title("SOTIF Risk Reduction Across Rounds")
    plt.legend()

    plt.savefig("results/viz3.png", dpi=150)
    plt.close()

    # =========================================================
    # VIZ 4 — Speed vs Latency
    # =========================================================
    plt.figure(figsize=(7, 5))

    for area, color in COLOR_MAP.items():
        sub = r0[r0["area"] == area]
        plt.scatter(sub["added_latency_s"], sub["speed_kmh"], c=color, s=5, label=area)

    plt.xlabel("Processing latency (s)")
    plt.ylabel("Ego speed (km/h)")
    plt.title("Kinematic Conditions vs SOTIF Area")
    plt.legend()

    plt.savefig("results/viz4.png", dpi=150)
    plt.close()

    # =========================================================
    # VIZ 5 — Parallel Coordinates
    # =========================================================
    sample = r0.sample(1500, random_state=0)
    cols = ["fog_severity", "sensor_noise_std", "added_latency_s", "speed_kmh"]

    norm = sample[cols].copy()
    for c in cols:
        mn, mx = norm[c].min(), norm[c].max()
        norm[c] = (norm[c] - mn) / (mx - mn + 1e-9)

    plt.figure(figsize=(10, 5))

    for _, row in norm.iterrows():
        plt.plot(range(len(cols)), row.values, alpha=0.1)

    plt.xticks(range(len(cols)), cols)
    plt.title("Multi-dimensional Triggering Conditions")
    plt.savefig("results/viz5.png", dpi=150)
    plt.close()