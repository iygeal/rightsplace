from django.urls import path
from . import views
from django.http import HttpResponse


def placeholder(request):
    return HttpResponse("This page is under construction.")


urlpatterns = [
    path('', views.index, name='index'),

    # Temporary placeholders to stop template errors
    path('report/create/', placeholder, name='report_create'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('report/anonymous/', views.anonymous_report, name='report_anonymous'),
]
