from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('report/create/', views.report_create, name='report_create'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('report/anonymous/', views.anonymous_report, name='report_anonymous'),
    path("cases/assigned/", views.assigned_cases_dashboard, name="assigned_cases_dashboard"),
    path(
        "my-reports/",
        views.reporter_dashboard,
        name="reporter_dashboard"
    ),
    path(
        "partners/verified/",
        views.verified_partners,
        name="verified_partners"
    )
]
