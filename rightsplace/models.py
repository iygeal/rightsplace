from django.db import models
from django.contrib.auth.models import User

# -----------------------------------------------------------------------------
# RightsPlace Models
# -----------------------------------------------------------------------------
# This file defines the core data structure for the RightsPlace platform.
# Models include:
#  - UserProfile: Extended info about users (Lawyers, NGOs, or Regular Users)
#  - Report: Represents a human rights violation or abuse report
#  - Evidence: Attached files (images, videos, docs) related to a report
#  - Case: Represents follow-up and handling of a report by legal/NGO actors
# -----------------------------------------------------------------------------


class UserProfile(models.Model):
    """
    Extends Django's built-in User model to store additional user information.
    Differentiates between Lawyers, NGOs, and Regular Users, with optional
    verification and contact preferences.
    """
    ROLE_CHOICES = [
        ('lawyer', 'Lawyer'),
        ('ngo', 'NGO Representative'),
        ('user', 'Regular User'),
    ]

    # Relationship with Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Role classification
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='user')

    # Contact and organizational details
    organization_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Organization name (required for NGOs)."
    )
    phone_number = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Optional phone contact."
    )
    email = models.EmailField(
        blank=True, null=True,
        help_text="Optional contact email for communication and verification."
    )
    location = models.CharField(max_length=100, blank=True, null=True)

    # User preferences
    wants_contact = models.BooleanField(
        default=False,
        help_text="If true, user is willing to be contacted about their report."
    )

    # Verification flag (for NGOs/Lawyers only)
    is_verified = models.BooleanField(
        default=False,
        help_text="Mark as verified after admin approval (applies to NGOs and Lawyers)."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------------------------------------------------------------
    # Validation & representation
    # -------------------------------------------------------------------------
    def clean(self):
        """Ensure role-based rules are respected."""
        from django.core.exceptions import ValidationError

        # Only NGOs and Lawyers can be verified
        if self.role == 'user' and self.is_verified:
            raise ValidationError("Only NGOs and Lawyers can be verified.")

        # NGOs must have organization_name
        if self.role == 'ngo' and not self.organization_name:
            raise ValidationError(
                "NGO Representatives must provide an organization name.")

        # Lawyers and NGOs must have contact info
        if self.role in ['lawyer', 'ngo']:
            if not self.email or not self.phone_number:
                raise ValidationError(
                    "Lawyers and NGOs must provide both email and phone number.")

    @property
    def verified_status(self):
        """Return human-readable verification status."""
        return "Verified" if self.is_verified else "Unverified"

    def __str__(self):
        """Readable name for admin and debugging."""
        return f"{self.user.username} ({self.role})"



class Report(models.Model):
    """
    Represents a human rights abuse report submitted by a user or anonymously.
    Reporters may remain anonymous, but must still provide clear case details.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    # Reporter can be null for anonymous submissions
    reporter = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Optional location info for the incident
    incident_location = models.CharField(max_length=200, blank=True, null=True)
    incident_date = models.DateField(blank=True, null=True)

    # Current case status (defaults to Pending)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    # Category of cases (optiona)
    CATEGORY_CHOICES = [
        ('HR', 'Human Rights'),
        ('GV', 'Gender Violence'),
        ('DV', 'Domestic Violence'),
        ('WL', 'Whistleblowing'),
        ('OT', 'Other'),
    ]

    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='OT'
    )

    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a readable string summary of the report."""
        return f"{self.title} ({self.status})"


class Evidence(models.Model):
    """
    Represents supporting evidence for a report (photos, videos, documents).

    """

    # Each evidence item belongs to one Report
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='evidences'
    )

    # File upload field
    file = models.FileField(upload_to='evidence/')

    # Optional short caption
    caption = models.CharField(max_length=200, blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the filename or caption."""
        return self.caption or f"Evidence {self.id} for {self.report.title}"


class Case(models.Model):
    """
    Represents the follow-up and management of a reported case.
    Lawyers and NGOs can be assigned to handle reports as formal cases.
    """

    # Each Case corresponds to exactly one Report
    report = models.OneToOneField(
        Report, on_delete=models.CASCADE, related_name='case'
    )

    # Responsible parties
    assigned_lawyer = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lawyer_cases'
    )
    assigned_ngo = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ngo_cases'
    )

    # Status and notes
    status_update = models.TextField(blank=True, null=True)
    last_contact_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a readable case identifier."""
        return f"Case for {self.report.title}"
