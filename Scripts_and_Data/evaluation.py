def evaluate(df,
             physics_params,
             extra_buffer=0.0):
    df = df.copy()

    from physics import required_stopping_distance, effective_detection_range

    df["required_distance_m"] = [
        required_stopping_distance(
            s, l,
            physics_params["BASE_REACTION_TIME_S"],
            physics_params["DECELERATION_MPS2"],
            physics_params["SAFETY_BUFFER_M"],
            extra_buffer
        )
        for s, l in zip(df["speed_kmh"], df["added_latency_s"])
    ]

    df["detected_range_m"] = [
        effective_detection_range(
            f, n,
            physics_params["BASE_DETECTION_RANGE_M"],
            physics_params["FOG_ATTENUATION_FACTOR"],
            physics_params["NOISE_RANGE_PENALTY_M"],
            physics_params["INTERACTION_PENALTY_M"]
        )
        for f, n in zip(df["fog_severity"], df["sensor_noise_std"])
    ]

    df["hazard"] = df["detected_range_m"] < df["required_distance_m"]

    return df