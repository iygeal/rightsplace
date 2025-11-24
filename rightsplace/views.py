from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.urls import reverse
from .forms import (
    ReporterRegistrationForm,
    LawyerRegistrationForm,
    NGORegistrationForm,
    LoginForm,
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
    Logs the user out and redirects to index with a message.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("index")