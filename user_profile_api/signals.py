from django.db.models.signals import post_save, pre_save, pre_delete, post_delete, m2m_changed, post_migrate
from django.dispatch import receiver
import requests
import yaml
import json, base64
from datetime import datetime, timedelta
from user_profile_api.middleware import specific_page_loaded
from django.conf import settings
from django.utils import timezone 

from user_profile_api.urls_services import (
    URL_RECORD_USER,
    URL_DELETE_USER,
    URL_SEARCH_USER,
    URL_MODIFY_USER,
    URL_RECORD_CARD,
    URL_DELETE_CARD,
    URL_COUNT_USER,
    URL_RECORD_IMAGE,
    URL_UserRightWeekPlanCfg,
    URL_UserRightPlanTemplate,
    URL_FaceDataRecord,
    URL_ADD_CARD,
    URL_MODIFY_CARD,
    URL_DELETE_CARD
)
from users_admin.settings import DEVICE_UUID
from requests.auth import HTTPDigestAuth
from user_profile_api.models import UserProfileStudent, SubjectSchedule, Device, UserTypes, UserProfile, UserProfileMaintenance 
from django.db.models import F
from unidecode import unidecode
from requests.auth import HTTPDigestAuth
import time

# Archivo de señales. Se activan funcionalidades que están ligadas al panel de administración
# que trae por defecto Django basandose en detección de cambios en los modelos 
# localizados en models.py

# Se cambia el booleano para comprobar funcionalidades sin necesidad
# de tener conectado un dispositivo

mockeo = False

# Señal que se acciona al detectar un cambio en las relaciones M2M de la tabla
# UserProfile. Se ejecuta si se carga un usuario relacionado a ciertos horarios.
# En el código se filtra según los dispositivos que están relacionados con los horarios asignados,
# y por cada uno de ellos se envía el JSON para localizar al usuario. 
# Dependiendo del condicional se crea o modifica el usuario con o sin imagen.

