from celery import Celery, shared_task, chain
from django.core.exceptions import ObjectDoesNotExist
import json
from datetime import datetime
from django.utils import timezone
import requests
from requests.auth import HTTPDigestAuth
from users_admin.settings import DEVICE_UUID
from user_profile_api.urls_services import URL_RECORD_USER, URL_SEARCH_USER
from user_profile_api.models import Device, UserProfile
from django.db.models.signals import post_save
from .signals import post_save_user_profile
from users_admin.settings import BASE_URL, DEVICE_UUID, GATEWAY_USER, GATEWAY_PASSWORD, GATEWAY_PORT

@shared_task
def sincronize_users():
    try:
        # Iterar sobre todos los dispositivos en tu base de datos
        for device in Device.objects.all():
            ip = device.ip
            door_port = GATEWAY_PORT
            #uuid = DEVICE_UUID
            username = device.user
            password = device.get_password()
            device_id = device.id

            url = f"http://{ip}:{door_port}{URL_SEARCH_USER}?format=json"
            headers = {'Content-Type': 'application/json'}
            data = {
                "UserInfoSearchCond": {
                    "searchID": "0",
                    "searchResultPosition": 0,
                    "maxResults": 30
                }
            }

            auth = HTTPDigestAuth(username, password)
            response = requests.post(url, json=data, headers=headers, auth=auth)
            if response.status_code == 200:
                # Obtener la lista de usuarios remotos
                response_data = response.json()
                user_info_search = response_data.get('UserInfoSearch', {})
                remote_users = user_info_search.get('UserInfo', [])
                remote_user_ids = [user.get('employeeNo') for user in remote_users]
                
                # Obtener todos los usuarios en tu base de datos para este dispositivo
                local_users = UserProfile.objects.filter(device=device)

                # Obtener los DNIs de los usuarios en tu base de datos
                local_user_dniss = set(UserProfile.objects.filter(device=device).values_list('dni', flat=True))

                # Logica para agregar usuarios al dispositivo
                for dni in local_user_dniss:
                    if dni not in remote_user_ids:
    
                        # Realizar una consulta a la base de datos para obtener toda la información del usuario
                        user = UserProfile.objects.get(device=device, dni=dni)

                        first_name = user.first_name
                        last_name = user.last_name
                        gender = user.gender
                        is_active = user.is_active
                        begin_time = user.begin_time
                        end_time = user.end_time
                        is_staff = user.is_staff
                        profile_type = user.profile_type

                        if is_active == 'Sí':
                            is_active = True
                        else:
                            is_active = False

                        if is_staff == 'Sí':
                            is_staff = True
                        else:
                            is_staff = False

                        url = f"http://{ip}:{door_port}{URL_RECORD_USER}?format=json"
                        headers = {'Content-Type': 'application/json'}

                        if begin_time == None and end_time == None:
                            data = {
                            "UserInfo":
                                {
                                    "employeeNo": str(dni),
                                    "name": str(first_name + " " + last_name),
                                    "userType": profile_type,
                                    "gender": gender,
                                    "Valid": {
                                        "enable": is_active
                                    }, 
                                    "localUIRight": is_staff
                                }
                            }
                        else:
                            begin_time_str = begin_time.strftime("%Y-%m-%dT%H:%M:%S") if begin_time else None
                            end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S") if end_time else None
                            data = {
                            "UserInfo":
                                {
                                    "employeeNo": str(dni),
                                    "name": str(first_name + " " + last_name),
                                    "userType": profile_type,
                                    "gender": gender,
                                    "Valid": {
                                        "enable": is_active, 
                                        "beginTime": begin_time_str,
                                        "endTime": end_time_str,
                                    }, 
                                    "localUIRight": is_staff
                                }
                            }

                        auth = HTTPDigestAuth(username, password)
                        response = requests.post(url, data=json.dumps(data), headers=headers, auth=auth)

                        if response.status_code == 200:
                            print('Usuario agregado correctamente al dispositivo remoto.')
                        else:
                            print('Error al agregar el usuario al dispositivo remoto. Código de estado:', response.status_code)
                            print('Respuesta del servidor:', response.text)

                # Logica para agregar usuarios a la base de datos
                for user in remote_users:
                    employee_number = user.get('employeeNo', '')
                    if employee_number not in local_user_dniss:
                        name = user.get('name', '')
                        first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
                        gender = user.get('gender', '')
                        is_active = user.get('Valid', {}).get('enable', False)
                        if is_active == True:
                            is_active = 'Sí'
                        else:
                            is_active = 'No'
                        is_staff = user.get('localUIRight', False)
                        if is_staff == True:
                            is_staff = 'Sí'
                        else:
                            is_staff = 'No'
                        profile_type = user.get('userType', '')
                        dni = employee_number
                        begin_time = user.get('Valid', {}).get('beginTime', '')
                        begin_time2 = timezone.make_aware(datetime.fromisoformat(begin_time))
                        end_time = user.get('Valid', {}).get('endTime', '')
                        end_time2 = timezone.make_aware(datetime.fromisoformat(end_time))

                        post_save.disconnect(post_save_user_profile, sender=UserProfile)

                        # Crear y guardar el usuario en la base de datos
                        if is_active == True:
                            UserProfile.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                gender=gender,
                                is_active=is_active,
                                is_staff=is_staff,
                                profile_type=profile_type,
                                dni=dni,
                                begin_time=begin_time2,
                                end_time=end_time2,
                                device_id=device_id
                            )
                            print('Usuario agregado a la BD local')
                        else:
                            UserProfile.objects.create(
                                first_name=first_name,
                                last_name=last_name,
                                gender=gender,
                                is_active=is_active,
                                is_staff=is_staff,
                                profile_type=profile_type,
                                dni=dni,
                                device_id=device_id
                            )
                            print('Usuario agregado a la BD local')
                            
                # Logica para actualizar base de datos si sucede modificacion de usuarios en dispositivo
                # se tomara de mayor importancia la infomarcion que se encuentra en el dispositivo
                # y no la de la base de datos. Esto con la finalidad de que puede ocurrir con mas
                # probabilidad que los usuarios sean modificados en el dispositivo (pagina hikvision)
                # que en la base de datos (sentencias SQL).
                for user in remote_users:
                    employee_number = user.get('employeeNo', '')

                    # Verificar si el usuario del dispositivo está presente en la base de datos local
                    if employee_number in local_user_dniss:
                        # Obtener información del usuario del dispositivo
                        name = user.get('name', '')
                        first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
                        gender = user.get('gender', '')
                        is_active = user.get('Valid', {}).get('enable', False)
                        if is_active:
                            is_active = 'Sí'
                            begin_time = user.get('Valid', {}).get('beginTime', '')
                            begin_time2 = timezone.make_aware(datetime.fromisoformat(begin_time))
                            end_time = user.get('Valid', {}).get('endTime', '')
                            end_time2 = timezone.make_aware(datetime.fromisoformat(end_time))
                        else:
                            is_active = 'No'
                            begin_time2 = None
                            end_time2 = None
                        is_staff = user.get('localUIRight', False)
                        if is_staff:
                            is_staff = 'Sí'
                        else:
                            is_staff = 'No'
                        profile_type = user.get('userType', '')

                        # Obtener el usuario correspondiente en la base de datos local
                        user_profile = UserProfile.objects.get(dni=employee_number)

                        # Verificar si hay cambios en la información del usuario
                        if (user_profile.first_name != first_name or
                            user_profile.last_name != last_name or
                            user_profile.gender != gender or
                            user_profile.is_active != is_active or
                            user_profile.is_staff != is_staff or
                            user_profile.profile_type != profile_type or
                            user_profile.begin_time != begin_time2 or
                            user_profile.end_time != end_time2):
                            
                            # Actualizar la información del usuario en la base de datos local
                            user_profile.first_name = first_name
                            user_profile.last_name = last_name
                            user_profile.gender = gender
                            user_profile.is_active = is_active
                            user_profile.is_staff = is_staff
                            user_profile.profile_type = profile_type
                            user_profile.begin_time = begin_time2
                            user_profile.end_time = end_time2
                            
                            post_save.disconnect(post_save_user_profile, sender=UserProfile)
                            
                            user_profile.save()
                            print(f"Usuario {first_name} con DNI {employee_number} fue actualizado en la base de datos local.")
            else:
                print(f"No se pudo obtener la lista de usuarios del dispositivo {device.device}.")
    except Exception as e:
        print(f"Error durante la sincronización: {e}")

    return 'Sincronización finalizada'