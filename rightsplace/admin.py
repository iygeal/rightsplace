from django.contrib import admin
from .models import UserProfile, Report, Evidence, Case


class EvidenceInline(admin.TabularInline):
    """
    Inline admin configuration for Evidence objects.

    This allows Evidence entries to be added, viewed, or edited directly
    from within the Report admin page. It improves workflow by avoiding
    the need to switch back and forth between pages.
    """
    model = Evidence
    extra = 1  # Show one blank evidence form by default
    # Evidence timestamps should never be edited manually
    readonly_fields = ('uploaded_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Report model.

    Manages how reports appear in the Django admin interface, including:
    - List display columns
    - Filters
    - Search capability
    - Inline evidence management
    """
    list_display = ('title', 'category', 'status', 'reporter', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'reporter__user__username')
    readonly_fields = ('created_at',)
    inlines = [EvidenceInline]  # Show evidence entries under each report


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Evidence model.

    Ensures admin users can browse uploaded evidence files efficiently.
    Uploaded date is read-only because it is auto-generated.
    """
    list_display = ('report', 'file', 'uploaded_at')
    search_fields = ('report__title',)
    readonly_fields = ('uploaded_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing user profiles.

    This setup makes it easy for staff to:
    - Verify lawyers and NGOs
    - View user role and contact preference
    - Search by multiple user-related fields
    """
    list_display = (
        'user', 'role', 'organization_name', 'is_verified',
        'wants_contact', 'phone_number', 'email', 'enrolment_number',
        'city', 'state', 'specialization', 'rc_number'
    )
    list_filter = ('role', 'is_verified', 'wants_contact')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'email', 'phone_number', 'organization_name', 'enrolment_number',
        'city', 'state', 'specialization', 'rc_number'
    )
    # Allows admin to verify lawyers/NGOs directly from list view
    list_editable = ('is_verified',)

    # Important: Show non-editable user metadata cleanly
    autocomplete_fields = ('user',)  # Helpful when user list is large


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Case model.

    Cases represent assignments made between:
    - A report
    - A lawyer
    - An NGO (if applicable)

    Admin users can search cases and quickly identify assigned entities.
    """
    list_display = ('report', 'assigned_lawyer', 'assigned_ngo', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'report__title',
        'assigned_lawyer__user__username',
        'assigned_ngo__user__username',
    )
    readonly_fields = ('created_at',)
