from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
import requests
import json, base64
from datetime import datetime

from user_profile_api.middleware import specific_page_loaded

from user_profile_api.urls_services import (
    URL_RECORD_USER,
    URL_DELETE_USER,
    URL_SEARCH_USER,
    URL_MODIFY_USER,
    URL_RECORD_CARD,
    URL_DELETE_CARD,
    URL_COUNT_USER,
    URL_RECORD_IMAGE,
)
from users_admin.settings import BASE_URL, DEVICE_UUID, GATEWAY_USER, GATEWAY_PASSWORD
from requests.auth import HTTPDigestAuth
from user_profile_api.models import UserProfile
from user_profile_api.services import get_default_user_device_id

mockeo = False

@receiver(pre_save, sender=UserProfile)
def send_user_data(sender, instance, **kwargs):
    if instance.pk is None:
        if mockeo:
            return

        base_url = BASE_URL
        record_url = f"{URL_RECORD_USER}?format=json&devIndex={DEVICE_UUID}"
        full_url = f"{base_url}{record_url}"
        headers = {"Content-type": "application/json"}

        begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
        end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

        data = {
            "UserInfo": 
                {
                    "employeeNo": str(instance.user_device_id),
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
                            "planTemplateNo": instance.planTemplateNo
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
            if instance.card:
                base_url = BASE_URL
                record_url = f"{URL_RECORD_CARD}?format=json&devIndex={DEVICE_UUID}"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                data = {
                    "CardInfo": {
                        "employeeNo": str(instance.user_device_id),
                        "cardNo": instance.card,
                        "cardType": instance.cardType
                        }
                    }

                response = requests.post(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )

                if response.status_code == 200:
                    print("Card created succesfully and sent to API!")
                    print("User created successfully and data sent to API!")
                else:
                    raise Exception("Error enviando la tarjeta al dispositivo: {}".format(response.text))

            else:
                print("User created successfully and data sent to API!")
        else:
            raise Exception("Error enviando el usuario al dispositivo: {}".format(response.text))

    else:
        base_url = BASE_URL
        record_url = f"{URL_MODIFY_USER}?format=json&devIndex={DEVICE_UUID}"
        full_url = f"{base_url}{record_url}"
        headers = {"Content-type": "application/json"}

        begin_time_str = instance.beginTime.strftime("%Y-%m-%dT%H:%M:%S")
        end_time_str = instance.endTime.strftime("%Y-%m-%dT%H:%M:%S")

        data = {
            "UserInfo": 
                {
                    "employeeNo": str(instance.user_device_id),
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
                            "planTemplateNo": instance.planTemplateNo
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
            original_instance = sender.objects.get(pk=instance.pk)

            if instance.card != original_instance.card:
                base_url = BASE_URL
                record_url = f"{URL_DELETE_CARD}?format=json&devIndex={DEVICE_UUID}"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                data = ({
                        "CardInfoDelCond": {
                            "CardNoList": [
                                {
                                    "cardNo": original_instance.card
                                }
                            ]
                        }
                    })

                response = requests.put(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )

                record_url = f"{URL_RECORD_CARD}?format=json&devIndex={DEVICE_UUID}"
                full_url = f"{base_url}{record_url}"
                headers = {"Content-type": "application/json"}

                data = (
                    {
                        "CardInfo": {
                            "employeeNo": str(instance.user_device_id),
                            "cardNo": instance.card,
                            "cardType": instance.cardType
                        }
                    }
                )

                response = requests.post(
                    full_url,
                    headers=headers,
                    data=json.dumps(data),
                    auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD),
                )
                

                if response.status_code == 200:
                    print("Card modified succesfully and sent to API!")
                    print("User modified successfully and data sent to API!")
                else:
                    raise Exception("Error modificando la tarjeta: {}".format(response.text))
            else:
                print("User modified successfully and data sent to API!")
        else:
            raise Exception("Failed to modify instance: {}".format(response.text))


@receiver(post_save, sender=UserProfile)
def send_image_data(sender, created, instance, **kwargs):
    if created:
        if mockeo:
            return

        if instance.fileImage:
            base_url = BASE_URL
            record_url = f"{URL_RECORD_IMAGE}?format=json&devIndex={DEVICE_UUID}"
            full_url = f"{base_url}{record_url}"
                
            payload = {
                "data": "{\"faceLibType\":\"blackFD\",\"FDID\":\"1\",\"FPID\":\"" + str(instance.user_device_id) + "\"}"
            }

            files=[('image',('Imagen',open(str(instance.fileImage),'rb'),'image/jpeg'))]

            headers = {}

            response = requests.request("PUT", full_url, headers=headers, data=payload, files=files, auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

            if response.status_code == 200:
                print("Image created succesfully and sent to API!")
                print("User created successfully and data sent to API!")
            else:
                print("Error sending image to API")
                instance.delete()
    else:

        original_instance = sender.objects.get(pk=instance.pk)
        if instance.fileImage != original_instance.fileImage:
            base_url = BASE_URL
            record_url = f"{URL_RECORD_IMAGE}?format=json&devIndex={DEVICE_UUID}"
            full_url = f"{base_url}{record_url}"

            payload = {"data": '{ "faceLibType": "blackFD", "FDID": "1", "FPID": "2", "deleteFP": true }'}

            files=[('image',('Imagen',open(str(instance.fileImage),'rb'),'image/jpeg'))]

            headers = {}

            response = requests.request("PUT", full_url, headers=headers, data=payload, files=files, auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))


            if response.status_code == 200:
                print("Image deleted succesfully and sent to API!")
                print("User deleted successfully and data sent to API!")
            else:
                raise Exception("Error enviando la imagen al dispositivo: {}".format(response.text))

        if instance.fileImage:
            base_url = BASE_URL
            record_url = f"{URL_RECORD_IMAGE}?format=json&devIndex={DEVICE_UUID}"
            full_url = f"{base_url}{record_url}"
                
            payload = {
                "data": "{\"faceLibType\":\"blackFD\",\"FDID\":\"1\",\"FPID\":\"" + str(instance.user_device_id) + "\"}"
            }

            files=[('image',('Imagen',open(str(instance.fileImage),'rb'),'image/jpeg'))]

            headers = {}

            response = requests.request("PUT", full_url, headers=headers, data=payload, files=files, auth=HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))

            if response.status_code == 200:
                print("Image modified succesfully and sent to API!")
                print("User modified successfully and data sent to API!")
            else:
                raise Exception("Error modificando la imagen: {}".format(response.text))



@receiver(pre_delete, sender=UserProfile)
def delete_user_data(sender, instance, **kwargs):
    if mockeo:
            return

    pre_delete.disconnect(delete_user_data, sender=UserProfile)
    base_url = BASE_URL

    record_url = f"{URL_DELETE_USER}?format=json&devIndex={DEVICE_UUID}"
    full_url = f"{base_url}{record_url}"
    headers = {"Content-type": "application/json"}

    data = {
        "UserInfoDetail": {
            "mode": "byEmployeeNo",
            "EmployeeNoList": [{"employeeNo": str(instance.user_device_id)}],
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

    pre_delete.connect(delete_user_data, sender=UserProfile)