#corregida
@receiver(m2m_changed, sender=UserProfileStudent.subject.through)
def update_user_subjects(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add" or action == "pre_remove":

        if mockeo:
            return

        subject_ids = list(pk_set)
        subject_schedules = SubjectSchedule.objects.filter(pk__in=subject_ids)
        device_ips = list(Device.objects.filter(subjectschedule__in=subject_schedules).values_list('ip', flat=True).distinct())
        door_ports = list(Device.objects.filter(subjectschedule__in=subject_schedules).values_list('door_port', flat=True).distinct())
        gateway_users = list(Device.objects.filter(subjectschedule__in=subject_schedules).values_list('user', flat=True).distinct())
        gateway_passwords = list(Device.objects.filter(subjectschedule__in=subject_schedules).values_list('password', flat=True).distinct())

        print("subject_ids")
        print(subject_ids)
        print("subject_schedules")
        print(subject_schedules)


        print("Probando:")
        print(device_ips)
        print(door_ports)
        print("Cantidad de valores:", len(device_ips))

        for i in range(len(device_ips)):


            print("Iteración:", i)
            ip_seleccionada = device_ips[i]
            GATEWAY_PORT = door_ports[i]
            GATEWAY_USER = gateway_users[i]
            GATEWAY_PASSWORD = gateway_passwords[i]

            print(ip_seleccionada)
            print(device_ips)
            print(GATEWAY_PORT)

            print("Filtrar con IP")

            filtered_horario_ids = list(subject_schedules.filter(device__ip=ip_seleccionada).values_list('horario_id', flat=True))
            days = list(subject_schedules.filter(device__ip=ip_seleccionada).values_list('day', flat=True))


            print(filtered_horario_ids)
            print(days)

            base_url = "http://{}:{}".format(ip_seleccionada, GATEWAY_PORT)
            record_url = f"{URL_SEARCH_USER}?format=json"
            full_url = f"{base_url}{record_url}"
            headers = {"Content-type": "application/json"}

            data = {
            "UserInfoSearchCond":
                {
                    "searchID": str(instance.dni),
                    "searchResultPosition":0,
                    "maxResults":1,
                    "EmployeeNoList": [{
                        "employeeNo": str(instance.dni)
                    }]
                }
            }

            response = requests.post(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
            )

            

            response_json = json.loads(response.text)
            response_status = response_json["UserInfoSearch"]["responseStatusStrg"]
            print(response_status)




            if response_status == "NO MATCH" and not action == "pre_remove":

                subject_ids = list(filtered_horario_ids)
                plan_template_no = ','.join(map(str, subject_ids))

                print("Testeando")
                print(plan_template_no)

                base_url = "http://{}:{}".format(ip_seleccionada, GATEWAY_PORT)
                record_url = f"{URL_RECORD_USER}?format=json"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

                data = {
                    "UserInfo": 
                        {
                            "employeeNo": str(instance.dni),
                            "name": str(instance.first_name + " " + instance.last_name),
                            "userType": instance.profile_type,
                            "gender": instance.gender,
                            "Valid": {
                                "enable": instance.is_active,
                                "beginTime": begin_time_str,
                                "endTime": end_time_str,
                                "timeType": instance.timeType
                            },
                            "doorRight": instance.doorRight,
                            "RightPlan": [
                                {
                                    "doorNo": instance.doorNo,
                                    "planTemplateNo": plan_template_no
                                }
                            ],
                            "localUIRight": instance.is_staff,
                            "userVerifyMode": instance.userVerifyMode
                        }
                    }

                response = requests.post(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )

                if response.status_code == 200:
                        print("Usuario creado y cargado con la API y CAMPO")
                        if instance.fileImage:

                            ips = []

                            for subject_schedule in subject_schedules:
                                device = subject_schedule.device
                                if device and device.is_active:  
                                    ips.append(device.ip)

                            print(ips)

                            for ip_address in ips:
                                
                                base_url = f'http://{ip_address}:{GATEWAY_PORT}'
                                record_url = f"{URL_RECORD_IMAGE}?format=json"
                                full_url = f"{base_url}{record_url}"
                                    
                                print("Acá es 1")

                                payload = {
                                    "FaceDataRecord": ('', '{"faceLibType":"blackFD","FDID":"1","FPID":"' + str(instance.dni) + '"}', 'application/json'),
                                    "img": ('Imagen', open(str(instance.fileImage), 'rb'), 'image/jpeg')
                                }

                                print(payload)


                                response = requests.put(full_url, files=payload, auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

                                if response.status_code == 200:
                                    print("Image created succesfully and sent to API!")
                                    print("User created successfully and data sent to API!")
                                else:
                                    raise Exception("Error enviando la imagen al dispositivo: {}".format(response.text))

                        if instance.card:
                            base_url = f'http://{ip_seleccionada}:{GATEWAY_PORT}'
                            record_url = f"{URL_ADD_CARD}?format=json"
                            full_url = f"{base_url}{record_url}"

                            print("Acá se crea con tarjeta")
                            payload = { 
                                "CardInfo": {
                                    "employeeNo": str(instance.user_device_id),
                                    "cardNo": str(instance.card),
                                    "cardType": str(instance.cardType)
                                }
                            }

                            print(payload)
                            
                            response = requests.request("POST", full_url, data=json.dumps(payload), auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

                            if response.status_code == 200:
                                print("Tarjeta creada y enviada correctamente!")
                            else:
                                raise Exception("Error enviando tarjeta al dispositivo: {}".format(response.text))
                else:
                    raise Exception("Error enviando el usuario al dispositivo: {}".format(response.text))

            elif response_status == "OK" and not action == "pre_remove":

                subject_ids = list(filtered_horario_ids)
                plan_template_no_new = ','.join(map(str, subject_ids))

                plan_template_no = response_json['UserInfoSearch']['UserInfo'][0]['RightPlan'][0]['planTemplateNo']
                print(plan_template_no)
                print(plan_template_no_new)

                existing_set = set(plan_template_no.split(","))
                new_set = set(plan_template_no_new.split(","))

                combined_set = existing_set.union(new_set)

                plan_template_definitivo = ",".join(sorted(combined_set))

                print("Definitivo")

                print(plan_template_definitivo)

                if mockeo:
                    return

                base_url = "http://{}:{}".format(ip_seleccionada, GATEWAY_PORT)
                record_url = f"{URL_MODIFY_USER}?format=json"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

                data = {
                    "UserInfo": 
                        {
                            "employeeNo": str(instance.dni),
                            "name": str(instance.first_name + " " + instance.last_name),
                            "userType": instance.profile_type,
                            "gender": instance.gender,
                            "Valid": {
                                "enable": instance.is_active,
                                "beginTime": begin_time_str,
                                "endTime": end_time_str,
                                "timeType": instance.timeType
                            },
                            "doorRight": instance.doorRight,
                            "RightPlan": [
                                {
                                    "doorNo": instance.doorNo,
                                    "planTemplateNo": plan_template_definitivo
                                }
                            ],
                            "localUIRight": instance.is_staff,
                            "userVerifyMode": instance.userVerifyMode
                        }
                    }

                response = requests.put(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )


                if response.status_code == 200:
                    print("Usuario modificado y cargado por la API y CAMPO")
                else:
                    raise Exception("Failed to modify instance: {}".format(response.text))

            elif response_status == "OK" and action == "pre_remove":

                subject_ids = list(filtered_horario_ids)
                plan_template_no_new = ','.join(map(str, subject_ids))

                plan_template_no = response_json['UserInfoSearch']['UserInfo'][0]['RightPlan'][0]['planTemplateNo']
                print(plan_template_no)
                print(plan_template_no_new)

                existing_set = set(plan_template_no.split(","))
                new_set = set(plan_template_no_new.split(","))

                final_set = existing_set.difference(new_set)

                plan_template_definitivo = ",".join(sorted(final_set))

                print("Definitivo")

                print(plan_template_definitivo)

                if mockeo:
                    return

                base_url = "http://{}:{}".format(ip_seleccionada, GATEWAY_PORT)
                record_url = f"{URL_MODIFY_USER}?format=json"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

                data = {
                    "UserInfo": 
                        {
                            "employeeNo": str(instance.dni),
                            "name": str(instance.first_name + " " + instance.last_name),
                            "userType": instance.profile_type,
                            "gender": instance.gender,
                            "Valid": {
                                "enable": instance.is_active,
                                "beginTime": begin_time_str,
                                "endTime": end_time_str,
                                "timeType": instance.timeType
                            },
                            "doorRight": instance.doorRight,
                            "RightPlan": [
                                {
                                    "doorNo": instance.doorNo,
                                    "planTemplateNo": plan_template_definitivo
                                }
                            ],
                            "localUIRight": instance.is_staff,
                            "userVerifyMode": instance.userVerifyMode
                        }
                    }

                response = requests.put(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )


                if response.status_code == 200:
                    print("Usuario modificado y cargado por la API y CAMPO")
                else:
                    raise Exception("Failed to modify instance: {}".format(response.text))


# Señales que se activan después de agregar un dispositivo en la base de datos. 
# Crea, modifica o elimina la configuración en el directorio por lo que es necesario reiniciar el
# programa go2rtc para que los cambios sean efectuados.

@receiver(post_save, sender=Device)
def send_yaml_config(sender, instance, created, **kwargs):
    if created:
        ruta_archivo = 'go2rtc.yaml'

        with open(ruta_archivo, 'r') as archivo:
            contenido = yaml.safe_load(archivo)

        if not contenido['streams']:
            contenido['streams'] = {}

        if str(instance.device) not in contenido:
            contenido['streams'][str(instance.device)] = [
                f"rtsp://{instance.user}:{instance.password}@{instance.ip}:554/ISAPI/Streaming/Channels/101"
     #           f"isapi://admin:password@{instance.ip}:80/"
            ]

        with open(ruta_archivo, 'w') as archivo:
            yaml.dump(contenido, archivo)

        print("Contenido del archivo YAML agregado")

#corregida
@receiver(pre_save, sender=Device)
def modify_yaml_config(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Device.objects.get(pk=instance.pk)
        old_value = old_instance.device

        ruta_archivo = 'go2rtc.yaml'

        with open(ruta_archivo, 'r') as archivo:
            contenido = yaml.safe_load(archivo)

        if not contenido['streams']:
            contenido['streams'] = {}

        print(old_instance.device)
        print(instance.device)

        if str(old_instance.device) in contenido['streams']:
            del contenido['streams'][str(old_instance.device)]

            contenido['streams'][str(instance.device)] = [
                f"rtsp://{instance.user}:{instance.password}@{instance.ip}:554/ISAPI/Streaming/Channels/101"
     #           f"isapi://admin:password@{instance.ip}:80/"
            ]

        with open(ruta_archivo, 'w') as archivo:
            yaml.dump(contenido, archivo)

        print("Contenido del archivo YAML modificado")  



@receiver(post_delete, sender=Device)
def delete_yaml_config(sender, instance, **kwargs):
    ruta_archivo = 'go2rtc.yaml'

    with open(ruta_archivo, 'r') as archivo:
        contenido = yaml.safe_load(archivo)

    print(instance.device)
    if str(instance.device) in contenido['streams']:
        del contenido['streams'][str(instance.device)]

    with open(ruta_archivo, 'w') as archivo:
        yaml.dump(contenido, archivo)

    print("Contenido del archivo YAML eliminado")      

# Señal que se activa después de agregar de un usuario de la tabla UserProfile.
# Se envía un JSON dependiendo del condicional si se está creando o modificando.

#corregida, revisar
@receiver(post_save, sender=UserProfileStudent)
def send_user_data(sender, instance, created, **kwargs):
    if created:
        if mockeo:
            return

        if not instance.subject:

            subject_schedules = instance.subject.all()
            ips = []
            door_ports = []
            users = []
            passwords = []

            for subject_schedule in subject_schedules:
                device = subject_schedule.device
                if device and device.is_active:  
                    ips.append(device.ip)
                    door_ports.append(device.door_port)
                    users.append(device.user)
                    passwords.append(device.password)

            print(ips)

            for ip_address, GATEWAY_PORT, GATEWAY_USER, GATEWAY_PASSWORD in zip(ips, door_ports, users, passwords):

                base_url = f'http://{ip_address}:{GATEWAY_PORT}'
                record_url = f"{URL_RECORD_USER}?format=json"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

                data = {
                    "UserInfo": 
                        {
                            "employeeNo": str(instance.dni),
                            "name": str(instance.first_name + " " + instance.last_name),
                            "userType": instance.profile_type,
                            "gender": instance.gender,
                            "Valid": {
                                "enable": instance.is_active,
                                "beginTime": begin_time_str,
                                "endTime": end_time_str,
                                "timeType": instance.timeType
                            },
                            "doorRight": instance.doorRight,
                            "RightPlan": [
                                {
                                    "doorNo": instance.doorNo,
                                }
                            ],
                            "localUIRight": instance.is_staff,
                            "userVerifyMode": instance.userVerifyMode
                        }
                    }

                print("Probemos para ver device: ")
                print(instance.subject)

                response = requests.post(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )

                if response.status_code == 200:
                        print("Usuario creado y cargado con la API (sin horario) 1")
                else:
                    raise Exception("Error enviando el usuario al dispositivo: {}".format(response.text))

    else:
        if mockeo:
            return

            
        previous_instance = UserProfileStudent.objects.get(pk=instance.pk)

        previous_subject_ids = set(previous_instance.subject.values_list('pk', flat=True))
        current_subject_ids = set(instance.subject.values_list('pk', flat=True))

        if previous_subject_ids == current_subject_ids:

            subject_schedules = instance.subject.all()
            device_ips = list(subject_schedules.values_list('device__ip', flat=True).distinct())

            print("Probando:")
            print(device_ips)
            print("Cantidad de valores:", len(device_ips))

            for i in range(len(device_ips)):

                print("Iteración:", i)
                ip_seleccionada = device_ips[i]
                print(ip_seleccionada)

                base_url = "http://{}:{}".format(ip_seleccionada, GATEWAY_PORT)
                record_url = f"{URL_MODIFY_USER}?format=json"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
                end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

                data = {
                    "UserInfo": 
                        {
                            "employeeNo": str(instance.dni),
                            "name": str(instance.first_name + " " + instance.last_name),
                            "userType": instance.profile_type,
                            "gender": instance.gender,
                            "Valid": {
                                "enable": instance.is_active,
                                "beginTime": begin_time_str,
                                "endTime": end_time_str,
                                "timeType": instance.timeType
                            },
                            "doorRight": instance.doorRight,
                            "RightPlan": [
                                {
                                    "doorNo": instance.doorNo,
                                }
                            ],
                            "localUIRight": instance.is_staff,
                            "userVerifyMode": instance.userVerifyMode
                        }
                    }

                response = requests.put(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )

                if response.status_code == 200:
                    print(response.text)
                    modificado = True 
                else:
                    modificado = False
                    mensaje1 = response.text
                    print("Mensaje 1")
                    print(mensaje1)

                    
            if not instance.fileImage:

                subject_schedules = instance.subject.all()
                ips = []
                door_ports = []
                users = []
                passwords = []

                for subject_schedule in subject_schedules:
                    device = subject_schedule.device
                    if device and device.is_active:  
                        ips.append(device.ip)
                        door_ports.append(device.door_port)
                        users.append(device.user)
                        passwords.append(device.password)

                print(ips)

                for ip_address, door_port, user, password in zip(ips, door_ports, users, passwords):
                    base_url = f'http://{ip_address}:{door_port}'
                    record_url = f"{URL_RECORD_IMAGE}?format=json"
                    full_url = f"{base_url}{record_url}"

                    data = {
                        "faceLibType": "blackFD",
                        "FDID": "1",
                        "FPID": str(instance.dni),
                        "deleteFP": True
                    }

                    print("Acá es 4")

                    print(data)


                    response = requests.put(full_url, data=json.dumps(data), auth=HTTPDigestAuth(user, password))


                    if response.status_code == 200:
                        imagen_borrada = True
                    else:
                        imagen_borrada = False
                        print("Mensaje 2")
                        mensaje2 = response.text

                    if response.status_code == 200:
                        print("Usuario modificado y cargado por la API (sin horario) 2")
                    else:
                        print(mensaje2)
                        raise Exception("Failed to modify instance: {}".format(response.text))

# Señal que se activa después de agregar un usuario en la tabla UserProfile. A diferencia
# de la señal anterior, se utiliza para sumar la imagen si es que se adjuntó alguna.

#corregida
@receiver(post_save, sender=UserProfileStudent)
def send_image_data(sender, created, instance, **kwargs):
        if created:
            return 
        else:
            original_instance = sender.objects.get(pk=instance.pk)
            if instance.fileImage != original_instance.fileImage:
                subject_schedules = instance.subject.all()
                ips = []
                door_ports = []
                users = []
                passwords = []

                for subject_schedule in subject_schedules:
                    device = subject_schedule.device
                    if device and device.is_active:  
                        ips.append(device.ip)
                        door_ports.append(device.door_port)
                        users.append(device.user)
                        passwords.append(device.password)

                print(ips)

                for ip_address, door_port, user, password in zip(ips, door_ports, users,passwords):
                    
                    GATEWAY_PORT = door_port
                    GATEWAY_USER = user
                    GATEWAY_PASSWORD = password

                    base_url = f'http://{ip_address}:{GATEWAY_PORT}'
                    record_url = f"{URL_RECORD_IMAGE}?format=json"
                    full_url = f"{base_url}{record_url}"

                    data = {
                        "faceLibType": "blackFD",
                        "FDID": "1",
                        "FPID": str(instance.dni),
                        "deleteFP": True
                    }

                    print("Acá es 2")

                    print(data)


                    response = requests.request("PUT", full_url, data=json.dumps(data), auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))


                    if response.status_code == 200:
                        print("Image deleted succesfully and sent to API!")
                        print("User deleted successfully and data sent to API!")
                    else:
                        raise Exception("Error enviando la imagen al dispositivo: {}".format(response.text))

            if instance.fileImage:

                subject_schedules = instance.subject.all()
                ips = []

                for subject_schedule in subject_schedules:
                    device = subject_schedule.device
                    if device and device.is_active:  
                        ips.append(device.ip)

                print(ips)

                for ip_address in ips:
                    base_url = f'http://{ip_address}:{GATEWAY_PORT}'
                    record_url = f"{URL_RECORD_IMAGE}?format=json"
                    full_url = f"{base_url}{record_url}"

                    print("Acá es 3")
                    

                    payload = {
                        "FaceDataRecord": ('', '{"faceLibType":"blackFD","FDID":"1","FPID":"' + str(instance.dni) + '"}', 'application/json'),
                        "img": ('Imagen', open(str(instance.fileImage), 'rb'), 'image/jpeg')
                    }

                    print(payload)

                    response = requests.put(full_url, files=payload, auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

                    if response.status_code == 200:
                        print("Image created succesfully and sent to API!")
                        print("User created successfully and data sent to API!")
                    else:
                        raise Exception("Error enviando la imagen al dispositivo: {}".format(response.text))

# Se activa luego de cargar un horario de materia en la tabla SubjectSchedule.
# Se sube el JSON al dispositivo respectivo tanto como para el horario de la materia
# como el plan de horario relacionado.

@receiver(post_save, sender=UserProfile)
def enviar_tarjeta(sender, created, instance, **kwargs):

    GATEWAY_PORT = instance.device.door_port
    GATEWAY_USER = instance.device.user
    GATEWAY_PASSWORD = instance.device.password

    if mockeo:
        return

    if created:
        return 

    if instance.card:
        subject_schedules = instance.subject.all()
        ips = []

        for subject_schedule in subject_schedules:
            device = subject_schedule.device
            if device and device.is_active:  
                ips.append(device.ip)

        for ip_address in ips:

            base_url = f'http://{ip_address}:{GATEWAY_PORT}'
            record_url = f"{URL_DELETE_CARD}?format=json"
            full_url = f"{base_url}{record_url}"

            print("Se borra la tarjeta")

            payload = {         
                "CardInfoDelCond" : {
                    "EmployeeNoList" : [{
                    "employeeNo": str(instance.user_device_id)
                    }]
                }
            }

            response = requests.request("PUT", full_url, data=json.dumps(payload), auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

            if response.status_code == 200:
                print("Tarjeta borrada para ser reemplazada")
                base_url = f'http://{ip_address}:{GATEWAY_PORT}'
                record_url = f"{URL_ADD_CARD}?format=json"
                full_url = f"{base_url}{record_url}"

                print("Acá se reemplaza la tarjeta")
                payload = { 
                    "CardInfo": {
                        "employeeNo": str(instance.user_device_id),
                        "cardNo": str(instance.card),
                        "cardType": str(instance.cardType)
                    }
                }
                
#corregida
@receiver(pre_save, sender=SubjectSchedule)
def enviar_horario(sender, instance, **kwargs):
    if mockeo:
        return

    ip = instance.device.ip
    GATEWAY_PORT = instance.device.door_port
    GATEWAY_USER = instance.device.user
    GATEWAY_PASSWORD = instance.device.password

    subject_schedules = []
    id_mapping = {}

    unique_days = list(set(instance.day))

    for day in unique_days:
        if day not in id_mapping:
            id_mapping[day] = 1
        else:
            id_mapping[day] += 1

        subject_data = {
            "week": day,
            "id": id_mapping[day],
            "enable": True,
            "TimeSegment": {
                "beginTime": str(instance.begin_time),
                "endTime": str(instance.end_time)
            }
        }
        subject_schedules.append(subject_data)

    subject_schedules.sort(key=lambda x: x['week'])

    json_data = {
        "UserRightWeekPlanCfg": {
            "enable": True,
            "WeekPlanCfg": subject_schedules
        }
    }

    json_str = json.dumps(json_data, indent=4)

    print(json_str)
    print((instance.horario_id + 1))

    base_url = "http://{}:{}".format(ip, GATEWAY_PORT)
    record_url = f"/ISAPI/AccessControl/UserRightWeekPlanCfg/{(instance.horario_id + 1)}?format=json"
    full_url = f"{base_url}{record_url}"
    headers = {"Content-type": "application/json"}


    response = requests.put(
        full_url,
        headers=headers,
        data=json_str,
        auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
    )

    if response.status_code == 200:
        print("Se registró correctamente el horario!")

        base_url = "http://{}:{}".format(ip, GATEWAY_PORT)
        record_url = f"/ISAPI/AccessControl/UserRightPlanTemplate/{(instance.horario_id + 1)}?format=json"
        full_url = f"{base_url}{record_url}"
        headers = {"Content-type": "application/json"}


        coded_value = str(instance.career_subject_year)
        decoded_value = unidecode(coded_value)
        subject = decoded_value.split(" - ")[1]

        json_data = {
            "UserRightPlanTemplate":{
                "enable": True,
                "templateName": subject,
                "weekPlanNo": (instance.horario_id + 1),
                "holidayGroupNo": ""
            }
        }

        json_str = json.dumps(json_data, indent=4)
        print(json_str)

        response = requests.put(
            full_url,
            headers=headers,
            data=json_str,
            auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
        )
        if response.status_code == 200:
            print("Se registró correctamente el template del horario!!")
        else:
            raise Exception("Error registrando el template de horario: {}".format(response.text))
    else:
        raise Exception("Error registrando el horario: {}".format(response.text))
    

#corregida
@receiver(pre_delete, sender=UserProfileStudent)
def delete_user_data(sender, instance, **kwargs):
    if mockeo:
            return

    pre_delete.disconnect(delete_user_data, sender=UserProfileStudent)
    
    subject_schedules = instance.subject.all()
    ips = []
    door_ports = []
    users = []
    passwords = []

    for subject_schedule in subject_schedules:
        device = subject_schedule.device
        if device and device.is_active:  
            ips.append(device.ip)
            door_ports.append(device.door_port)
            users.append(device.user)
            passwords.append(device.password)

    print(ips)
    print(door_ports)
    print(users)
    print(passwords)

    for ip_address, door_port, user, password in zip(ips, door_ports, users, passwords):
        GATEWAY_PORT = door_port
        GATEWAY_USER = user
        GATEWAY_PASSWORD = password

        base_url = f'http://{ip_address}:{GATEWAY_PORT}'

        print(base_url)

        record_url = f"{URL_DELETE_USER}?format=json"
        full_url = f"{base_url}{record_url}"
        headers = {"Content-type": "application/json"}

        data = {
            "UserInfoDetail": {
                "mode": "byEmployeeNo",
                "EmployeeNoList": [{"employeeNo": str(instance.dni)}],
            }
        }

        response = requests.put(
            full_url,
            headers=headers,
            data=json.dumps(data),
            auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
        )

        if response.status_code == 200:
            print("User deleted successfully!")
            instance.delete()
        else:
            print("Error: can't delete user")
            raise Exception("Failed to delete instance: {}".format(response.text))

        pre_delete.connect(delete_user_data, sender=UserProfileStudent)
    
# Función encargada de chequear que los tipos de usuarios por defecto estén creados en la aplicación.
# En caso de que no se encuentren creados se crean, si no, se obtienen y no se hace nada.

def create_default_usertypes():
    default_usertypes = ['Alumno', 'Mantenimiento']
    for usertype in default_usertypes:
        UserTypes.objects.get_or_create(user_type=usertype)

@receiver(post_migrate)
def post_migrate_receiver(sender, **kwargs):
    create_default_usertypes()

# Variable global que se utiliza para manejar la modificación de usuarios del tipo mantenimiento

modified = False

# Array que tiene los días de la semana, se utilizan en distintas señales y funciones

days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

# Función encargada de enviar los datos de los usuarios creados o modificados al dispositivo remoto

@receiver(post_save, sender=UserProfile)
def post_save_user_profile(sender, instance, created, **kwargs):
    global modified
    instance.last_updated = timezone.now()
    device = instance.device
    ip = device.ip
    door_port = device.door_port
    uuid = settings.DEVICE_UUID
    username = device.user
    password = device.get_password()
    auth = HTTPDigestAuth(username, password)
    headers = {'Content-Type': 'application/json'}
    if instance.is_active == 'Sí':
        is_active = True
    else:
        is_active = False
    if instance.is_staff == 'Sí':
        is_staff = True
    else:
        is_staff = False

    if created:
        if instance.user_type.user_type == 'Mantenimiento':
            return
        url = f"http://{ip}:{door_port}{URL_RECORD_USER}?format=json&devIndex={uuid}"
        #print(url)

        if instance.begin_time == None and instance.end_time == None:
            today = datetime.now()
            begin_time_str = today.strftime("%Y-%m-%dT%H:%M:%S")
            end_time = today + timedelta(days=365 * 10)
            end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
            data = {
            "UserInfo":
                {
                    "employeeNo": str(instance.dni),
                    "name": str(instance.first_name + " " + instance.last_name),
                    "userType": instance.profile_type,
                    "gender": instance.gender,
                    "Valid": {
                        "enable": is_active,
                        "beginTime": begin_time_str, 
                        "endTime": end_time_str
                    }, 
                    "localUIRight": is_staff
                }
            }
            print(data)
        else:
            begin_time_str = instance.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if instance.begin_time else None
            end_time_str = instance.end_time.strftime("%Y-%m-%dT%H:%M:%S") if instance.end_time else None
            data = {
            "UserInfo":
                {
                    "employeeNo": str(instance.dni),
                    "name": str(instance.first_name + " " + instance.last_name),
                    "userType": instance.profile_type,
                    "gender": instance.gender,
                    "Valid": {
                        "enable": is_active, 
                        "beginTime": begin_time_str,
                        "endTime": end_time_str,
                    }, 
                    "localUIRight": is_staff
                }
            }
            print(data)

        response = requests.post(url, data=json.dumps(data), headers=headers, auth=auth)
        if response.status_code == 200:
            print('Usuario agregado correctamente al dispositivo remoto.')
        else:
            print('Error al agregar el usuario al dispositivo remoto. Código de estado:', response.status_code)
            print('Respuesta del servidor:', response.text)
    else:
        if instance.user_type.user_type == 'Mantenimiento':
            modified = True
        else: 
            url = f"http://{ip}:{door_port}{URL_MODIFY_USER}?format=json&devIndex={uuid}"
            #print(url)
            if instance.begin_time == None and instance.end_time == None:
                today = datetime.now()
                begin_time_str = today.strftime("%Y-%m-%dT%H:%M:%S")
                end_time = today + timedelta(days=365 * 10)
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(instance.dni),
                        "name": str(instance.first_name + " " + instance.last_name),
                        "userType": instance.profile_type,
                        "gender": instance.gender,
                        "Valid": {
                            "enable": is_active, 
                            "beginTime": begin_time_str,
                            "endTime": end_time
                        }, 
                        "localUIRight": is_staff
                    }
                }
                print(data)
            else:
                begin_time_str = instance.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if instance.begin_time else None
                end_time_str = instance.end_time.strftime("%Y-%m-%dT%H:%M:%S") if instance.end_time else None
                data = {
                "UserInfo":
                    {
                        "employeeNo": str(instance.dni),
                        "name": str(instance.first_name + " " + instance.last_name),
                        "userType": instance.profile_type,
                        "gender": instance.gender,
                        "Valid": {
                            "enable": is_active, 
                            "beginTime": begin_time_str,
                            "endTime": end_time_str,
                        }, 
                        "localUIRight": is_staff
                    }
                }
                print(data)

            response = requests.put(url, data=json.dumps(data), headers=headers, auth=auth)
            if response.status_code == 200:
                print('Usuario modificado correctamente.')
            else:
                print('Error al modificar el usuario en el dispositivo remoto. Código de estado:', response.status_code)
                print('Respuesta del servidor:', response.text)

# Función encargada de enviar los datos de eliminación de usuarios
            
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
    #print(url)

    data = {
        "UserInfoDetail": {
            "mode": "byEmployeeNo",
            "EmployeeNoList": [{
                "employeeNo": str(instance.dni)
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

# Función encargada de registrar usuarios del tipo mantenimiento. Es similar a la anterior pero se 
# deben configurar los JSON para habilitar el usuario en ciertos horarios
        
@receiver(post_save, sender=UserProfileMaintenance)
def post_save_user_profile_maintenance(sender, instance, created,**kwargs):
    global modified
    global days
    id = instance.id + 64

    user_profile = instance.user_profile
    if user_profile.is_active == 'Sí':
        is_active = True
    else:
        is_active = False
    if user_profile.is_staff == 'Sí':
        is_staff = True
    else:
        is_staff = False
    
    device = user_profile.device
    ip = device.ip
    door_port = device.door_port
    uuid = settings.DEVICE_UUID
    username = device.user
    password = device.get_password()
    auth = HTTPDigestAuth(username, password)
    headers = {'Content-Type': 'application/json'}

    if created:
        if modified == True:
            modify_user_maintenence(instance, id)
            modified = False
        else:
            week_plan_cfg = [{
                'week': day.capitalize(),
                'id': 1,
                'enable': getattr(instance, day) == 'Sí',
                'TimeSegment': {
                    'beginTime': getattr(instance, f'{day}_time_begin').strftime("%H:%M:%S"),
                    'endTime': getattr(instance, f'{day}_time_end').strftime("%H:%M:%S")
                }
            } for day in days if getattr(instance, day) == 'Sí']
            
            data_1 = {
                "UserRightWeekPlanCfg": {
                    "planNo": str(id),
                    "enable": True,
                    "WeekPlanCfg": week_plan_cfg
                }
            }
            print(data_1)

            url_1 = f"http://{ip}:{door_port}{URL_UserRightWeekPlanCfg}{id}?format=json&devIndex={uuid}"
            #print(url_1)
            response_1 = requests.put(url_1, data=json.dumps(data_1), headers=headers, auth=auth)
            
            if response_1.status_code == 200:
                print('Plan semanal creado con éxito')
            else:
                print('Error crear al plan semanal. Código de estado:', response_1.status_code)
                print('Respuesta del servidor:', response_1.text)

            data_2 = {
                "UserRightPlanTemplate": {
                    "templateNo": str(id),
                    "enable": True,
                    "templateName": f"Usuario mantenimiento n° {id - 64}",
                    "weekPlanNo": id,
                    "holidayGroupNo": ""
                }
            }

            url_2 = f"http://{ip}:{door_port}{URL_UserRightPlanTemplate}{id}?format=json&devIndex={uuid}"
            #print(url_2)
            response_2 = requests.put(url_2, data=json.dumps(data_2), headers=headers, auth=auth)
            
            if response_2.status_code == 200:
                print('Template de horarios creado con éxito')
            else:
                print('Error al crear el template de horarios. Código de estado:', response_2.status_code)
                print('Respuesta del servidor:', response_2.text)

            url_3 = f"http://{ip}:{door_port}{URL_RECORD_USER}?format=json&devIndex={uuid}"
            #print(url_3)

            if user_profile.begin_time == None and user_profile.end_time == None:
                today = datetime.now()
                begin_time_str = today.strftime("%Y-%m-%dT%H:%M:%S")
                end_time = today + timedelta(days=365 * 10)
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
                data_3 = {
                "UserInfo":
                    {
                        "employeeNo": str(user_profile.dni),
                        "name": str(user_profile.first_name + " " + user_profile.last_name),
                        "userType": user_profile.profile_type,
                        "gender": user_profile.gender,
                        "Valid": {
                            "enable": is_active,
                            "beginTime": begin_time_str,
                            "endTime": end_time_str
                        }, 
                        "doorRight": "1",
                        "RightPlan" : [{
                            "doorNo": 1,
                            "planTemplateNo": str(id)
                        }],
                        "localUIRight": is_staff
                    }
                }
                print(data_3)
            else:
                begin_time_str = user_profile.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if user_profile.begin_time else None
                end_time_str = user_profile.end_time.strftime("%Y-%m-%dT%H:%M:%S") if user_profile.end_time else None
                data_3 = {
                "UserInfo":
                    {
                        "employeeNo": str(user_profile.dni),
                        "name": str(user_profile.first_name + " " + user_profile.last_name),
                        "userType": user_profile.profile_type,
                        "gender": user_profile.gender,
                        "Valid": {
                            "enable": is_active, 
                            "beginTime": begin_time_str,
                            "endTime": end_time_str,
                        },
                        "doorRight": "1",
                        "RightPlan" : [{
                            "doorNo": 1,
                            "planTemplateNo": str(id)
                        }], 
                        "localUIRight": is_staff
                    }
                }
                print(data_3)

            response_3 = requests.post(url_3, data=json.dumps(data_3), headers=headers, auth=auth)
            if response_3.status_code == 200:
                print('Usuario agregado correctamente al dispositivo remoto.')
            else:
                print('Error al agregar el usuario al dispositivo remoto. Código de estado:', response_3.status_code)
                print('Respuesta del servidor:', response_3.text)
    else:
        modify_user_maintenence(instance, id)

# Función encargada de la modificación de los usurios del tipo mantenimiento. Debido a que se tenía que
# utilizar más de una vez se decició empaquetar el código en una función y llamarla cuando sea necesario.

def modify_user_maintenence(instance, id):
    global days

    user_profile = instance.user_profile
    if user_profile.is_active == 'Sí':
        is_active = True
    else:
        is_active = False
    if user_profile.is_staff == 'Sí':
        is_staff = True
    else:
        is_staff = False        

    device = user_profile.device
    ip = device.ip
    door_port = device.door_port
    uuid = settings.DEVICE_UUID
    username = device.user
    password = device.get_password()
    auth = HTTPDigestAuth(username, password)
    headers = {'Content-Type': 'application/json'}
    week_plan_cfg = [{
            'week': day.capitalize(),
            'id': 1,
            'enable': getattr(instance, day) == 'Sí',
            'TimeSegment': {
                'beginTime': getattr(instance, f'{day}_time_begin').strftime("%H:%M:%S"),
                'endTime': getattr(instance, f'{day}_time_end').strftime("%H:%M:%S")
            }
        } for day in days if getattr(instance, day) == 'Sí']
        
    data_1 = {
        "UserRightWeekPlanCfg": {
            "planNo": str(id),
            "enable": True,
            "WeekPlanCfg": week_plan_cfg
        }
    }
    print(data_1)

    url_1 = f"http://{ip}:{door_port}{URL_UserRightWeekPlanCfg}{id}?format=json&devIndex={uuid}"
    #print(url_1)
    response_1 = requests.put(url_1, data=json.dumps(data_1), headers=headers, auth=auth)
    
    if response_1.status_code == 200:
        print('Plan semanal creado con éxito')
    else:
        print('Error crear plan semanal. Código de estado:', response_1.status_code)
        print('Respuesta del servidor:', response_1.text)

    data_2 = {
        "UserRightPlanTemplate": {
            "templateNo": str(id),
            "enable": True,
            "templateName": f"Usuario mantenimiento n° {id - 64}",
            "weekPlanNo": id,
            "holidayGroupNo": ""
        }
    }
    print(data_2)

    url_2 = f"http://{ip}:{door_port}{URL_UserRightPlanTemplate}{id}?format=json&devIndex={uuid}"
    #print(url_2)
    response_2 = requests.put(url_2, data=json.dumps(data_2), headers=headers, auth=auth)
    
    if response_2.status_code == 200:
        print('Template de horarios creado con éxito')
    else:
        print('Error crear el template de horarios. Código de estado:', response_2.status_code)
        print('Respuesta del servidor:', response_2.text)

    url_3 = f"http://{ip}:{door_port}{URL_MODIFY_USER}?format=json&devIndex={uuid}"
    #print(url_3)
    if user_profile.begin_time == None and user_profile.end_time == None:
        today = datetime.now()
        begin_time_str = today.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = today + timedelta(days=365 * 10)
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        data_3 = {
        "UserInfo":
            {
                "employeeNo": str(user_profile.dni),
                "name": str(user_profile.first_name + " " + user_profile.last_name),
                "userType": user_profile.profile_type,
                "gender": user_profile.gender,
                "Valid": {
                    "enable": is_active, 
                    "beginTime": begin_time_str,
                    "endTime": end_time_str
                }, 
                "doorRight": "1",
                "RightPlan" : [{
                    "doorNo": 1,
                    "planTemplateNo": str(id)
                }],
                "localUIRight": is_staff
            }
        }
        print(data_3)
    else:
        begin_time_str = user_profile.begin_time.strftime("%Y-%m-%dT%H:%M:%S") if user_profile.begin_time else None
        end_time_str = user_profile.end_time.strftime("%Y-%m-%dT%H:%M:%S") if user_profile.end_time else None
        data_3 = {
        "UserInfo":
            {
                "employeeNo": str(user_profile.dni),
                "name": str(user_profile.first_name + " " + user_profile.last_name),
                "userType": user_profile.profile_type,
                "gender": user_profile.gender,
                "Valid": {
                    "enable": is_active, 
                    "beginTime": begin_time_str,
                    "endTime": end_time_str,
                },
                "doorRight": "1",
                "RightPlan" : [{
                    "doorNo": 1,
                    "planTemplateNo": str(id)
                }], 
                "localUIRight": is_staff
            }
        }
        print(data_3)

    response_3 = requests.put(url_3, data=json.dumps(data_3), headers=headers, auth=auth)
    if response_3.status_code == 200:
        print('Usuario modificado correctamente.')
    else:
        print('Error al modificar el usuario en el dispositivo remoto. Código de estado:', response_3.status_code)
        print('Respuesta del servidor:', response_3.text)

@receiver(pre_delete, sender=UserProfileMaintenance)
def pre_delete_user_profile_maintenance(sender, instance,**kwargs):
    global days
    id = instance.id + 64
    
    user_profile = instance.user_profile
    device = user_profile.device
    ip = device.ip
    door_port = device.door_port
    uuid = settings.DEVICE_UUID
    username = device.user
    password = device.get_password()
    auth = HTTPDigestAuth(username, password)
    headers = {'Content-Type': 'application/json'}

    week_plan_cfg = [{
        'week': day.capitalize(),
        'id': 1,
        'enable': False,
        'TimeSegment': {
            'beginTime': "00:00:00",
            'endTime': "00:00:00"
        }
    } for day in days if getattr(instance, day) == 'Sí']

    data_1 = {
        "UserRightWeekPlanCfg": {
            "planNo": str(id),
            "enable": False,
            "WeekPlanCfg": week_plan_cfg
        }
    }

    url_1 = f"http://{ip}:{door_port}{URL_UserRightWeekPlanCfg}{id}?format=json&devIndex={uuid}"
    #print(url_1)
    response_1 = requests.put(url_1, data=json.dumps(data_1), headers=headers, auth=auth)
    
    if response_1.status_code == 200:
        print('Plan semanal limpiado con éxito')
    else:
        print('Error al limpiar plan semanal. Código de estado:', response_1.status_code)
        print('Respuesta del servidor:', response_1.text)

    data_2 = {
                "UserRightPlanTemplate": {
                    "templateNo": str(id),
                    "enable": False,
                    "templateName": "",
                    "weekPlanNo": id,
                    "holidayGroupNo": ""
                }
            }

    url_2 = f"http://{ip}:{door_port}{URL_UserRightPlanTemplate}{id}?format=json&devIndex={uuid}"
    #print(url_2)
    response_2 = requests.put(url_2, data=json.dumps(data_2), headers=headers, auth=auth)
    
    if response_2.status_code == 200:
        print('Template de horarios limpiado con éxito')
    else:
        print('Error al limpiar el template de horarios. Código de estado:', response_2.status_code)
        print('Respuesta del servidor:', response_2.text)