# simulator/anomaly_scenarios.py
import random

# mapping par capteur — évite les anomalies non-pertinentes
ANOMALY_MAP = {
    "temperature": [
        "temperature_spike",
        "temperature_drop",
        "temperature_heat_stress",
        "temperature_cold_stress",
    ],
    "humidity": [
        "humidity_drop",
        "humidity_spike",
        "humidity_very_dry",
        "humidity_very_humid",
    ],
    "moisture": [
        "moisture_drop_fast",
        "moisture_prolonged_low",
    ],
    # correlation/drift/missing gérés directement par sensor_type
}

# -------------------------------------------------------------------
# GENERATEURS D'ANOMALIES (valeurs réalistes selon ton tableau)
# -------------------------------------------------------------------
def generate_temperature_spike(base):
    return base + random.uniform(8, 15)

def generate_temperature_drop(base):
    return max(-50, base - random.uniform(8, 15))  # -50 safety floor

def generate_temperature_heat_stress(base):
    return random.uniform(33, 40)

def generate_temperature_cold_stress(base):
    return random.uniform(2, 9)

def generate_humidity_drop(base):
    return max(0, base - random.uniform(25, 40))

def generate_humidity_spike(base):
    return min(100, base + random.uniform(20, 35))

def generate_humidity_very_dry(base):
    return random.uniform(10, 29)

def generate_humidity_very_humid(base):
    return random.uniform(86, 100)

def generate_moisture_drop_fast(base):
    return max(0, base - random.uniform(10, 25))

def generate_moisture_prolonged_low(base):
    return random.uniform(5, 34)

def generate_temp_humidity_index_shift(temp, hum):
    # on modifie temp fortement sans changer hum pour casser l'indice
    return temp + random.uniform(8, 18), hum

def generate_negative_correlation(temp, moisture):
    # temp monte mais moisture chute fortement
    return temp + random.uniform(5, 12), max(0, moisture - random.uniform(12, 30))

def generate_missing_reading():
    # signal pour indiquer "aucune lecture"
    return None

def generate_data_drift_triplet(temp, hum, moisture):
    # dérive lente sur 1 step (simule portion de dérive progressive)
    dt = temp + random.uniform(-0.8, 2.0)
    dh = hum + random.uniform(-3.0, 3.0)
    dm = moisture + random.uniform(-3.0, 3.0)
    # bornes pratiques
    dt = max(-50, min(60, dt))
    dh = max(0, min(100, dh))
    dm = max(0, min(100, dm))
    return dt, dh, dm

# -------------------------------------------------------------------
# APPLY (choisir et appliquer l'anomalie)
# -------------------------------------------------------------------
def apply_anomaly(sensor_type, base_value, related_value=None):
    """
    sensor_type:
      - "temperature" -> base_value: float
      - "humidity"    -> base_value: float
      - "moisture"    -> base_value: float
      - "correlation" -> base_value: (temp, moisture) tuple OR pass related_value
      - "drift"       -> base_value: (temp, hum, moisture) tuple
      - "missing"     -> base_value ignored
    RETURNS:
      - For single sensors: (new_value, anomaly_name)
      - For correlation: (new_temp, new_moisture, anomaly_name)
      - For drift: (new_temp, new_hum, new_moisture, anomaly_name)
      - For missing: (None, "missing_readings")
    """

    # ---------- MISSING ----------
    if sensor_type == "missing":
        return generate_missing_reading(), "missing_readings"

    # ---------- DRIFT (triple) ----------
    if sensor_type == "drift":
        # base_value must be tuple (temp, hum, moisture)
        try:
            temp, hum, moisture = base_value
        except Exception:
            # sécurité: si mauvaise entrée, renvoyer inchangé
            return base_value, None
        t2, h2, m2 = generate_data_drift_triplet(temp, hum, moisture)
        return t2, h2, m2, "data_drift"

    # ---------- CORRELATION ----------
    if sensor_type == "correlation":
        # base_value expected (temp, moisture) or related_value provided
        if isinstance(base_value, tuple) and len(base_value) >= 2:
            temp, moisture = base_value[0], base_value[1]
        elif isinstance(related_value, tuple) and len(related_value) >= 2:
            temp, moisture = related_value[0], related_value[1]
        else:
            return base_value, None

        # two possible correlation anomalies: negative correlation or THI shift
        if random.random() < 0.5:
            t2, m2 = generate_negative_correlation(temp, moisture)
            return t2, m2, "negative_moisture_temperature_correlation"
        else:
            t2, h_dummy = generate_temp_humidity_index_shift(temp, None)
            # return temp and keep moisture (we use "temp_humidity_index_shift" as label)
            return t2, moisture, "temp_humidity_index_shift"

    # ---------- SINGLE-SENSOR ANOMALIES ----------
    # choose from mapping list relevant to the sensor
    choices = None
    if sensor_type in ANOMALY_MAP:
        choices = ANOMALY_MAP[sensor_type]
    else:
        # if unknown sensor_type, do nothing
        return base_value, None

    anomaly = random.choice(choices)

    # Temperature anomalies
    if anomaly == "temperature_spike":
        return generate_temperature_spike(base_value), anomaly
    if anomaly == "temperature_drop":
        return generate_temperature_drop(base_value), anomaly
    if anomaly == "temperature_heat_stress":
        return generate_temperature_heat_stress(base_value), anomaly
    if anomaly == "temperature_cold_stress":
        return generate_temperature_cold_stress(base_value), anomaly

    # Humidity anomalies
    if anomaly == "humidity_drop":
        return generate_humidity_drop(base_value), anomaly
    if anomaly == "humidity_spike":
        return generate_humidity_spike(base_value), anomaly
    if anomaly == "humidity_very_dry":
        return generate_humidity_very_dry(base_value), anomaly
    if anomaly == "humidity_very_humid":
        return generate_humidity_very_humid(base_value), anomaly

    # Moisture anomalies
    if anomaly == "moisture_drop_fast":
        return generate_moisture_drop_fast(base_value), anomaly
    if anomaly == "moisture_prolonged_low":
        return generate_moisture_prolonged_low(base_value), anomaly

    # fallback
    return base_value, None

def maybe_trigger_anomaly(prob=0.10):
    """
    Probabilité par défaut de déclencher une anomalie (10%).
    Tu peux ajuster ce paramètre à l'appel.
    """
    return random.random() < prob
