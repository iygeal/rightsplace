from django.contrib import admin
from .models import UserProfile, Report, Evidence, Case


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

    # Show non-editable user metadata cleanly
    autocomplete_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        """Make is_verified a readonly field for reporters
            and editable for NGOs and Lawyers
        """
        if obj and obj.role == 'user':
            return self.readonly_fields + ('is_verified',)
        return self.readonly_fields

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
    list_display = (
        'title', 'category', 'status',
        'reporter', 'has_case', 'created_at'
        )
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'reporter__user__username')
    readonly_fields = ('created_at',)
    inlines = [EvidenceInline]  # Show evidence entries under each report

    def has_case(self, obj):
        """
        Returns a boolean indicating whether the given Report has a Case associated with it.

        This is used to generate a read-only column in the Report admin list view.
        """
        return hasattr(obj, 'case')
    has_case.boolean = True
    has_case.short_description = "Case Created?"


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


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Case model.

    Ensures the admin page shows the report, assigned lawyer, assigned NGO, and creation date.
    Allows searching by report title, assigned lawyer username, and assigned NGO username.
    """
    list_display = ('report', 'assigned_lawyer', 'assigned_ngo', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'report__title',
        'assigned_lawyer__user__username',
        'assigned_ngo__user__username',
    )
    readonly_fields = ('created_at',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_lawyer":
            kwargs["queryset"] = UserProfile.objects.filter(
                role="lawyer", is_verified=True
            )
        if db_field.name == "assigned_ngo":
            kwargs["queryset"] = UserProfile.objects.filter(
                role="ngo", is_verified=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def save_model(self, request, obj, form, change):
        """
        Overridden save_model to automate status transition from "pending" to "in_progress" when a Case is created or updated.
        """
        super().save_model(request, obj, form, change)
        if obj.report.status == "pending":
            obj.report.status = "in_progress"
            obj.report.save()
