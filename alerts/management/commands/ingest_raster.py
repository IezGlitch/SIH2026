from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from alerts.models import FloodAlert
from alerts.gis_utils import raster_to_alert_geometry


class Command(BaseCommand):
    help = 'Convert a raster prediction into a FloodAlert record'

    def add_arguments(self, parser):
        parser.add_argument('raster_path', type=str)
        parser.add_argument('--region', type=str, default='Test Region')
        parser.add_argument('--threshold', type=int, default=100)

    def handle(self, *args, **options):
        geom, confidence = raster_to_alert_geometry(
            options['raster_path'],
            threshold=options['threshold']
        )

        if geom is None:
            self.stdout.write(self.style.WARNING('No areas found above threshold — no alert created.'))
            return

        risk_level = 'high' if confidence > 0.5 else ('medium' if confidence > 0.2 else 'low')

        alert = FloodAlert.objects.create(
            region_name=options['region'],
            geom=GEOSGeometry(geom.wkt, srid=4326),
            risk_level=risk_level,
            confidence_score=confidence,
            reason=f"Raster analysis: {confidence:.0%} of area exceeded threshold ({options['threshold']}).",
            source='Raster ingestion (test)'
        )

        self.stdout.write(self.style.SUCCESS(f'Created alert: {alert}'))