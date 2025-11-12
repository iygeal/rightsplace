from django.contrib import admin
from .models import UserProfile, Report, Evidence, Case


class EvidenceInline(admin.TabularInline):
    """
    Allows Evidence objects to be displayed and edited
    directly on the Report admin page.
    """
    model = Evidence
    extra = 1  # Show one empty evidence form by default


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Customizes how the Report model is displayed in the admin panel.
    """
    list_display = ('title', 'category', 'status', 'reporter', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'reporter__user__username')
    inlines = [EvidenceInline]  # Display related evidence under the report
    readonly_fields = ('created_at',)  # Created date shouldn’t be editable


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """
    Controls display and management of Evidence objects in the admin panel.
    """
    list_display = ('report', 'file', 'uploaded_at')
    search_fields = ('report__title',)
    readonly_fields = ('uploaded_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Customizes how user profiles are managed in the admin panel.
    """
    list_display = (
        'user', 'role', 'organization_name', 'is_verified',
        'wants_contact', 'phone_number', 'email'
    )
    list_filter = ('role', 'is_verified', 'wants_contact')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'email', 'phone_number', 'organization_name'
    )
    list_editable = ('is_verified',)



@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """
    Customizes how the Case model is displayed in the admin panel.

    List display shows the report title, assigned lawyer and NGO, status, and created date.
    Filtering is available for status and created date.
    Searching is available for report title, assigned lawyer username, and assigned NGO username.
    """
    list_display = ('report', 'assigned_lawyer', 'assigned_ngo', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'report__title',
        'assigned_lawyer__user__username',
        'assigned_ngo__user__username',
    )

