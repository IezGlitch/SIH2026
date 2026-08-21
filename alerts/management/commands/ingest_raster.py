from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from alerts.models import FloodAlert, HeatZone, CropField
from alerts.gis_utils import raster_to_alert_geometry


MODEL_MAP = {
    'flood': {'model': FloodAlert, 'status_field': 'risk_level', 'default_source': 'Sentinel-1'},
    'heat': {'model': HeatZone, 'status_field': 'risk_level', 'default_source': 'Landsat Thermal'},
    'crop': {'model': CropField, 'status_field': 'health_status', 'default_source': 'Sentinel-2 NDVI'},
}


def level_for(hazard_type, confidence):
    if hazard_type == 'crop':
        if confidence > 0.5:
            return 'critical'
        elif confidence > 0.2:
            return 'stressed'
        return 'healthy'
    else:
        if confidence > 0.5:
            return 'high'
        elif confidence > 0.2:
            return 'medium'
        return 'low'


class Command(BaseCommand):
    help = 'Convert a raster prediction into a FloodAlert, HeatZone, or CropField record'

    def add_arguments(self, parser):
        parser.add_argument('raster_path', type=str)
        parser.add_argument('--type', type=str, choices=['flood', 'heat', 'crop'], default='flood',
                             help='Which hazard model to create a record for')
        parser.add_argument('--region', type=str, default='Test Region')
        parser.add_argument('--threshold', type=int, default=100)
        parser.add_argument('--min-points', type=int, default=20)
        parser.add_argument('--simplify', type=float, default=0.01)

    def handle(self, *args, **options):
        hazard_type = options['type']
        config = MODEL_MAP[hazard_type]
        Model = config['model']
        status_field = config['status_field']

        geom, confidence = raster_to_alert_geometry(
            options['raster_path'],
            threshold=options['threshold'],
            simplify_tolerance=options['simplify'],
            min_points=options['min_points'],
        )

        if geom is None:
            self.stdout.write(self.style.WARNING('No areas found above threshold — no record created.'))
            return

        level = level_for(hazard_type, confidence)

        record = Model.objects.create(
            region_name=options['region'],
            geom=GEOSGeometry(geom.wkt, srid=4326),
            confidence_score=confidence,
            reason=f"Raster analysis: {confidence:.0%} of area exceeded threshold ({options['threshold']}).",
            source=config['default_source'],
            **{status_field: level}
        )

        self.stdout.write(self.style.SUCCESS(f'Created {hazard_type} record: {record}'))
