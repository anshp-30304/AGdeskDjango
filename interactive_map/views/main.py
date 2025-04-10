from datetime import date, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from interactive_map.utils.core import map_api_endpoint, Colour
from main.utils.geojson import GeoJSONSerializer
from tms.models import Tenement


def tenement_serializer(queryset):
    """Standard serialization function for tenements"""
    if queryset.model != Tenement:
        raise ValueError(f"This queryset must be of type Tenement and not {queryset.model}")

    return GeoJSONSerializer().serialize(
        queryset,
        geometry_field="area_polygons",
        fields=[
            "permit_id", "permit_state", "permit_type", "permit_number", "permit_status", "date_lodged", "date_granted",
            "date_commenced", "date_expiry", "date_renewed", "ahr_name", "get_permit_status_display",
            "get_permit_type_display"
        ],
    )


def get_epm_granted_layer(request):
    queryset = Tenement.objects.filter(permit_type='EPM', permit_status='G').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_epm_application_layer(request):
    queryset = Tenement.objects.filter(permit_type='EPM', permit_status='A').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_epm_expiring_layer(request):
    current_date = date.today()
    six_months_from_now = current_date + timedelta(days=180)  # Assuming 6 months = 180 days

    queryset = Tenement.objects.filter(permit_type='EPM', permit_status='G', date_expiry__gte=current_date,
                                       date_expiry__lte=six_months_from_now).order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_mdl_granted_layer(request):
    queryset = Tenement.objects.filter(permit_type='MDL', permit_status='G').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_mdl_application_layer(request):
    queryset = Tenement.objects.filter(permit_type='MDL', permit_status='A').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_ml_granted_layer(request):
    queryset = Tenement.objects.filter(permit_type='ML', permit_status='G').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def get_ml_application_layer(request):
    queryset = Tenement.objects.filter(permit_type='ML', permit_status='A').order_by('-date_lodged')
    json = tenement_serializer(queryset)
    return JsonResponse(json, safe=False, status=200)


def home(request):
    return render(request, 'interactive_map/interactive_map.html')


