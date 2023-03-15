from django import forms

from customer.models import Certificate

INPUT_CLASS = 'w-full py-4 px-6 rounded-xl border-1'

class upload(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['photo']

        widgets = {
            'photo': forms.FileInput(attrs={'class': INPUT_CLASS}),
        }

class uploadLatLong(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['latitude', 'longitude']

        widgets = {
            'latitude': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'longitude': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }