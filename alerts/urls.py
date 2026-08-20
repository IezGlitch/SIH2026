from django.urls import path
from .views import FloodAlertListCreate, FloodAlertDetail

urlpatterns = [
    path('flood-alerts/', FloodAlertListCreate.as_view(), name='flood-alerts'),
    path('flood-alerts/<int:pk>/', FloodAlertDetail.as_view(), name='flood-alert-detail'),
]