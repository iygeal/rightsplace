from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Report, Evidence


class UserRegistrationForm(forms.ModelForm):
    """
    Handles registration for all user types (Regular User, Lawyer, NGO).
    Combines Django's User model and custom UserProfile fields.
    """

    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    username = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    # Custom UserProfile fields
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    organization_name = forms.CharField(
        max_length=100, required=False, help_text="Required only for NGO representatives."
    )
    phone_number = forms.CharField(
        max_length=20, required=False, help_text="Optional contact number."
    )
    location = forms.CharField(max_length=100, required=False)
    wants_contact = forms.BooleanField(
        required=False,
        label="I want to be contacted for follow-up on reports.",
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'username', 'email', 'password',
            'role', 'organization_name', 'phone_number', 'location', 'wants_contact'
        ]

    def clean(self):
        """
        Enforce required fields based on role and contact preference.
        """
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        wants_contact = cleaned_data.get('wants_contact')
        org_name = cleaned_data.get('organization_name')

        # NGO: Must have organization name and contact info
        if role == 'ngo':
            if not org_name:
                self.add_error(
                    'organization_name', "Organization name is required for NGO representatives.")
            if not cleaned_data.get('email'):
                self.add_error(
                    'email', "Email is required for NGO representatives.")

        # Lawyer: Must provide contact info
        if role == 'lawyer':
            if not cleaned_data.get('email'):
                self.add_error('email', "Email is required for Lawyers.")
            if not cleaned_data.get('phone_number'):
                self.add_error(
                    'phone_number', "Phone number is required for Lawyers.")

        # Regular user with 'wants_contact' must provide at least one contact field
        if role == 'user' and wants_contact:
            if not (cleaned_data.get('email') or cleaned_data.get('phone_number')):
                self.add_error(
                    None, "Please provide at least one contact detail if you want to be contacted.")

        return cleaned_data

    def save(self, commit=True):
        """
        Creates both User and associated UserProfile records.
        """
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )

        profile = UserProfile(
            user=user,
            role=self.cleaned_data['role'],
            organization_name=self.cleaned_data.get('organization_name', ''),
            phone_number=self.cleaned_data.get('phone_number', ''),
            email=self.cleaned_data.get('email', ''),
            location=self.cleaned_data.get('location', ''),
        )

        # Store the contact preference
        profile.wants_contact = self.cleaned_data.get('wants_contact', False)

        if commit:
            profile.save()

        return profile


class ReportForm(forms.ModelForm):
    """
    Handles submission of human rights abuse reports.
    Reporters can remain anonymous or choose to be contacted.
    """

    class Meta:
        model = Report
        fields = [
            'title', 'description', 'incident_location', 'incident_date', 'category'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'incident_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        """
        Encourage valid evidence and ensure meaningful details.
        """
        cleaned_data = super().clean()
        description = cleaned_data.get('description')

        if len(description.strip()) < 30:
            self.add_error(
                'description', "Please provide a more detailed description of the incident.")

        return cleaned_data


class EvidenceForm(forms.ModelForm):
    """
    Handles uploading of files supporting a Report.
    Evidence is optional but highly encouraged.
    """

    class Meta:
        model = Evidence
        fields = ['file', 'caption']


class UserLoginForm(AuthenticationForm):
    """
    Custom login form allowing users to authenticate using either
    their username or email address.
    """
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        """
        Override authentication to allow login via email.
        """
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')

        if username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                # replace with username for auth
                cleaned_data['username'] = user_obj.username
            except User.DoesNotExist:
                pass  # if no email match, Django will handle normal username auth

        return cleaned_data
