from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Case, Report, UserProfile
from .forms import (
    ReporterRegistrationForm,
    LawyerRegistrationForm,
    NGORegistrationForm,
    LoginForm,
    AuthenticatedReportForm,
    AnonymousReportForm,
)


def index(request):
    """
    Landing page for RightsPlace.

    Displays:
    - Reporting buttons
    - Basic explanation of platform
    - Quick links to anonymous report and registration
    """
    return render(request, "rightsplace/index.html")


def register(request):
    """
    Unified registration handler for:
        - Regular Users (ReporterRegistrationForm)
        - Lawyers (LawyerRegistrationForm)
        - NGO Representatives (NGORegistrationForm)

    Workflow:
    - GET request → show registration page with no form selected.
    - JavaScript on the template reveals form when a role button is clicked.
    - POST request → detect which form was submitted via `role` hidden field.
    - Validate → create user + profile → auto-login → redirect to index.

    Returns:
        HttpResponse: Rendered registration template or redirect.
    """

    # Initialize empty forms for the template
    reporter_form = ReporterRegistrationForm()
    lawyer_form = LawyerRegistrationForm()
    ngo_form = NGORegistrationForm()

    if request.method == "POST":
        role = request.POST.get("role")  # Determine which form was submitted

        # ------------------------------------------------------------------
        # Handle Reporter Registration
        # ------------------------------------------------------------------
        if role == "user":
            reporter_form = ReporterRegistrationForm(request.POST)
            if reporter_form.is_valid():
                profile = reporter_form.save()
                login(request, profile.user)
                messages.success(request, "Registration successful. Welcome!")
                return redirect("index")

            messages.error(request, "Please correct the errors below.")

        # ------------------------------------------------------------------
        # Handle Lawyer Registration
        # ------------------------------------------------------------------
        elif role == "lawyer":
            lawyer_form = LawyerRegistrationForm(request.POST)
            if lawyer_form.is_valid():
                profile = lawyer_form.save()
                login(request, profile.user)
                messages.success(
                    request, "Account created. Pending verification.")
                return redirect("index")

            messages.error(request, "Please correct the errors below.")

        # ------------------------------------------------------------------
        # Handle NGO Registration
        # ------------------------------------------------------------------
        elif role == "ngo":
            ngo_form = NGORegistrationForm(request.POST)
            if ngo_form.is_valid():
                profile = ngo_form.save()
                login(request, profile.user)
                messages.success(
                    request, "NGO account created. Pending admin verification."
                )
                return redirect("index")

            messages.error(request, "Please correct the errors below.")

        else:
            messages.error(request, "Invalid form submission.")

    # GET request → simply render the page with all forms hidden initially
    return render(
        request,
        "rightsplace/register.html",
        {
            "reporter_form": reporter_form,
            "lawyer_form": lawyer_form,
            "ngo_form": ngo_form,
        },
    )


def login_view(request):
    """
    Handles user login using the custom LoginForm.
    - Accepts username OR email
    - On success → redirects to index
    - On failure → re-renders with error message
    """

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("index")

        else:
            messages.error(request, "Invalid login details.")
    else:
        form = LoginForm()

    context = {
        "form": form,
    }

    return render(request, "rightsplace/login.html", context)



# ------------------------------------------
# LOGOUT VIEW
# ------------------------------------------
def logout_view(request):
    """
    Logs the user out and redirects to index.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("index")


@require_http_methods(["GET", "POST"])
def anonymous_report(request):
    """
    Anonymous report submission.

    - GET  → render form
    - POST → JSON response
    """

    if request.method == "POST":
        form = AnonymousReportForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            report = form.save()

            return JsonResponse(
                {
                    "success": True
                },
                status=200
            )

        # Form validation errors
        errors = {
            field: list(errs)
            for field, errs in form.errors.items()
        }

        return JsonResponse(
            {
                "success": False,
                "errors": errors
            },
            status=400
        )


    # GET request
    form = AnonymousReportForm()
    return render(
        request,
        "rightsplace/anonymous_report.html",
        {"form": form}
    )


@login_required
@require_http_methods(["GET", "POST"])
def report_create(request):
    """
    Authenticated report submission.

    - GET  → render form
    - POST → JSON response
    """
    profile = request.user.userprofile

    if profile.role != "user":
        return JsonResponse(
            {
                "success": False,
                "errors": {
                    "role": ["Only regular users can submit reports."]
                }
            },
            status=403
        )

    if request.method == "POST":

        form = AuthenticatedReportForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save(
                commit=True,
                reporter=request.user.userprofile
            )

            return JsonResponse(
                {"success": True},
                status=200
            )

        errors = {
            field: list(errs)
            for field, errs in form.errors.items()
        }

        return JsonResponse(
            {
                "success": False,
                "errors": errors
            },
            status=400
        )

    # GET
    form = AuthenticatedReportForm()
    return render(
        request,
        "rightsplace/report_create.html",
        {"form": form}
    )


@login_required
def assigned_cases_dashboard(request):
    """
    Shared dashboard for Lawyers and NGOs.

    - Lawyers see cases assigned to them
    - NGOs see cases assigned to them
    - Read-only access
    """
    profile = request.user.userprofile

    if profile.role not in ("lawyer", "ngo"):
        return HttpResponseForbidden(
            "You are not authorized to view this page."
        )

    if profile.role == "lawyer":
        cases = Case.objects.filter(
            assigned_lawyer=profile
        ).select_related("report", "report__reporter__user").prefetch_related(
            "report__evidences"
        )

    else:  # NGO
        cases = Case.objects.filter(
            assigned_ngo=profile
        ).select_related("report", "report__reporter__user").prefetch_related(
            "report__evidences"
        )

    return render(
        request,
        "rightsplace/assigned_cases_dashboard.html",
        {
            "cases": cases,
            "profile": profile,
        }
    )


@login_required
def reporter_dashboard(request):
    """
    Dashboard for reporters to track their submitted reports.
    """
    profile = request.user.userprofile

    if profile.role != "user":
        return HttpResponseForbidden(
            "Only reporters can access this page."
        )

    reports = (
        Report.objects
        .filter(reporter=profile)
        .select_related("case")
        .order_by("-created_at")
    )

    return render(
        request,
        "rightsplace/reporter_dashboard.html",
        {
            "reports": reports
        }
    )


@login_required
def verified_partners(request):
    """
    Displays verified lawyers and NGOs.

    - Accessible only to authenticated users
    """

    verified_lawyers = UserProfile.objects.filter(
        role="lawyer",
        is_verified=True
    ).order_by("user__first_name", "user__last_name")

    verified_ngos = UserProfile.objects.filter(
        role="ngo",
        is_verified=True
    ).order_by("organization_name")

    return render(
        request,
        "rightsplace/verified_partners.html",
        {
            "verified_lawyers": verified_lawyers,
            "verified_ngos": verified_ngos,
        }
    )


@login_required
def reporter_cases(request):
    """
    Dashboard for reporters to track their submitted reports
    and see whether they have progressed into cases.
    """
    profile = request.user.userprofile

    if profile.role != "user":
        return HttpResponseForbidden(
            "Only reporters can view this page."
        )

    reports = (
        Report.objects
        .filter(reporter=profile,
               case__isnull=False)
        .select_related("case")
        .order_by("-updated_at")
    )

    return render(
        request,
        "rightsplace/reporter_cases.html",
        {
            "reports": reports,
        }
    )
