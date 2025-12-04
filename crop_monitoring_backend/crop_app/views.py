from rest_framework import generics, permissions
from .models import SensorReading, AnomalyEvent, AgentRecommendation
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer
)

# ===============================
# CREATE (POST) Sensor Reading
# ===============================
class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]   # 🔐 JWT obligatoire

# ===============================
# LIST (GET) Sensor Readings
# ===============================
class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        plot_id = self.request.query_params.get("plot")
        if not plot_id:
            return SensorReading.objects.none()
        return SensorReading.objects.filter(plot_id=plot_id).order_by("-timestamp")

# ===============================
# LIST (GET) Anomaly Events
# ===============================
class AnomalyListView(generics.ListAPIView):
    queryset = AnomalyEvent.objects.all().order_by("-timestamp")
    serializer_class = AnomalyEventSerializer
    permission_classes = [permissions.IsAuthenticated]

# ===============================
# LIST (GET) Agent Recommendations
# ===============================
class RecommendationListView(generics.ListAPIView):
    queryset = AgentRecommendation.objects.all().order_by("-timestamp")  # <-- corrigé !
    serializer_class = AgentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
