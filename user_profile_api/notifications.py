from django.core.mail import send_mail
import requests

def send_email():
  subject = 'Alerta ingreso'
  message = 'Un usuario no autorizado ha intentado ingresar'
  from_email = 'ic3unraf@gmail.com'
  recipient_list = ['ic3unraf@gmail.com']

  send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def send_telegram(): 
  bot_token = '6880127774:AAHPAYLgObat0VZE3TbIOOwDb2Wc6rDN2PY'
  chat_id = '6190641852'
  mensaje = "Un usuario no autorizado ha intentado ingresar"

  url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
  data = {'chat_id': chat_id, 'text': mensaje}

  requests.post(url, data=data)