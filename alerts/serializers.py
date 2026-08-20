from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import FloodAlert

class FloodAlertSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = FloodAlert
        geo_field = 'geom'
        fields = ['id', 'region_name', 'risk_level', 'confidence_score', 'reason', 'source', 'detected_at', 'validated_status']