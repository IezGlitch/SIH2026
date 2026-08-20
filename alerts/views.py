from rest_framework import generics
from .models import FloodAlert
from .serializers import FloodAlertSerializer

class FloodAlertListCreate(generics.ListCreateAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer

class FloodAlertDetail(generics.RetrieveUpdateAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer