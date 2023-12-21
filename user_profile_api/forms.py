from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Device
        fields = ['device', 'ip', 'door_port', 'date_purchased', 'is_active', 'is_synchronized', 'user', 'password', 'massive_opening']