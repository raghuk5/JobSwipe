from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import JobPreference, Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=120, required=True, widget=forms.TextInput(attrs={"autocomplete":"name","placeholder":"Your full name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete":"email","placeholder":"you@example.com"}))
    class Meta:
        model = User
        fields = ("full_name", "email")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email address", widget=forms.EmailInput(attrs={"autofocus":True,"autocomplete":"email","placeholder":"you@example.com"}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete":"current-password","placeholder":"Your password"}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("qualification", "skills", "experience_years", "resume")
        widgets = {
            "qualification": forms.TextInput(attrs={"placeholder":"e.g. B.Tech Electronics and Communication Engineering"}),
            "skills": forms.Textarea(attrs={"rows":3,"placeholder":"Python, SQL, Django, PostgreSQL"}),
            "experience_years": forms.NumberInput(attrs={"min":"0","max":"60","step":"0.5"}),
            "resume": forms.ClearableFileInput(attrs={"accept":".pdf,.doc,.docx"}),
        }
        help_texts = {"resume":"Optional. PDF, DOC, or DOCX; maximum 5 MB.", "experience_years":"Enter 0 if you are a fresher."}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class JobPreferenceForm(forms.ModelForm):
    class Meta:
        model = JobPreference
        fields = ("preferred_roles","preferred_locations","minimum_salary","maximum_salary","work_mode","employment_type","experience_level","willing_to_relocate")
        widgets = {
            "preferred_roles": forms.Textarea(attrs={"rows":2,"placeholder":"Python Developer, Junior Software Engineer, Data Analyst"}),
            "preferred_locations": forms.Textarea(attrs={"rows":2,"placeholder":"Trichy, Chennai, Bengaluru, Remote, Pan India"}),
            "minimum_salary": forms.NumberInput(attrs={"min":"0","step":"10000","placeholder":"e.g. 300000"}),
            "maximum_salary": forms.NumberInput(attrs={"min":"0","step":"10000","placeholder":"e.g. 600000"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control")
    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get("minimum_salary"), cleaned.get("maximum_salary")
        if low is not None and high is not None and low > high:
            self.add_error("maximum_salary", "Maximum salary must be greater than or equal to minimum salary.")
        return cleaned


class EmployerRegisterForm(RegisterForm):
    company_name = forms.CharField(max_length=160, label="Company name", widget=forms.TextInput(attrs={"placeholder": "Your registered company name"}))
    company_website = forms.URLField(required=False, label="Company website", widget=forms.URLInput(attrs={"placeholder": "https://company.example"}))
    company_headquarters = forms.CharField(max_length=120, label="Headquarters", widget=forms.TextInput(attrs={"placeholder": "City, State"}))
    company_description = forms.CharField(required=False, label="Company description", widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Briefly describe your company"}))

    class Meta(RegisterForm.Meta):
        fields = ("full_name", "email")

    def clean_company_name(self):
        name = self.cleaned_data["company_name"].strip()
        from jobs.models import Company
        if Company.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A company with this name already exists. Contact the administrator to join it.")
        return name
