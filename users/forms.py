from django import forms

class UserProfileForm(forms.Form):
    about = forms.CharField(widget=forms.Textarea)
