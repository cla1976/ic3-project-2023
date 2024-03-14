from django import forms
from .models import Device, UserProfile, UserProfileStudent, UserProfileMaintenance
from django.forms.widgets import DateInput, TimeInput
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone

class DeviceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Device
        fields = '__all__'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__' 

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
         # Excluye la opción 'Bloqueado' al agregar un nuevo usuario
        if not self.instance.pk:
            self.fields['profile_type'].choices = [choice for choice in self.fields['profile_type'].choices if choice[0] != 'blackList']

        required_fields = ['device', 'first_name', 'last_name', 'dni', 'email', 'gender', 'address', 'phone', 
                           'is_active', 'is_staff', 'profile_type', 'user_type' ]
        for field_name in required_fields:
            self.fields[field_name].required = True

        not_required_fields = ['begin_time', 'end_time']  
        for field_name in not_required_fields:
            self.fields[field_name].required = False
        
        if self.instance.pk:
            self.fields['dni'].widget.attrs['readonly'] = True

        if self.instance.user_type is not None:
            self.fields['user_type'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')
        begin_time = cleaned_data.get('begin_time')
        end_time = cleaned_data.get('end_time')
        min_date = timezone.localtime(timezone.now()).date()
        year = min_date.year + 1
        max_date = timezone.make_aware(datetime(year, 12, 31)).date()
        begin_time_date = begin_time.date() if begin_time is not None else None
        end_time_date = end_time.date() if end_time is not None else None
        begin_time_hour_minute = begin_time.strftime('%H:%M') if begin_time is not None else None
        end_time_hour_minute = end_time.strftime('%H:%M') if end_time is not None else None

        if is_active == 'Sí':
            is_active = True
        else:
            is_active = False
            
        if is_active == False:
            cleaned_data['begin_time'] = None
            cleaned_data['end_time'] = None
                
        if is_active == True:
            
            if (begin_time != None and end_time != None):
                if begin_time_date > end_time_date:
                    raise ValidationError('La fecha de inicio de habilitación no puede ser posterior a la fecha de fin de habilitación.')
                elif begin_time_date == end_time_date:
                    if begin_time_hour_minute >= end_time_hour_minute:
                        raise ValidationError('La fecha de inicio de habilitación no puede ser mayor o igual que la fecha de fin de habilitación.')
                if (begin_time_date < min_date or end_time_date > max_date):
                    min_date_str = min_date.strftime('%d/%m/%Y')
                    max_date_str = max_date.strftime('%d/%m/%Y')
                    raise ValidationError('La fecha de habilitación del usuario estar entre {} y {}.'.format(min_date_str, max_date_str))
            if begin_time == None or end_time == None:
                raise ValidationError('Si la opción de fecha de habilitación está en sí, se deben ingresar tanto las fechas de inicio y fin de habilitación como sus respectivos horarios.')

        return cleaned_data

class UserProfileStudentForm(forms.ModelForm):
    class Meta:
        model = UserProfileStudent
        fields = '__all__'    

class UserProfileMaintenanceForm(forms.ModelForm):
    class Meta:
        model = UserProfileMaintenance
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(UserProfileMaintenanceForm, self).__init__(*args, **kwargs)

        required_fields = ['sunday' ,'monday', 'tuesday', 'thursday', 'wednesday', 'thursday', 'friday', 'saturday']
        for field_name in required_fields:
            self.fields[field_name].required = True

        not_required_fields = ['sunday_time_begin', 'sunday_time_end', 'monday_time_begin', 
                               'monday_time_end', 'tuesday_time_begin', 'tuesday_time_end',
                               'wednesday_time_begin', 'wednesday_time_end', 'thursday_time_begin', 
                               'thursday_time_end', 'friday_time_begin', 'friday_time_end', 
                               'saturday_time_begin', 'saturday_time_end']  
        for field_name in not_required_fields:
            self.fields[field_name].required = False