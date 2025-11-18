from django.db import models
from django.contrib.auth.models import User

# =============================================================================
# RightsPlace Models
# =============================================================================
# This file defines the core data layer for RightsPlace.
# It contains:
#   - UserProfile: Extends Django's User for Lawyers, NGOs, and Reporters
#   - Report: A submitted human rights violation report
#   - Evidence: Files attached to a Report
#   - Case: Follow-up handling of a Report by legal/NGO actors
# =============================================================================


class UserProfile(models.Model):
    """
    Extends Django's built-in User model with role-based information.

    Roles:
        - lawyer: Verified legal practitioners with enrolment numbers
        - ngo: NGO representatives who handle or monitor cases
        - user: Regular reporters (anonymous or registered)

    The model stores additional professional and contact details depending on role.
    Validation rules enforced in `clean()` ensure required fields are present.
    """

    ROLE_CHOICES = [
        ('lawyer', 'Lawyer'),
        ('ngo', 'NGO Representative'),
        ('user', 'Regular User'),
    ]

    # Link to Django's User
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Role classification
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='user')

    # Core contact & organizational details
    organization_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Required for NGOs."
    )

    rc_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Required for NGOs."
    )
    phone_number = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Contact phone number (required for NGOs and Lawyers)."
    )
    email = models.EmailField(
        blank=True, null=True,
        help_text="Contact email (required for NGOs and Lawyers)."
    )
    location = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="General location or address."
    )

    # Lawyer-specific attributes
    enrolment_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Lawyer's official enrolment number (NBA verified)."
    )
    specialization = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Optional field: area of legal specialty."
    )
    state = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="State of residence or operation."
    )
    city = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="City of residence or operation."
    )

    # User preference
    wants_contact = models.BooleanField(
        default=False,
        help_text="Whether the reporter wishes to be contacted."
    )

    # Admin verification (Lawyers + NGOs)
    is_verified = models.BooleanField(
        default=False,
        help_text="True after admin verification for Lawyers/NGOs."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------------------------------------------------------------
    # Model Validation
    # -------------------------------------------------------------------------
    def clean(self):
        """
        Enforce role-based validation rules.
        - Only Lawyers and NGOs can be verified.
        - NGOs must provide organization name and rc number.
        - Lawyers must provide enrolment number, phone, and email.
        """
        from django.core.exceptions import ValidationError

        # Prevent regular users from being marked verified
        if self.role == 'user' and self.is_verified:
            raise ValidationError("Only NGOs and Lawyers can be verified.")

        # NGO role must include an organization name
        if self.role == 'ngo' and not self.organization_name:
            raise ValidationError("NGOs must provide an organization name.")

        # NGO role must include an RC number
        if self.role == 'ngo' and not self.rc_number:
            raise ValidationError("NGOs must provide an RC number.")

        # Lawyers must have professional credentials + contact info
        if self.role == 'lawyer':
            missing = []
            if not self.enrolment_number:
                missing.append("enrolment_number")
            if not self.email:
                missing.append("email")
            if not self.phone_number:
                missing.append("phone_number")

            if missing:
                raise ValidationError(
                    f"Lawyers must provide: {', '.join(missing)}"
                )

    @property
    def verified_status(self):
        """Return 'Verified' or 'Unverified' as a human-readable status."""
        return "Verified" if self.is_verified else "Unverified"

    def __str__(self):
        """Readable representation used in admin and debugging."""
        return f"{self.user.username} ({self.role})"


# =============================================================================
# Report Model
# =============================================================================

class Report(models.Model):
    """
    Represents a submitted incident or rights violation report.

    Reports may be:
        - Anonymous (reporter=None)
        - Submitted by a registered UserProfile

    Stores details such as title, description, category, location, and status.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    CATEGORY_CHOICES = [
        ('HR', 'Human Rights'),
        ('GV', 'Gender Violence'),
        ('DV', 'Domestic Violence'),
        ('WL', 'Whistleblowing'),
        ('OT', 'Other'),
    ]

    # Reporter is optional to support anonymous submissions
    reporter = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Incident metadata (optional)
    incident_location = models.CharField(max_length=200, blank=True, null=True)
    incident_date = models.DateField(blank=True, null=True)

    # Category and workflow tracking
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='OT')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Human-friendly summary for admin and logs."""
        return f"{self.title} ({self.status})"


# =============================================================================
# Evidence Model
# =============================================================================

class Evidence(models.Model):
    """
    Uploadable evidence files linked to a Report.
    Can include images, videos, PDFs, audio, etc.
    """

    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='evidences'
    )
    file = models.FileField(upload_to='evidence/')
    caption = models.CharField(max_length=200, blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Show caption if present, else fallback to generic label."""
        return self.caption or f"Evidence {self.id} for {self.report.title}"


# =============================================================================
# Case Model
# =============================================================================

class Case(models.Model):
    """
    Links a Report to follow-up legal or NGO processes.

    - Each Report can escalate into a Case.
    - A Case may have a Lawyer, an NGO, or both assigned.
    - Tracks last updates and engagement details.
    """

    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name='case'
    )

    assigned_lawyer = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lawyer_cases'
    )
    assigned_ngo = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ngo_cases'
    )

    status_update = models.TextField(blank=True, null=True)
    last_contact_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Readable case representation."""
        return f"Case for {self.report.title}"
