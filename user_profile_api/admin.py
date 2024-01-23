from django.contrib import admin
from user_profile_api.models import UserTypes, UserProfile, UserProfileStudent, UserProfileMaintenance, Room, Subject, Device, Career, CareerSubjectYear, SubjectSchedule
from django.utils import timezone
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django import forms
from user_profile_api.services import get_default_user_device_id, get_default_schedule_id
from .forms import DeviceForm, UserProfileForm, UserProfileStudentForm, UserProfileMaintenanceForm
from django.conf import settings
import requests
from requests.auth import HTTPDigestAuth
import json
from user_profile_api.urls_services import (URL_RECORD_USER, URL_DELETE_USER, URL_SEARCH_USER, URL_MODIFY_USER )
from django.db.models.signals import post_delete
from django.dispatch import receiver

class UserProfileStudentInline(admin.StackedInline):
    model = UserProfileStudent
    form = UserProfileStudentForm
    extra = 1 

class UserProfileMaintenanceInline(admin.StackedInline):
    form = UserProfileMaintenanceForm
    model = UserProfileMaintenance
    extra = 1

@admin.register(UserProfile)
class ManageUser(admin.ModelAdmin):
    inlines = [UserProfileStudentInline, UserProfileMaintenanceInline]
    form = UserProfileForm
    list_display=('user_device_id', 'dni', 'first_name', 'last_name', 'email', 'phone','user_type')
    ordering=('user_device_id', 'first_name','last_name')
    search_fields= ('user_device_id', 'dni', 'email', 'phone', 'first_name', 'last_name')
    list_per_page=50
    #filter_vertical = ('user_type',)
    exclude = ('planTemplateNo',)
    #readonly_fields=('date_created', 'last_updated', 'timeType')

    def save_model(self, request, obj, form, change):
        obj.last_updated = timezone.now()

        device = obj.device
        ip = device.ip
        door_port = device.door_port
        uuid = settings.DEVICE_UUID
        username = device.user
        password = device.get_password()

        if change:
            url = f"http://{ip}:{door_port}{URL_MODIFY_USER}?format=json&devIndex={uuid}"
            headers = {'Content-Type': 'application/json'}
            print(url)

            if obj.begin_time == None and obj.end_time == None:
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(obj.user_device_id),
                        "name": str(obj.first_name + " " + obj.last_name),
                        "userType": obj.profile_type,
                        "gender": obj.gender,
                        "Valid": {
                            "enable": obj.is_active
                        }, 
                        "localUIRight": obj.is_staff
                    }
                }
                print(data)
            else:
                begin_time_str = obj.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if obj.begin_time else None
                end_time_str = obj.end_time.strftime("%Y-%m-%dT%H:%M:%S") if obj.end_time else None
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(obj.user_device_id),
                        "name": str(obj.first_name + " " + obj.last_name),
                        "userType": obj.profile_type,
                        "gender": obj.gender,
                        "Valid": {
                            "enable": obj.is_active, 
                            "beginTime": begin_time_str,
                            "endTime": end_time_str,
                        }, 
                        "localUIRight": obj.is_staff
                    }
                }
                print(data)

            auth = HTTPDigestAuth(username, password)
            response = requests.put(url, data=json.dumps(data), headers=headers, auth=auth)

            if response.status_code == 200:
                print('Usuario modificado correctamente.')
            else:
                print('Error al modificar el usuario en el dispositivo remoto. Código de estado:', response.status_code)
                print('Respuesta del servidor:', response.text)

        else: 
            url = f"http://{ip}:{door_port}{URL_RECORD_USER}?format=json&devIndex={uuid}"
            headers = {'Content-Type': 'application/json'}
            print(url)

            if obj.begin_time == None and obj.end_time == None:
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(obj.user_device_id),
                        "name": str(obj.first_name + " " + obj.last_name),
                        "userType": obj.profile_type,
                        "gender": obj.gender,
                        "Valid": {
                            "enable": obj.is_active
                        }, 
                        "localUIRight": obj.is_staff
                    }
                }
                print(data)
            else:
                begin_time_str = obj.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if obj.begin_time else None
                end_time_str = obj.end_time.strftime("%Y-%m-%dT%H:%M:%S") if obj.end_time else None
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(obj.user_device_id),
                        "name": str(obj.first_name + " " + obj.last_name),
                        "userType": obj.profile_type,
                        "gender": obj.gender,
                        "Valid": {
                            "enable": obj.is_active, 
                            "beginTime": begin_time_str,
                            "endTime": end_time_str,
                        }, 
                        "localUIRight": obj.is_staff
                    }
                }
                print(data)

            auth = HTTPDigestAuth(username, password)
            response = requests.post(url, data=json.dumps(data), headers=headers, auth=auth)

            if response.status_code == 200:
                print('Usuario agregado correctamente al dispositivo remoto.')
            else:
                print('Error al agregar el usuario al dispositivo remoto. Código de estado:', response.status_code)
                print('Respuesta del servidor:', response.text)
        
        super().save_model(request, obj, form, change)

    @receiver(post_delete, sender=UserProfile)
    def post_delete_userprofile(sender, instance, **kwargs):
        device = instance.device
        ip = device.ip
        door_port = device.door_port
        uuid = settings.DEVICE_UUID
        username = device.user
        password = device.get_password()

        url = f"http://{ip}:{door_port}{URL_DELETE_USER}?format=json&devIndex={uuid}"
        headers = {'Content-Type': 'application/json'}
        print(url)

        data = {
            "UserInfoDetail": {
                "mode": "byEmployeeNo",
                "EmployeeNoList": [{
                    "employeeNo": str(instance.user_device_id)
                }]
            }
        }

        auth = HTTPDigestAuth(username, password)
        response = requests.put(url, data=json.dumps(data), headers=headers, auth=auth)

        if response.status_code == 200:
            print('Usuario eliminado correctamente al dispositivo remoto.')
        else:
            print('Error al eliminar el usuario del dispositivo remoto. Código de estado:', response.status_code)
            print('Respuesta del servidor:', response.text)

    """def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user_profile = UserProfile.objects.get(id=form.instance.id)
        student_profile = UserProfileStudent.objects.get(user_profile=user_profile)
        print(user_profile, " ", student_profile)"""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        default_user_device_id = get_default_user_device_id()
        form.base_fields['user_device_id'].initial = default_user_device_id
        if obj:  # estamos modificando un objeto existente
            form.base_fields['profile_type'].choices = [
                ('normal', 'Normal'),
                ('visitor', 'Visitante'),
                ('blackList', 'Bloqueado')
            ]
        else:  # estamos creando un nuevo objeto
            form.base_fields['profile_type'].choices = [
                ('normal', 'Normal'),
                ('visitor', 'Visitante')
            ]
        return form

