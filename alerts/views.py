from rest_framework import generics
from .models import FloodAlert, HeatZone, CropField
from .serializers import FloodAlertSerializer, HeatZoneSerializer, CropFieldSerializer


class FloodAlertListCreate(generics.ListCreateAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer


class FloodAlertDetail(generics.RetrieveUpdateAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer


class HeatZoneListCreate(generics.ListCreateAPIView):
    queryset = HeatZone.objects.all()
    serializer_class = HeatZoneSerializer


class HeatZoneDetail(generics.RetrieveUpdateAPIView):
    queryset = HeatZone.objects.all()
    serializer_class = HeatZoneSerializer


class CropFieldListCreate(generics.ListCreateAPIView):
    queryset = CropField.objects.all()
    serializer_class = CropFieldSerializer


class CropFieldDetail(generics.RetrieveUpdateAPIView):
    queryset = CropField.objects.all()
    serializer_class = CropFieldSerializer
