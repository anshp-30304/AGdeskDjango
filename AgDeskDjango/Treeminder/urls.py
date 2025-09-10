from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('header/', views.dashboard_header, name='dashboard_header'),
    path('stats/', views.stats_cards, name='stats_cards'),
    path('tree-status/', views.tree_status, name='tree_status'),
    path('alerts/', views.recent_alerts, name='recent_alerts'),
]
