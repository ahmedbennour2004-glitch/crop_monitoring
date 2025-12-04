# simulator/sensor_simulator.py
import requests
import time
import math
import random
from datetime import datetime

from anomaly_scenarios import (
    apply_anomaly,
    maybe_trigger_anomaly,
)

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"

# Ton token — garde-le secret
JWT_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0ODg3OTIwLCJpYXQiOjE3NjQ4ODc2MjAsImp0aSI6ImIyMGU1M2VlZTZjNDQ4ZTRhNDE5MjY4ZGYyMjk2NGQ0IiwidXNlcl9pZCI6IjEifQ.-A0Bh8YMXmNN5TIrtWNCiFLvgfY5pD3iIDi_UsCR3mM"
HEADERS = {
    "Authorization": f"Bearer {JWT_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

PLOTS = [1, 2]
SEND_INTERVAL = 5  # secondes

# stockage des moisture par plot
soil_moisture = {plot: 65.0 for plot in PLOTS}

# -------------------------
# VALEURS NORMALES
# -------------------------
def diurnal_temperature(hour):
    # journée centrée ~23°C, amplitude raisonnable
    return 23 + 5 * math.sin((hour / 24) * 2 * math.pi)

def humidity_baseline():
    return random.uniform(50, 75)

def soil_moisture_next(prev):
    return max(0.0, prev - random.uniform(0.1, 0.5))

# -------------------------
# ENVOI API
# -------------------------
def send_reading(plot, sensor_type, value):
    # ignore None values (missing reading)
    if value is None:
        return None

    payload = {
        "plot": plot,
        "sensor_type": sensor_type,
        "value": round(float(value), 3),
    }

    try:
        r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=5)
        print(f"[{datetime.now().isoformat()}] POST {sensor_type}={value} -> {r.status_code}")
        if r.status_code >= 400:
            print("  Response:", r.text)
        return r
    except Exception as e:
        print("Erreur HTTP:", e)
        return None

# -------------------------
# MAIN
# -------------------------
def main():
    print("Simulator started with anomaly injection...\n")

    while True:
        now = datetime.now()
        hour = now.hour

        for plot in PLOTS:
            # valeurs normales
            temp = diurnal_temperature(hour)
            hum = humidity_baseline()
            soil_moisture[plot] = soil_moisture_next(soil_moisture[plot])

            # -------------------------
            # ANOMALIES (gérées proprement)
            # -------------------------

            # Temperature (single)
            if maybe_trigger_anomaly(0.08):  # probabilité par type (ajustable)
                temp_new, a = apply_anomaly("temperature", temp)
                print(f"\n⚠️  ANOMALIE SUR TEMPÉRATURE -> {a}")
                temp = temp_new

            # Humidity (single)
            if maybe_trigger_anomaly(0.08):
                hum_new, a = apply_anomaly("humidity", hum)
                print(f"\n⚠️  ANOMALIE SUR HUMIDITÉ -> {a}")
                hum = hum_new

            # Moisture (single)
            if maybe_trigger_anomaly(0.08):
                moisture_new, a = apply_anomaly("moisture", soil_moisture[plot])
                print(f"\n⚠️  ANOMALIE SUR MOISTURE -> {a}")
                soil_moisture[plot] = moisture_new

            # Correlation (temp <-> moisture) : renvoie (temp, moisture, label)
            if maybe_trigger_anomaly(0.03):  # plus rare
                t_corr, m_corr, a = apply_anomaly("correlation", (temp, soil_moisture[plot]))
                print(f"\n⚠️  ANOMALIE DE CORRÉLATION -> {a}")
                temp = t_corr
                soil_moisture[plot] = m_corr

            # Drift (multi-sensor) : renvoie (temp, hum, moisture, label)
            if maybe_trigger_anomaly(0.02):  # rare mais possible
                t_d, h_d, m_d, a = apply_anomaly("drift", (temp, hum, soil_moisture[plot]))
                print(f"\n⚠️  ANOMALIE DRIFT -> {a}")
                temp, hum, soil_moisture[plot] = t_d, h_d, m_d

            # Missing reading (skip entire cycle for this plot)
            if maybe_trigger_anomaly(0.02):
                print("\n⚠️  ANOMALIE : lecture manquante (skip envoi pour ce tour)")
                # on skip directement l'envoi de ce tour
                continue

            # -------------------------
            # ENVOI API (si pas skip)
            # -------------------------
            send_reading(plot, "temperature", temp)
            time.sleep(0.15)
            send_reading(plot, "humidity", hum)
            time.sleep(0.15)
            send_reading(plot, "moisture", soil_moisture[plot])
            time.sleep(0.15)

        # pause globale entre cycles
        time.sleep(SEND_INTERVAL)

if __name__ == "__main__":
    main()
