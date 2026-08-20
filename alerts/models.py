from django.contrib.gis.db import models


class FloodAlert(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    region_name = models.CharField(max_length=255)
    geom = models.MultiPolygonField(srid=4326)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    confidence_score = models.FloatField()
    reason = models.TextField()
    source = models.CharField(max_length=100, default='Sentinel-1')
    detected_at = models.DateTimeField(auto_now_add=True)
    validated_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.region_name} — {self.risk_level} ({self.confidence_score:.0%})"


class HeatZone(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    region_name = models.CharField(max_length=255)
    geom = models.MultiPolygonField(srid=4326)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES)
    confidence_score = models.FloatField()
    reason = models.TextField()
    source = models.CharField(max_length=100, default='Landsat Thermal')
    detected_at = models.DateTimeField(auto_now_add=True)
    validated_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.region_name} — {self.risk_level} ({self.confidence_score:.0%})"


class CropField(models.Model):
    HEALTH_CHOICES = [('healthy', 'Healthy'), ('stressed', 'Stressed'), ('critical', 'Critical')]

    region_name = models.CharField(max_length=255)
    geom = models.MultiPolygonField(srid=4326)
    health_status = models.CharField(max_length=10, choices=HEALTH_CHOICES)
    confidence_score = models.FloatField()
    reason = models.TextField()
    source = models.CharField(max_length=100, default='Sentinel-2 NDVI')
    detected_at = models.DateTimeField(auto_now_add=True)
    validated_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.region_name} — {self.health_status} ({self.confidence_score:.0%})"
