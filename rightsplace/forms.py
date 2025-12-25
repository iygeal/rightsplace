"""
Forms used throughout the RightsPlace platform.

This module contains the following forms:
 - ReporterRegistrationForm: registration for regular reporters
 - AnonymousReportForm: form for anonymous users to submit reports
 - LawyerRegistrationForm: registration for lawyers
 - NGORegistrationForm: registration for NGOs
  - LoginForm: login form for users
  - AuthenticatedReportForm: form for authenticated users to submit reports
    Each form includes necessary fields, validation logic, and save methods
    to simplify form processing and to handle the creation of associated models.
  - AnonymousReportForm: form for anonymous users to submit reports
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Report, Evidence
from multiupload.fields import MultiFileField, MultiUploadMetaInput


# -------------------------------------------------------------------------
# Bootstrap Widgets
# -------------------------------------------------------------------------
TEXT_INPUT = forms.TextInput(attrs={"class": "form-control"})
EMAIL_INPUT = forms.EmailInput(attrs={"class": "form-control"})
PASSWORD_INPUT = forms.PasswordInput(attrs={"class": "form-control"})
TEXTAREA = forms.Textarea(attrs={"class": "form-control", "rows": 4})
SELECT = forms.Select(attrs={"class": "form-select"})
FILE_INPUT_MULTI = MultiUploadMetaInput(attrs={
    "class": "form-control"
    })
CHECKBOX = forms.CheckboxInput(attrs={"class": "form-check-input"})



class CustomErrors(forms.ModelForm):
    """Custom Error Messages for Required Fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if field.required:
                field.error_messages.setdefault(
                    "required",
                    f"{field.label} is required."
                )

    def clean_username(self):
        if "username" not in self.cleaned_data:
            return None

        username = self.cleaned_data.get("username")

        qs = User.objects.filter(username=username)

        # Allow updates without false positives
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This username is already taken.")

        return username

    def clean_email(self):
        if "email" not in self.cleaned_data:
            return None

        email = self.cleaned_data.get("email")

        qs = User.objects.filter(email=email)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "This email address is already registered.")

        return email
# -------------------------------------------------------------------------
# Reporter Registration Form
# -------------------------------------------------------------------------
class ReporterRegistrationForm(CustomErrors):
    """
    Registration for regular reporters (non-lawyers, non-NGO).

    Behavior:
    - Users may choose to remain anonymous.
    - If wants_contact=True → require name + email + phone.
    - If wants_contact=False → these fields may remain blank.
    """

    username = forms.CharField(widget=TEXT_INPUT)
    password = forms.CharField(widget=PASSWORD_INPUT)

    first_name = forms.CharField(required=True, widget=TEXT_INPUT)
    last_name = forms.CharField(required=True, widget=TEXT_INPUT)
    email = forms.EmailField(required=True, widget=EMAIL_INPUT)
    phone_number = forms.CharField(required=False, widget=TEXT_INPUT)

    wants_contact = forms.BooleanField(
        required=False,
        widget=CHECKBOX,
        help_text="Check this if you want us to contact you for follow-up."
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
class LawyerRegistrationForm(CustomErrors):
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
class NGORegistrationForm(CustomErrors):
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


class AuthenticatedReportForm(CustomErrors):
    """
    Form for authenticated users to submit reports.

    Validates uploaded evidence files:
    - Allowed types
    - Max size 100 MB
    """
    evidence_files = MultiFileField(
        min_num=0,
        max_num=20,
        max_file_size=100 * 1024 * 1024,   # 100MB per file
        required=False,
        widget=FILE_INPUT_MULTI,
        help_text="Upload supporting evidence files (max 100MB each)."
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
        """
        Validates uploaded files:
        - Allowed types
        - Max size 100 MB
        """
        files = self.cleaned_data.get("evidence_files") or []
        cleaned = []
        errors = []

        allowed_prefixes = ("image/", "video/", "audio/")
        allowed_exact = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/plain",
        }

        for f in files:
            ctype = getattr(f, "content_type", "")
            size = getattr(f, "size", 0)

            if size > 100 * 1024 * 1024:
                errors.append(f'"{f.name}" exceeds 100 MB.')
            elif not (any(ctype.startswith(p) for p in allowed_prefixes) or ctype in allowed_exact):
                errors.append(f'"{f.name}" has unsupported type: "{ctype}".')
            else:
                cleaned.append(f)

        if errors:
            raise ValidationError(errors)

        return cleaned

    def save(self, commit=True, reporter=None):
        """
        Saves the report and associated Evidence files.

        :param commit: whether to save the report and associated Evidence files
        :param reporter: the UserProfile instance of the reporter
        """
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


class AnonymousReportForm(CustomErrors):
    """
    Form for anonymous users to submit reports.

    Uses django-multiupload for evidence files.
    """

    evidence_files = MultiFileField(
        min_num=0,
        max_num=20,
        max_file_size=100 * 1024 * 1024,  # 100MB
        required=False,
        widget=FILE_INPUT_MULTI,
        help_text="Upload supporting evidence files (max 100MB each)."
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
        files = self.cleaned_data.get("evidence_files") or []
        cleaned = []
        errors = []

        allowed_prefixes = ("image/", "video/", "audio/")
        allowed_exact = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/plain",
        }

        for f in files:
            ctype = getattr(f, "content_type", "")
            size = getattr(f, "size", 0)

            if size > 100 * 1024 * 1024:
                errors.append(f'"{f.name}" exceeds 100 MB.')
            elif not (
                any(ctype.startswith(p) for p in allowed_prefixes)
                or ctype in allowed_exact
            ):
                errors.append(f'"{f.name}" has unsupported type: "{ctype}".')
            else:
                cleaned.append(f)

        if errors:
            raise ValidationError(errors)

        return cleaned

    def save(self, commit=True):
        """
        Saves anonymous report (reporter=None)
        """
        report = super().save(commit=False)
        report.reporter = None

        if commit:
            report.save()

        for f in self.cleaned_data.get("evidence_files", []):
            Evidence.objects.create(report=report, file=f)

        return report
