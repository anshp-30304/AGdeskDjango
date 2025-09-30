from django.shortcuts import render,redirect

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

def mapView(request):
    return render(request,"Treeminder/navigation_bar/navigation.html")

def inventory(request):
    return render(request, "Treeminder/navigation_bar/navigation.html")

def document(request):
    return render(request,"Treeminder/docTracker.html")

def viewAlert(request):
    # Redirect to the URL by path or by name
    return render(request,'Treeminder/viewAlert.html')

def prediction_dashboard_page(request):
    return render(request, "Treeminder/prediction_dashboard.html")