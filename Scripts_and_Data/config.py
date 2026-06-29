def load_config():
    import numpy as np

    np.random.seed(42)
    return {
        "N_SCENARIOS": 10_000,

        "SPEED_RANGE_KMH": (30, 80),
        "FOG_SEVERITY_RANGE": (0.0, 1.0),
        "SENSOR_NOISE_RANGE": (0.0, 2.0),
        "ADDED_LATENCY_RANGE": (0.0, 0.3),

        "BASE_DETECTION_RANGE_M": 120.0,
        "FOG_ATTENUATION_FACTOR": 0.80,
        "NOISE_RANGE_PENALTY_M": 6.0,
        "INTERACTION_PENALTY_M": 25.0,

        "BASE_REACTION_TIME_S": 0.35,
        "DECELERATION_MPS2": 7.0,
        "SAFETY_BUFFER_M": 3.0,

        "C1": "#2ecc71",
        "C2": "#e67e22",
        "C3": "#e74c3c",
        "CB": "#2c3e50",
        "CG": "#ecf0f1",
    }