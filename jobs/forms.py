from django import forms
from .models import Job, Message


class EmployerJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("title", "description", "responsibilities", "required_skills", "location", "work_mode", "employment_type", "experience_level", "minimum_salary", "maximum_salary", "application_url", "closing_date")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "responsibilities": forms.Textarea(attrs={"rows": 3}),
            "required_skills": forms.Textarea(attrs={"rows": 2, "placeholder": "Python, SQL, Django"}),
            "closing_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get("minimum_salary"), cleaned.get("maximum_salary")
        if low is not None and high is not None and low > high:
            self.add_error("maximum_salary", "Maximum salary must be greater than or equal to minimum salary.")
        return cleaned


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 2, "maxlength": 4000, "placeholder": "Write a message about the role..."})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].widget.attrs["class"] = "form-control"

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if not body:
            raise forms.ValidationError("Message cannot be empty.")
        return body
