from django.urls import path
from .views import (
    SensorReadingCreateView,
    SensorReadingListView,
    AnomalyListView,
    RecommendationListView,
)

urlpatterns = [
    path('sensor-readings/', SensorReadingCreateView.as_view(), name='sensor-reading-create'),
    path('sensor-readings/list/', SensorReadingListView.as_view(), name='sensor-reading-list'),

    path('anomalies/', AnomalyListView.as_view(), name='anomaly-list'),

    path('recommendations/', RecommendationListView.as_view(), name='recommendation-list'),
]
