from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

from django.core.exceptions import ValidationError
from django.db.models import Max
from django_cryptography.fields import encrypt

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
              ('face', 'Cara'),
              ('cardOrFaceOrFp', 'Cara, tarjeta o huella'),
              ('fpOrface', 'Cara o huella'))

class Device(models.Model):

    device = models.CharField(unique=True, max_length=50, null=False)
    ip = models.CharField(unique=True, max_length=50, null=False)
    door_port = models.IntegerField(null=False)
    date_purchased = models.DateField(editable=True, null=True)
    is_active = models.BooleanField(null=True)
    is_synchronized = models.BooleanField(null=True)
    user = models.CharField(max_length=50, null=False)
    password = encrypt(models.CharField(max_length=128, null=False))
    massive_opening = models.BooleanField(null=False)
   
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_password(self):
        return self.password

    def __str__(self):
        text = "{0}"
        return text.format(self.device)

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

class Career(models.Model):
    name_career = models.CharField(unique=True, max_length=100, null=True)

    def __str__(self):
        return self.name_career

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"


class Subject(models.Model):
    subject = models.CharField(unique=True, max_length=100, null=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

class CareerSubjectYear(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.CharField(max_length=50)

    def __str__(self):
        return "{0} - {1} - {2}".format(self.career.name_career, self.subject.subject, self.year)

    class Meta:
        verbose_name = "Carrera y materia"
        verbose_name_plural = "Carrera y materias"
        #unique_together = ('career', 'subject', 'year')

class SubjectSchedule(models.Model):
    WEEK = (('Monday', 'Lunes'),
         ('Tuesday', 'Martes'),
         ('Wednesday', 'Miércoles'),
         ('Thursday', 'Jueves'),
         ('Friday', 'Viernes'),
         ('Saturday', 'Sábado'),
         ('Sunday', 'Domingo'))

    horario_id = models.IntegerField(blank=True, verbose_name="ID de horario", null=True)
    begin_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    day = MultiSelectField(choices=WEEK, max_length=255, null=True)
    device = models.ForeignKey(Device, null=True, on_delete=models.CASCADE, verbose_name="Dispositivos")
    career_subject_year = models.ForeignKey(CareerSubjectYear, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1}".format(self.career_subject_year, self.day, self.begin_time, self.end_time)

    class Meta:
        verbose_name = "Horario de materia"
        verbose_name_plural = "Horario de materias"
        unique_together = ('horario_id', 'device')

class UserTypes(models.Model):
    user_type = models.CharField(verbose_name="Tipo de usuario", max_length=100, null=False)

    def __str__(self):
        text = "{1}"
        return text.format(self.id, self.user_type)
    
    class Meta:
        verbose_name = "Tipos de usuarios"
        verbose_name_plural = "Tipos de usuarios"

class UserProfile(models.Model):
    choices = [(None, '-------'), ('Sí', 'Sí'), ('No', 'No')]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Dispositivo")
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Apellido")
    dni = models.CharField(max_length=100, unique=True, verbose_name="DNI")
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, verbose_name="Correo electrónico")
    gender = models.CharField(max_length=10, choices=GENDER, verbose_name="Género")
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Teléfono")

    is_active = models.CharField(max_length=10, choices=choices, default=None, verbose_name="¿Fecha de habilitación?")
    begin_time = models.DateTimeField(editable=True, null=True, blank=True, verbose_name="Fecha inicio de habilitación")
    end_time = models.DateTimeField(editable=True, null=True, blank=True, verbose_name="Fecha final de habilitación")
    is_staff = models.CharField(max_length=10, choices=choices, default=None, verbose_name="¿Usuario administrador?")
    profile_type = models.CharField(default='normal', max_length=10, choices=PROFILETYPE, verbose_name="Tipo de usuario del dipositivo")
    file_image = models.FileField(upload_to='user_profile_api/images/', null=True, blank=True, verbose_name="Imagen")
    user_type = models.ForeignKey(UserTypes, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de usuario dentro de la institución")


    def __str__(self):
        text = "{0} {1} {2}"
        return text.format(self.first_name, self.last_name, self.dni)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = set(UserProfile.objects.values_list('id', flat=True))
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            self.id = next_id
        super().save(*args, **kwargs)


class UserProfileStudent(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    subject = models.ManyToManyField(SubjectSchedule, verbose_name="Materias a asistir", blank=True)
    user_verify_mode = models.CharField(max_length=30, choices=VERIFYMODE, blank=True, verbose_name="Tipo de verificación", null=True)
    door_right = models.CharField(max_length=100, verbose_name="Puerta proxima", null=True)
    doorNo = models.CharField(max_length=100, verbose_name="Número de puerta", null=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now, verbose_name="Fecha creación", null=True)
    last_updated = models.DateTimeField(editable=False, default=timezone.now, verbose_name="Fecha actualización", null=True)
    card = models.CharField(max_length=20, blank=True, verbose_name="Tarjeta", null=True)
    card_type = models.CharField(max_length=20, blank=True, choices=CARDS, verbose_name="Tipo de tarjeta", null=True)
    time_type = models.CharField(max_length=10, default='local', verbose_name="Modo de hora", null=True)
    fingerprint = models.TextField(unique=True, blank=True, null=True)

    def clean(self):
        super().clean()
        if self.card and not self.cardType:
            raise ValidationError({'cardType': 'Tipo de tarjeta es requerido si se agrega tarjeta.'})
        elif self.cardType and not self.card:
            raise ValidationError({'card': 'Tarjeta es requerido si tipo de tarjeta se completa.'})
        elif self.card and not (17 <= len(self.card) <= 20):
            raise ValidationError(
                {'card': "El identificador de tarjeta debe tener entre 17 y 20 caracteres y solo puede contener letras o números."}
            )
            
    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = set(UserProfileStudent.objects.values_list('id', flat=True))
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            self.id = next_id
        super().save(*args, **kwargs)

class UserProfileMaintenance(models.Model):
    choices = [(None, '-------'), ('Sí', 'Sí'), ('No', 'No')]

    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    sunday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Domingo")
    sunday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    sunday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    monday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Lunes")
    monday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    monday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    tuesday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Martes")
    tuesday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    tuesday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    wednesday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Miércoles")
    wednesday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    wednesday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    thursday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Jueves")
    thursday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    thursday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    friday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Viernes")
    friday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    friday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")
    saturday = models.CharField(max_length=3, choices=choices, default=None, verbose_name="Sábado")
    saturday_time_begin = models.TimeField(null=True, verbose_name="Hora de inicio")
    saturday_time_end = models.TimeField(null=True, verbose_name="Hora de fin")

    class Meta:
        verbose_name = "Personal de Mantenimiento"

    def save(self, *args, **kwargs):
        if not self.id:
            existing_ids = set(UserProfileMaintenance.objects.values_list('id', flat=True))
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            self.id = next_id
        super().save(*args, **kwargs)

class Room(models.Model):
    room = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)

    def __str__(self):
        text = "{0} ({1})"
        return text.format(self.room, self.location)

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
