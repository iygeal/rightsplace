"""
Forms for the RightsPlace platform.

This file contains:
 - LoginForm
 - ReporterRegistrationForm
 - AnonymousReportForm
 - LawyerRegistrationForm
 - NGORegistrationForm
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Report, Evidence


class ClearableMultipleFileInput(forms.ClearableFileInput):
    """
    A custom form field that allows multiple files to be selected.
    """
    allow_multiple_selected = True


# -------------------------------------------------------------------------
# Login Form
# -------------------------------------------------------------------------
class LoginForm(forms.Form):
    """
    Custom login form allowing authentication via username or email.
    """
    identifier = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter username or email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )

    def clean(self):
        """
        Attempt authentication using:
            1. identifier as username
            2. identifier as email → translated to username
        """
        cleaned = super().clean()
        identifier = cleaned.get("identifier")
        password = cleaned.get("password")

        if identifier and password:
            # Try logging in with username
            user = authenticate(username=identifier, password=password)

            if user is None:
                # Try interpreting identifier as email
                try:
                    user_obj = User.objects.get(email=identifier)
                    user = authenticate(
                        username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is None:
                raise ValidationError("Invalid username/email or password.")

            cleaned["user"] = user

        return cleaned


# -------------------------------------------------------------------------
# Bootstrap Widgets
# -------------------------------------------------------------------------
TEXT_INPUT = forms.TextInput(attrs={"class": "form-control"})
EMAIL_INPUT = forms.EmailInput(attrs={"class": "form-control"})
PASSWORD_INPUT = forms.PasswordInput(attrs={"class": "form-control"})
TEXTAREA = forms.Textarea(attrs={"class": "form-control", "rows": 4})
SELECT = forms.Select(attrs={"class": "form-select"})
FILE_INPUT_MULTI = ClearableMultipleFileInput(attrs={
    "class": "form-control",
    "multiple": True
    })
CHECKBOX = forms.CheckboxInput(attrs={"class": "form-check-input"})


# -------------------------------------------------------------------------
# Reporter Registration Form
# -------------------------------------------------------------------------
class ReporterRegistrationForm(forms.ModelForm):
    """
    Registration for regular reporters (non-lawyers, non-NGO).

    Behavior:
    - Users may choose to remain anonymous.
    - If wants_contact=True → require name + email + phone.
    - If wants_contact=False → these fields may remain blank.
    """

    username = forms.CharField(widget=TEXT_INPUT)
    password = forms.CharField(widget=PASSWORD_INPUT)

    first_name = forms.CharField(required=False, widget=TEXT_INPUT)
    last_name = forms.CharField(required=False, widget=TEXT_INPUT)
    email = forms.EmailField(required=False, widget=EMAIL_INPUT)
    phone_number = forms.CharField(required=False, widget=TEXT_INPUT)

    wants_contact = forms.BooleanField(
        required=False,
        widget=CHECKBOX,
        help_text="Check if you want us to contact you for follow-up."
    )

    class Meta:
        model = UserProfile
        fields = ["role", "email", "phone_number", "wants_contact"]
        widgets = {
            "role": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form by setting the role to "user".

        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form
        """
        super().__init__(*args, **kwargs)
        self.fields["role"].initial = "user"

    def clean(self):
        """
        Enforces role-based validation rules.

        If wants_contact=True, require first name, last name, email, and phone number.
        """
        cleaned = super().clean()
        wants_contact = cleaned.get("wants_contact")

        if wants_contact:
            required_fields = ["first_name",
                               "last_name", "email", "phone_number"]
            for f in required_fields:
                if not self.cleaned_data.get(f):
                    raise ValidationError(
                        f"{f.replace('_', ' ').title()} is required.")

        return cleaned

    def save(self, commit=True):
        """
        Creates:
        - Django User object
        - UserProfile with role='user'
        """
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
            email=self.cleaned_data.get("email", "")
        )

        profile = super().save(commit=False)
        profile.user = user
        profile.role = "user"
        profile.email = self.cleaned_data.get("email")
        profile.phone_number = self.cleaned_data.get("phone_number")

        if commit:
            profile.save()

        return profile



