from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    """
    Landing page for RightsPlace.

    Displays:
    - Reporting buttons
    - Basic explanation of platform
    - Quick links to anonymous report and registration
    """
    return render(request, "rightsplace/index.html")