def get_map_tree(request, **kwargs):
    return JsonResponse([
        {
            "id": "0",
            "label": "Tenements",
            "children": [
                {
                    "id": "0",
                    "label": "Exploration Permit for Minerals (EPM)",
                    "children": [
                        {
                            "id": "epm_granted",
                            "label": "Granted Permits",
                            "description": "All granted exploration permits (EPM) in Queensland",
                            "url": reverse("interactive_map:epm_granted"),
                            "style": {
                                "color": Colour.PINK.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_granted'],
                        },
                        {
                            "id": "epm_application",
                            "label": "Application Permits",
                            "description": "All application exploration permits (EPM) in Queensland",
                            "url": reverse("interactive_map:epm_application"),
                            "style": {
                                "color": Colour.CYAN.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_lodged'],
                        },
                        {
                            "id": "epm_expiring",
                            "label": "Approaching Expiry",
                            "description": "All granted exploration permits that are approaching expiry in Queensland",
                            "url": reverse("interactive_map:epm_approaching_expiry"),
                            "style": {
                                "color": Colour.MAGENTA.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_expiry'],
                        },
                    ]
                },
                {
                    "id": "2",
                    "label": "Mining Development License (MDL)",
                    "children": [
                        {
                            "id": "mdl_granted",
                            "label": "Granted Permits",
                            "description": "All granted mining development licenses (MDL) in Queensland",
                            "url": reverse("interactive_map:mdl_granted"),
                            "style": {
                                "color": Colour.RED.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_granted'],
                        },
                        {
                            "id": "mdl_application",
                            "label": "Application Permits",
                            "description": "All application mining development licenses (MDL) in Queensland",
                            "url": reverse("interactive_map:mdl_application"),
                            "style": {
                                "color": Colour.PERU.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_lodged'],
                        },
                    ]
                },
                {
                    "id": "3",
                    "label": "Mining Lease (ML)",
                    "children": [
                        {
                            "id": "ml_granted",
                            "label": "Granted Permits",
                            "description": "All granted mining leases (ML) in Queensland",
                            "url": reverse("interactive_map:ml_granted"),
                            "style": {
                                "color": Colour.BLUE.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_granted'],
                        },
                        {
                            "id": "ml_application",
                            "label": "Application Permits",
                            "description": "All application mining leases (ML) in Queensland",
                            "url": reverse("interactive_map:ml_application"),
                            "style": {
                                "color": Colour.GREEN.value,
                            },
                            "feature_name": 'permit_id',
                            "feature_table": ['permit_id', 'date_lodged'],
                        },
                    ]
                },
                # {
                #     "id": "4",
                #     "name": "Exploration Permit for Coal (EPC)",
                #     "action": "___"
                # }
            ]
        },
        {
            "id": "1",
            "label": "Hazards",
            "children": [
                {
                    "id": "hazard_fire",
                    "label": "Fire",
                    "description": "___",
                    # "url": reverse("interactive_map:epm_granted_layer"),
                    "icon": {
                        "iconUrl": 'https://i.imgur.com/S0b6BcO.png', # Path to your icon image
                        "iconSize": [32, 32],          # Size of the icon [width, height]
                        "iconAnchor": [16, 32],        # Point where the icon is anchored on the map [center horizontally, bottom vertically]
                        "popupAnchor": [0, -32]        # Where to open a popup in relation to the icon
                    },
                },
                {
                    "id": "hazard_flood",
                    "label": "Flood",
                    "description": "___",
                    # "url": reverse("interactive_map:epm_granted_layer"),
                    "icon": {
                        "iconUrl": 'https://i.imgur.com/OC3GeFx.png', # Path to your icon image
                        "iconSize": [32, 32],          # Size of the icon [width, height]
                        "iconAnchor": [16, 32],        # Point where the icon is anchored on the map [center horizontally, bottom vertically]
                        "popupAnchor": [0, -32]        # Where to open a popup in relation to the icon
                    },
                },
                {
                    "id": "hazard_other",
                    "label": "Other",
                    "description": "___",
                    # "url": reverse("interactive_map:epm_granted_layer"),
                    "icon": {
                        "iconUrl": 'https://i.imgur.com/w12naKC.png', # Path to your icon image
                        "iconSize": [32, 32],          # Size of the icon [width, height]
                        "iconAnchor": [16, 32],        # Point where the icon is anchored on the map [center horizontally, bottom vertically]
                        "popupAnchor": [0, -32]        # Where to open a popup in relation to the icon
                    },
                }
            ]
        }
    ], safe=False, status=200)


def get_tenement_layer(request, query_str):
    return JsonResponse([], safe=False, status=200)

    # """/map/api/tenements/"""
    # tenement_queryset = Tenement.objects.filter(permit_state='QLD')
    # moratorium_queryset = Moratorium.objects.select_related('tenement').all()
    #
    # isVisible = False
    # print('isAll: ', isAll)
    # if isAll == 'true':
    #     isVisible = True
    #
    # # Set up the resulting GeoJSON Tree
    # tenement_geojson = [
    #     {
    #         'display': '<span class="sp-display-label" style="font-size: 13px;">Tenements</span>',
    #         'value': 'tenement',
    #         'children': [
    #             {
    #                 'display': 'Exploration Permit for Minerals (EPM)',
    #                 'value': 'epm',
    #                 'children': [
    #                     epm_granted_date_tree(tenement_queryset, True),
    #                     epm_pending_date_tree(tenement_queryset, True),
    #                     epm_moratorium_date_tree(moratorium_queryset, isVisible)
    #                 ]
    #             },
    #             {
    #                 'display': 'Mining Development License (MDL)',
    #                 'value': 'mdl',
    #                 'children': [
    #                     tenement_permit_category_tree(tenement_queryset, 'MDL', 'G', Colour.MAGENTA, isVisible),
    #                     tenement_permit_category_tree(tenement_queryset, 'MDL', 'A', Colour.BLACK, isVisible),
    #                 ]
    #             },
    #             {
    #                 'display': 'Mining Lease (ML)',
    #                 'value': 'ml',
    #                 'children': [
    #                     tenement_permit_category_tree(tenement_queryset, 'ML', 'G', Colour.ORANGE, isVisible),
    #                     tenement_permit_category_tree(tenement_queryset, 'ML', 'A', Colour.BROWN, isVisible),
    #                 ]
    #             },
    #             {
    #                 'display': 'Exploration Permit for Coal (EPC)',
    #                 'value': 'epc',
    #                 'children': [
    #                     tenement_permit_category_tree(tenement_queryset, 'EPC', 'G', Colour.TEAL, isVisible),
    #                     tenement_permit_category_tree(tenement_queryset, 'EPC', 'A', Colour.MAROON, isVisible),
    #                 ]
    #             },
    #         ]
    #     }
    # ]
    #
    # return JsonResponse(tenement_geojson, safe=False, status=200)
