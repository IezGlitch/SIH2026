from django.urls import path
from .views import (
    FloodAlertListCreate, FloodAlertDetail,
    HeatZoneListCreate, HeatZoneDetail,
    CropFieldListCreate, CropFieldDetail,
)

urlpatterns = [
    path('flood-alerts/', FloodAlertListCreate.as_view(), name='flood-alerts'),
    path('flood-alerts/<int:pk>/', FloodAlertDetail.as_view(), name='flood-alert-detail'),
    path('heat-zones/', HeatZoneListCreate.as_view(), name='heat-zones'),
    path('heat-zones/<int:pk>/', HeatZoneDetail.as_view(), name='heat-zone-detail'),
    path('crop-fields/', CropFieldListCreate.as_view(), name='crop-fields'),
    path('crop-fields/<int:pk>/', CropFieldDetail.as_view(), name='crop-field-detail'),
]