# -------------------------------------------------------------------------
# Lawyer Registration Form
# -------------------------------------------------------------------------
class LawyerRegistrationForm(forms.ModelForm):
    """
    Registration for lawyers.

    Required:
    - First name, last name
    - Email
    - Phone number
    - Enrolment number

    Optional:
    - Specialization
    - City / State
    """

    username = forms.CharField(widget=TEXT_INPUT)
    password = forms.CharField(widget=PASSWORD_INPUT)

    first_name = forms.CharField(widget=TEXT_INPUT)
    last_name = forms.CharField(widget=TEXT_INPUT)
    email = forms.EmailField(widget=EMAIL_INPUT)
    phone_number = forms.CharField(widget=TEXT_INPUT)

    enrolment_number = forms.CharField(widget=TEXT_INPUT)
    specialization = forms.CharField(required=False, widget=TEXT_INPUT)
    city = forms.CharField(required=False, widget=TEXT_INPUT)
    state = forms.CharField(required=False, widget=TEXT_INPUT)

    class Meta:
        model = UserProfile
        fields = [
            "role", "email", "phone_number",
            "enrolment_number", "specialization",
            "city", "state", "is_verified"
        ]
        widgets = {
            "role": forms.HiddenInput(),
            "is_verified": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form by setting the role to "lawyer" and
        is_verified to False.

        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form
        """
        super().__init__(*args, **kwargs)
        self.fields["role"].initial = "lawyer"
        self.fields["is_verified"].initial = False

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
        )

        profile = super().save(commit=False)
        profile.user = user
        profile.role = "lawyer"

        if commit:
            profile.save()

        return profile


# -------------------------------------------------------------------------
# NGO Registration Form
# -------------------------------------------------------------------------
class NGORegistrationForm(forms.ModelForm):
    """
    Registration for NGOs.

    Required:
    - Contact person's first & last names
    - Organization name
    - RC number
    - Email & phone

    Optional:
    - City
    - State
    """

    username = forms.CharField(widget=TEXT_INPUT)
    password = forms.CharField(widget=PASSWORD_INPUT)

    first_name = forms.CharField(label="Contact First Name", widget=TEXT_INPUT)
    last_name = forms.CharField(label="Contact Last Name", widget=TEXT_INPUT)

    email = forms.EmailField(widget=EMAIL_INPUT)
    phone_number = forms.CharField(widget=TEXT_INPUT)

    organization_name = forms.CharField(widget=TEXT_INPUT)
    rc_number = forms.CharField(label="RC Number", widget=TEXT_INPUT)

    city = forms.CharField(required=False, widget=TEXT_INPUT)
    state = forms.CharField(required=False, widget=TEXT_INPUT)

    class Meta:
        model = UserProfile
        fields = [
            "role", "organization_name", "rc_number",
            "email", "phone_number", "city", "state", "is_verified"
        ]
        widgets = {
            "role": forms.HiddenInput(),
            "is_verified": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].initial = "ngo"
        self.fields["is_verified"].initial = False

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
        )

        profile = super().save(commit=False)
        profile.user = user
        profile.role = "ngo"

        if commit:
            profile.save()

        return profile


class AuthenticatedReportForm(forms.ModelForm):
    """
    Form used by logged-in users to submit a report.
    Allows uploading multiple evidence files.
    """

    evidence_files = forms.FileField(
        required=False,
        widget=ClearableMultipleFileInput(
            attrs={
                "class": "form-control",
                "multiple": True,
                "id": "djangoFileInput",
            }
        ),
        help_text="Upload supporting evidence files.",
    )

    class Meta:
        model = Report
        fields = ["title", "description", "category", "incident_location"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "incident_location": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_evidence_files(self):
        """
        Validate uploaded files:
        - each file ≤ 25 MB
        - MIME type supported
        Returns a list of uploaded files.
        """
        files = self.files.getlist("evidence_files")
        cleaned = []

        allowed_prefixes = ("image/", "video/", "audio/")
        allowed_exact = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        }
        max_bytes = 25 * 1024 * 1024

        errors = []

        for f in files:
            if f.size > max_bytes:
                errors.append(f'"{f.name}" exceeds 25 MB.')
                continue

            ctype = getattr(f, "content_type", "")
            if not ctype:
                errors.append(f'Could not determine content type: "{f.name}".')
                continue

            if not (any(ctype.startswith(p) for p in allowed_prefixes) or ctype in allowed_exact):
                errors.append(f'"{f.name}" has unsupported type: "{ctype}".')

            cleaned.append(f)

        if errors:
            raise ValidationError(errors)

        return cleaned

    def save(self, commit=True, reporter=None):
        if reporter is None:
            raise ValueError(
                "AuthenticatedReportForm requires reporter=request.user.userprofile")

        report = super().save(commit=False)
        report.reporter = reporter

        if commit:
            report.save()

        for f in self.cleaned_data.get("evidence_files", []):
            Evidence.objects.create(report=report, file=f)

        return report


# -----------------------------
# AnonymousReportForm changes
# -----------------------------
class AnonymousReportForm(forms.ModelForm):
    contact_email = forms.EmailField(required=False, widget=EMAIL_INPUT)
    contact_phone = forms.CharField(required=False, widget=TEXT_INPUT)


    evidence_files = forms.FileField(
        required=False,
        widget=ClearableMultipleFileInput(attrs={
            "class": "form-control",
            "multiple": True,
            "id": "djangoFileInput",
        }),
        help_text="Upload supporting evidence files.",
    )


    class Meta:
        model = Report
        fields = ["title", "description", "category", "incident_location"]
        widgets = {
            "title": TEXT_INPUT,
            "description": TEXTAREA,
            "category": SELECT,
            "incident_location": TEXT_INPUT,
        }

    def clean_evidence_files(self):
        # reuse same validation logic as authenticated form
        files = self.files.getlist("evidence_files")
        # We can reuse code by instantiating an AuthenticatedReportForm-like validation,
        # but to keep it simple we replicate the same checks here.

        allowed_prefixes = ("image/", "video/", "audio/")
        allowed_exact = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        }
        max_bytes = 25 * 1024 * 1024

        errors = []
        cleaned = []
        for f in files:
            if f.size > max_bytes:
                errors.append(
                    f'"{f.name}" is too large ({f.size} bytes). Max 25 MB.')
                continue
            ctype = getattr(f, "content_type", "")
            if not (any(ctype.startswith(p) for p in allowed_prefixes) or ctype in allowed_exact):
                errors.append(f'"{f.name}" has unsupported type "{ctype}".')
            cleaned.append(f)

        if errors:
            raise ValidationError(errors)
        return cleaned

    def save(self, commit=True):
        report = super().save(commit)

        for f in self.cleaned_data.get("evidence_files", []):
            Evidence.objects.create(report=report, file=f)

        return report
