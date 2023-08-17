from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

DEVICES = (('1', 'Device 1'),
           ('2', 'Device 2'),
           ('3', 'Device 3'))

CARDS = (('normalCard', 'Normal'),
         ('patrolCard', 'Mantenimiento'),
         ('hijackCard', 'Hijack'),
         ('superCard', 'Super'),
         ('dismissingCard', 'Destituir'),
         ('emergencyCard', 'Emergencia'))

PROFILETYPE = (('normal', 'Normal'),
               ('visitor', 'Visitante'),
               ('blackList', 'Bloqueado'))

SUBJECTS = (('análisis matematico', 'Análisis matemático'),
            ('física', 'Física'),
            ('química', 'Química'))

CAREERS = (('computer engineering', 'Computer Engineering'),
           ('mechatronics', 'Mechatronics'),
           ('bioinformatics', 'Bioinformatics'))

GENDER = (('male', 'Hombre'),
          ('female', 'Mujer'),
          ('unknown', 'Sin especificar'))

ROOMS = (('1', 'Room 1'),
         ('2', 'Room 2'),
         ('3', 'Room 3'))

HOURS = (('8', '8:00'),
         ('9', '9:00'),
         ('10', '10:00'),
         ('11', '11:00'),
         ('12', '12:00'),
         ('13', '13:00'),
         ('14', '14:00'),
         ('15', '15:00'),
         ('16', '16:00'),
         ('17', '17:00'),
         ('18', '18:00'),
         ('19', '19:00'),
         ('20', '20:00'),
         ('21', '21:00'),
         ('22', '22:00'),
         ('23', '23:00'))

VERIFYMODE = (('cardOrFace', 'Tarjeta o cara'),
              ('cardOrfaceOrPw', 'Tarjeta, cara o clave'),
              ('cardOrPw', 'Tarjeta o clave'),
              ('card', 'Tarjeta'),
              ('cardOrFace', 'Cara o clave'),
              ('face', 'Cara'))


class UserProfile(models.Model):
    user_device_id = models.IntegerField(unique=True, blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    userVerifyMode = models.CharField(max_length=30, choices=VERIFYMODE, blank=True)
    doorRight = models.CharField(max_length=100)
    doorNo = models.CharField(max_length=100)
    planTemplateNo = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_type = models.CharField(max_length=10, choices=PROFILETYPE)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    last_updated = models.DateTimeField(editable=False, default=timezone.now)
    dni = models.CharField(max_length=100, unique=True, null=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    emergency_phone = models.CharField(max_length=100, null=True)
    beginTime = models.DateTimeField(editable=True)
    endTime = models.DateTimeField(editable=True)
    fileImage = models.FileField(upload_to='user_profile_api/images/', blank=True)
    card = models.CharField(max_length=20, blank=True)
    cardType = models.CharField(max_length=20, blank=True, choices=CARDS)
    timeType = models.CharField(max_length=10, default='local')
    

    def __str__(self):
        text = "{0} {1} ({2} {3})"
        return text.format(self.first_name, self.last_name, self.dni, self.user_device_id)

    USERNAME_FIELD = 'email'


class Device(models.Model):
    device = models.CharField(max_length=50)
    date_purchased = models.DateField(editable=True)
    is_active = models.BooleanField(default=False)
    is_synchronized = models.BooleanField(default=True)
    users = models.ManyToManyField(UserProfile, related_name='devices', blank=True)


    def __str__(self):
        text = "{0}"
        return text.format(self.device)





class Room(models.Model):
    room = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)

    def __str__(self):
        text = "{0} ({1})"
        return text.format(self.room, self.location)

class Career(models.Model):
    name_career = models.CharField(max_length=100)

    def __str__(self):
        return self.name_career


class Subject(models.Model):
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.subject


class CareerSubjectYear(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.CharField(max_length=50)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.career.name_career, self.subject.subject, self.year)


class SubjectSchedule(models.Model):
    WEEK = (('Monday', 'Lunes'),
         ('Tuesday', 'Martes'),
         ('Wednesday', 'Miércoles'),
         ('Thursday', 'Jueves'),
         ('Friday', 'Viernes'),
         ('Saturday', 'Sábado'),
         ('Sunday', 'Domingo'))

    begin_time = models.TimeField()
    end_time = models.TimeField()
    day = MultiSelectField(choices=WEEK, max_length=100)
    career_subject_year = models.ForeignKey(CareerSubjectYear, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1}".format(self.career_subject_year, self.day)


