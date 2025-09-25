from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='treeminder_dashboard'),
    path('header/', views.dashboard_header, name='dashboard_header'),
    path('stats/', views.stats_cards, name='stats_cards'),
    path('tree-status/', views.tree_status, name='tree_status'),
    path('alerts/', views.recent_alerts, name='recent_alerts'),
    path('viewAlert/', views.viewAlert, name='viewAlert'),

    path('nav/', views.navigation, name='navigation'),
    path('mapView/', views.mapView, name='mapView'),
    path('inventory/', views.inventory, name='inventory'),
    path('document/', views.document, name='document'),

]
