from django.db import models
from django.contrib.auth.models import User


# -------------------- FARM PROFILE --------------------

class FarmProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="farms")
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size = models.FloatField()  # hectares
    crop_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# -------------------- FIELD PLOT --------------------

class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name="plots")
    name = models.CharField(max_length=100)
    crop_variety = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.farm.name} - {self.name}"


# -------------------- SENSOR READING --------------------

class SensorReading(models.Model):
    SENSOR_TYPES = [
        ("moisture", "Soil Moisture"),
        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
    ]

    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="readings")
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="simulator")

    def __str__(self):
        return f"{self.plot.name} - {self.sensor_type}: {self.value}"


# -------------------- ANOMALY EVENT --------------------

class AnomalyEvent(models.Model):
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="anomalies")
    anomaly_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)  # low, medium, high
    model_confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anomaly in {self.plot.name} - {self.anomaly_type}"


# -------------------- AGENT RECOMMENDATION --------------------

class AgentRecommendation(models.Model):
    anomaly_event = models.ForeignKey(
        AnomalyEvent,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )
    recommended_action = models.TextField()
    explanation_text = models.TextField()
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.anomaly_event}"
