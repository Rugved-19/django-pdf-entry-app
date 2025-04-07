# pdf_app/forms.py

from django import forms
from .models import Entry, User

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['raw_input', 'amount']
        widgets = {
            'raw_input': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',  # Trick browser
                'name': 'raw_input_fake',        # Fake name to avoid suggestions
                'placeholder': 'Enter Raw Input'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'name': 'amount_fake',
                'placeholder': 'Enter Amount'
            }),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Enter Name'
            }),
        }