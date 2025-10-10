
from django import forms
from .models import Officer, Education, Family, Award

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'enlistment_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'dob': 'Date of Birth',
            'enlistment_date': 'Enlistment Date',
            'army_number': 'Army ID Number',
            'blood_group': 'Blood Group',
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = '__all__'
        exclude = ['officer']
        widgets = {
            'year_of_passing': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
            'specialization': forms.TextInput(),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'year_of_passing': 'Year of Passing',
        }

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = '__all__'
        exclude = ['officer']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'dob': 'Date of Birth',
            'relation': 'Relationship',
        }

class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = '__all__'
        exclude = ['officer']
        widgets = {
            'date_awarded': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'citation': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'date_awarded': 'Date Awarded',
            'award_name': 'Award Name',
        }