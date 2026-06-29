def required_stopping_distance(speed_kmh, added_latency_s,
                               BASE_REACTION_TIME_S,
                               DECELERATION_MPS2,
                               SAFETY_BUFFER_M,
                               extra_buffer=0.0):
    v = speed_kmh / 3.6
    reaction_time = BASE_REACTION_TIME_S + added_latency_s
    reaction_dist = v * reaction_time
    braking_dist = v ** 2 / (2 * DECELERATION_MPS2)

    return reaction_dist + braking_dist + SAFETY_BUFFER_M + extra_buffer

def effective_detection_range(fog_severity,
                              sensor_noise_std,
                              BASE_DETECTION_RANGE_M,
                              FOG_ATTENUATION_FACTOR,
                              NOISE_RANGE_PENALTY_M,
                              INTERACTION_PENALTY_M):
    range_m = BASE_DETECTION_RANGE_M * (1 - fog_severity * FOG_ATTENUATION_FACTOR)
    range_m -= sensor_noise_std * NOISE_RANGE_PENALTY_M

    if fog_severity > 0.25 and sensor_noise_std > 0.8:
        range_m -= INTERACTION_PENALTY_M

    return max(range_m, 0.0)


