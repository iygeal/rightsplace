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
    This model helps differentiate between user roles (e.g., Lawyer, NGO).
    """
    ROLE_CHOICES = [
        ('lawyer', 'Lawyer'),
        ('ngo', 'NGO Representative'),
        ('user', 'Regular User'),
    ]

    # Relationship with the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Role helps us know what kind of user this is
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Optional contact details
    organization = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    # Record creation time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable string representation of the profile."""
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
