from django import forms
from .models import Address, Bill, Certificate

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ('firstName', 'lastName','companyName', 'email', 'phoneNumber')

        widgets = {
            'firstName': forms.TextInput(attrs={'class': 'form-control'}),
            'lastName': forms.TextInput(attrs={'class': 'form-control'}),
            'companyName': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phoneNumber': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('street1', 'street2', 'city', 'state', 'zip_code', 'country')

        widgets = {
            'street1': forms.TextInput(attrs={'class': 'form-control'}),
            'street2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

         # Add Bootstrap classes to fields
        widgets['street1'].attrs.update({'class': 'form-control mb-3'})
        widgets['street2'].attrs.update({'class': 'form-control mb-3'})
        widgets['city'].attrs.update({'class': 'form-control mb-3'})
        widgets['state'].attrs.update({'class': 'form-control mb-3'})
        widgets['zip_code'].attrs.update({'class': 'form-control mb-3'})
        widgets['country'].attrs.update({'class': 'form-control mb-3'})

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ('receiverName', 'receiverEmail')
        
        widgets = {
            'receiverName': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'receiverEmail': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }
        
        # Add required=False to remove the "This field is required" error message
        # for these fields
        error_messages = {
            'receiverName': {
                'required': ''
            },
            'receiverEmail': {
                'required': ''
            }
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['receiverName'].required = False
            self.fields['receiverEmail'].required = False