@admin.register(Room)
class ManageRoom(admin.ModelAdmin):
    list_display=('room','location')
    ordering=('id',)
    search_fields= ('id',)
    list_per_page=10


@admin.register(Career)
class ManageCareer(admin.ModelAdmin):
    list_display=('name_career',)
    ordering=('id',)
    search_fields= ('id','name_career')
    list_per_page=10

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'


@admin.register(Subject)
class ManageSubject(admin.ModelAdmin):
    list_display=('subject',)
    ordering=('id',)
    search_fields= ('id','subject')
    list_per_page=10
    
@admin.register(CareerSubjectYear)
class ManageCareerSubjectYear(admin.ModelAdmin):
    list_display=('career', 'subject', 'year')
    ordering=('id',)
    search_fields=('id', 'career', 'subject', 'year')
    list_per_page=10


@admin.register(SubjectSchedule)
class ManageSubjectSchedule(admin.ModelAdmin):
    list_display=('horario_id', 'device', 'career_subject_year', 'day', 'begin_time', 'end_time')
    ordering=('horario_id',)
    search_fields=('horario_id', 'career_subject_year')
    list_per_page=10

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        default_horario_id = get_default_schedule_id()
        form.base_fields['horario_id'].initial = default_horario_id
        return form

class ManageDeviceForm(DeviceForm):
    class Meta(DeviceForm.Meta):
        model = Device

@admin.register(Device)
class ManageDevice(admin.ModelAdmin):
    form = ManageDeviceForm
    list_display=('id', 'device', 'ip', 'door_port', 'user','date_purchased', 'is_active', 'is_synchronized', 'massive_opening')
    ordering=('id',)
    search_fields= ('id','device','date_purchased','user')
    list_per_page=10
  
@admin.register(UserTypes)
class ManageUserTypes(admin.ModelAdmin):
    list_display=('id', 'user_type')
    ordering=('id',)
    search_fields= ('id','user_type')
    list_per_page=10

def create_default_usertypes():
    default_usertypes = ['Alumno', 'Mantenimiento']
    for usertype in default_usertypes:
        UserTypes.objects.get_or_create(user_type=usertype)

create_default_usertypes()