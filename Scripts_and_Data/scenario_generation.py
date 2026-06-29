def generate_scenarios(n,
                       SPEED_RANGE_KMH,
                       FOG_SEVERITY_RANGE,
                       SENSOR_NOISE_RANGE,
                       ADDED_LATENCY_RANGE,
                       fog_cap=1.0,
                       noise_cap=2.0):
    import numpy as np
    import pandas as pd

    speed = np.random.uniform(*SPEED_RANGE_KMH, n)
    fog = np.random.uniform(*FOG_SEVERITY_RANGE, n)
    noise = np.random.uniform(*SENSOR_NOISE_RANGE, n)
    latency = np.random.uniform(*ADDED_LATENCY_RANGE, n)

    df = pd.DataFrame({
        "speed_kmh": speed,
        "fog_severity": fog,
        "sensor_noise_std": noise,
        "added_latency_s": latency,
    })

    df = df[df["fog_severity"] <= fog_cap].reset_index(drop=True)
    df["sensor_noise_std"] = df["sensor_noise_std"].clip(upper=noise_cap)

    return df