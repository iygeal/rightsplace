from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Evidence
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import (
    ReporterRegistrationForm,
    LawyerRegistrationForm,
    NGORegistrationForm,
    LoginForm,
    AnonymousReportForm,
    AuthenticatedReportForm,
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


def anonymous_report(request):
    """
    Allows users to submit a report anonymously.
    Evidence upload supported.
    Contact information optional.
    """
    if request.method == "POST":
        form = AnonymousReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save()
            messages.success(
                request,
                "Your anonymous report has been submitted successfully. Thank you for speaking up."
            )
            return redirect("report_anonymous")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AnonymousReportForm()

    return render(request, "rightsplace/anonymous_report.html", {
        "form": form
    })


@login_required
@require_http_methods(["GET", "POST"])
def report_create(request):
    """
    Authenticated report creation view.

    Behavior:
    - If the client submits via normal POST (no JS), we keep the old behaviour:
      validate, on success redirect (PRG) to avoid resubmission; on failure render page.
    - If the client submits via AJAX (X-Requested-With: XMLHttpRequest), we return JSON:
      - success -> {success: True}
      - errors -> {success: False, errors: {field: [messages], ...}}
      This avoids a full page reload so selected files in the browser remain intact.
    """
    # Only users with role == "user" may create authenticated reports
    try:
        role = request.user.userprofile.role
    except Exception:
        role = None

    if role != "user":
        # For AJAX return JSON; for normal POST/GET show a message + redirect
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": {"__all__": ["Only regular reporter accounts may submit reports."]}}, status=403)
        messages.error(
            request, "Only regular reporter accounts may submit reports.")
        return redirect("index")

    if request.method == "POST":
        form = AuthenticatedReportForm(request.POST, request.FILES)
        # Ensure the form has access to files (it will use self.files.getlist in clean)
        if form.is_valid():
            # Save with reporter
            report = form.save(reporter=request.user.userprofile)

            # If AJAX: respond JSON (no page reload)
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Your report has been submitted successfully."})

            # Non-AJAX: use PRG to avoid form re-submission
            messages.success(
                request, "Your report has been submitted successfully.")
            return redirect(reverse("report_create"))

        # Form invalid
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Convert form.errors to a plain dict of lists for easy client processing
            errors = {}
            for k, v in form.errors.items():
                errors[k] = v.get_json_data(escape_html=True)
            # Also include non_field_errors if present
            non_field = form.non_field_errors()
            if non_field:
                errors["__all__"] = non_field.get_json_data(escape_html=True)
            return JsonResponse({"success": False, "errors": errors}, status=400)

        # Non-AJAX invalid → render page with errors (form will display server-side errors)
        return render(request, "rightsplace/report_create.html", {"form": form, "success": False})

    # GET request
    form = AuthenticatedReportForm()
    return render(request, "rightsplace/report_create.html", {"form": form, "success": False})
