from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import FloodAlert, HeatZone, CropField


class FloodAlertSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = FloodAlert
        geo_field = 'geom'
        fields = ['id', 'region_name', 'risk_level', 'confidence_score', 'reason', 'source', 'detected_at', 'validated_status']


class HeatZoneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HeatZone
        geo_field = 'geom'
        fields = ['id', 'region_name', 'risk_level', 'confidence_score', 'reason', 'source', 'detected_at', 'validated_status']


class CropFieldSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CropField
        geo_field = 'geom'
        fields = ['id', 'region_name', 'health_status', 'confidence_score', 'reason', 'source', 'detected_at', 'validated_status']
