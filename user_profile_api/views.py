from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.http import StreamingHttpResponse
from django.http import HttpResponse
from django.views.decorators.http import condition
import cv2
import imutils
import xml.etree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import requires_csrf_token
import requests
from django.shortcuts import render
from users_admin.settings import BASE_URL, DEVICE_UUID, GATEWAY_USER, GATEWAY_PASSWORD, GATEWAY_IP2, GATEWAY_IP, GATEWAY_RTSP, GATEWAY_PORT
from user_profile_api.urls_services import (
    URL_STREAM_101,
    URL_DOOR_1,
    URL_SEARCH_USER,
    URL_AcsEvent,
)
import datetime
import json, base64
from django.http import JsonResponse
import hashlib

rtsp_url = f"rtsp://{GATEWAY_USER}:{GATEWAY_PASSWORD}@{GATEWAY_IP2}:{GATEWAY_RTSP}{URL_STREAM_101}"
base_url = BASE_URL
door_url = f"{URL_DOOR_1}?format=xml&devIndex={DEVICE_UUID}"
full_url = f"{base_url}{door_url}"

def add_timestamp(frame):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame

def gen_frames():
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = imutils.resize(frame, width=640)
            frame = add_timestamp(frame)  
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


def video(request):
    return render(request, "custom/video/video.html")


def video_open_door(request):
    url = full_url
    payload = "<RemoteControlDoor xmlns=\"http://www.isapi.org/ver20/XMLSchema\" version=\"2.0\"><cmd>open</cmd></RemoteControlDoor>"
    headers = {
        'Content-Type': 'application/xml'
    }
    response = requests.put(url, headers=headers, data=payload, auth=requests.auth.HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))
    return HttpResponse('')


def get_users(request):
    base_url = BASE_URL
    record_url = f"{URL_SEARCH_USER}?format=json&devIndex={DEVICE_UUID}"
    full_url = f"{base_url}{record_url}"
    payload = json.dumps({
        "UserInfoSearchCond": {
        "searchID": "0",
        "searchResultPosition": 0,
        "maxResults": 1500
        }
        })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.post(full_url, headers=headers, data=payload, auth=requests.auth.HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))
    users = response.json()
    return JsonResponse({'users': users['UserInfoSearch']['UserInfo']})

def show_users(request):
    return render(request, "custom/show_users/show_users.html")

class GetEventsView(TemplateView):
    template_name = 'custom/show_events/show_events.html'

    def post(self, request, *args, **kwargs):
        base_url = BASE_URL
        record_url = f"{URL_AcsEvent}?format=json&devIndex={DEVICE_UUID}"
        full_url = f"{base_url}{record_url}"

        usuario = request.POST.get('usuario')
        grupoevento = request.POST.get('grupoevento')
        tipoevento = request.POST.get('tipoevento')
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')

        payload = {
            "AcsEventCond": {
                "searchID": "1",
                "searchResultPosition": 0,
                "maxResults": 500,
                "major": int(grupoevento),
                "minor": int(tipoevento),
                "startTime": desde,
                "endTime": hasta,
                "employeeNoString": "",
                "currentVerifyMode": ""
            }
        }

        headers = {
        'Content-Type': 'application/json'
        }

        payload_json = json.dumps(payload)
        print(payload_json)
        response = requests.post(full_url, headers=headers, data=payload_json, auth=requests.auth.HTTPDigestAuth(GATEWAY_USER, GATEWAY_PASSWORD))
        events = response.json()
        print(response.text)
        return JsonResponse({'events': events['AcsEvent']['InfoList']})



def show_events(request):
    return render(request, "custom/show_events/show_events.html")


