from django import forms
from .models import Device, UserProfile
from django.forms.widgets import DateInput, TimeInput

class DeviceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Device
        fields = ['device', 'ip', 'door_port', 'date_purchased', 'is_active', 'is_synchronized', 'user', 'password', 'massive_opening']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__' 

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        required_fields = ['device', 'first_name', 'last_name', 'dni', 'email', 'gender', 'address', 'phone', 
                           'is_active', 'is_staff', 'profile_type', 'user_type' ]
        for field_name in required_fields:
            self.fields[field_name].required = True

        not_required_fields = ['begin_time', 'end_time', 'file_image']  
        for field_name in not_required_fields:
            self.fields[field_name].required = False
