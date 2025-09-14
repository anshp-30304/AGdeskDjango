from django.shortcuts import render

def dashboard(request):
    return render(request, "Treeminder/index.html")

def dashboard_header(request):
    return render(request, "Treeminder/partials/dashboard_header.html")

def stats_cards(request):
    return render(request, "Treeminder/partials/stats_cards.html")

def tree_status(request):
    return render(request, "Treeminder/partials/tree_status.html")

def recent_alerts(request):
    return render(request, "Treeminder/partials/recent_alerts.html")

def navigation(request):
    return render(request, "Treeminder/navigation_bar/navigation.html")
