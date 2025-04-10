import json
from http import HTTPStatus

from django.contrib.gis.db.models import Union
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse

from interactive_map.utils.core import Colour, map_api_endpoint
from interactive_map.utils.parcel import project_parcel_type_tree
from interactive_map.utils.tenement import permit_type_status_date_tree, permit_type_status_tree, basic_permit_tree
from lms.models import Parcel, ProjectParcel
from main.utils.geojson import GeoJSONSerializer
from project.utils.decorators import project_perm_required
from tms.models import Tenement, Prospect
from interactive_map.utils.tenement import map_box_tree

@map_api_endpoint()
@project_perm_required('can_read')
def project_tenements_endpoint(request, project, slug, bounding_box, *args, **kwargs):
    """api/project/<str:slug>/tenements/<str:mode>/"""
    # Get the correct tree function, this determines how the tree is displayed, whether in date or status form

    queryset = Tenement.objects.filter(project_links__project__slug=slug).all()
    tree = map_box_tree(queryset)

    return JsonResponse(tree, safe=False, status=HTTPStatus.OK)


@map_api_endpoint()
@project_perm_required('can_read')
def project_prospects_endpoint(request, project, bounding_box, *args, **kwargs):
    queryset = Prospect.objects.filter(project=project)
    tree = [
        {
            'display': 'Prospects',
            'enabled': True,
            'data': GeoJSONSerializer().serialize(queryset, geometry_field="location", fields=["name"]),
            'value': 0,
        }
    ]

    return JsonResponse(tree, safe=False, status=HTTPStatus.OK)


@map_api_endpoint()
@project_perm_required('can_read')
def project_parcels_endpoint(request, project, slug, bounding_box, *args, **kwargs):


    project_geometry = project.tenements.geometry_union()

    queryset = Parcel.objects.filter(geometry__intersects=project_geometry)

    ProjectParcel.objects.all().delete()
    for p in queryset:
        pp = ProjectParcel.objects.create(parcel=p, project=project)

    project_parcels = ProjectParcel.objects.filter(parcel__in=queryset)

    print('parcels', len(queryset), len(project_parcels))

    tree = project_parcel_type_tree(queryset)

    return JsonResponse(tree, safe=False, status=HTTPStatus.OK)
