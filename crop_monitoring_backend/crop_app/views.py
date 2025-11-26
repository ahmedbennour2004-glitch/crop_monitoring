from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from .models import SensorReading, AnomalyEvent, AgentRecommendation
from .serializers import SensorReadingSerializer, AnomalyEventSerializer, AgentRecommendationSerializer


class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer


class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        plot_id = self.request.query_params.get("plot")
        return SensorReading.objects.filter(plot_id=plot_id)


class AnomalyListView(generics.ListAPIView):
    queryset = AnomalyEvent.objects.all()
    serializer_class = AnomalyEventSerializer


class RecommendationListView(generics.ListAPIView):
    queryset = AgentRecommendation.objects.all()
    serializer_class = AgentRecommendationSerializer



