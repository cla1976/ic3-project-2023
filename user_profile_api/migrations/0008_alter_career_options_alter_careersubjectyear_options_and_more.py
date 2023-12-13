# Generated by Django 4.2.4 on 2023-10-24 00:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile_api', '0007_alter_subjectschedule_day'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='career',
            options={'verbose_name': 'Carrera', 'verbose_name_plural': 'Carreras'},
        ),
        migrations.AlterModelOptions(
            name='careersubjectyear',
            options={'verbose_name': 'Carrera y materia', 'verbose_name_plural': 'Carrera y materias'},
        ),
        migrations.AlterModelOptions(
            name='device',
            options={'verbose_name': 'Dispositivo', 'verbose_name_plural': 'Dispositivos'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'Sala', 'verbose_name_plural': 'Salas'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'verbose_name': 'Materia', 'verbose_name_plural': 'Materias'},
        ),
        migrations.AlterModelOptions(
            name='subjectschedule',
            options={'verbose_name': 'Horario de materia', 'verbose_name_plural': 'Horario de materias'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
        migrations.RemoveField(
            model_name='device',
            name='users',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='emergency_phone',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='planTemplateNo',
        ),
        migrations.AddField(
            model_name='device',
            name='door_port',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='ip',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='device',
            name='massive_opening',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='password',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='user',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='subjectschedule',
            name='device',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user_profile_api.device', verbose_name='Dispositivos'),
        ),
        migrations.AddField(
            model_name='subjectschedule',
            name='horario_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID de horario'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='subject',
            field=models.ManyToManyField(null=True, to='user_profile_api.subjectschedule', verbose_name='Materias a asistir'),
        ),
        migrations.AlterField(
            model_name='career',
            name='name_career',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='date_purchased',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='device',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='is_active',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='is_synchronized',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='subject',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='subjectschedule',
            name='begin_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='subjectschedule',
            name='day',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Monday', 'Lunes'), ('Tuesday', 'Martes'), ('Wednesday', 'Miércoles'), ('Thursday', 'Jueves'), ('Friday', 'Viernes'), ('Saturday', 'Sábado'), ('Sunday', 'Domingo')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='subjectschedule',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(max_length=100, null=True, verbose_name='Dirección'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='beginTime',
            field=models.DateTimeField(null=True, verbose_name='Fecha inicio de habilitación'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='card',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Tarjeta'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='cardType',
            field=models.CharField(blank=True, choices=[('normalCard', 'Normal'), ('patrolCard', 'Mantenimiento'), ('hijackCard', 'Hijack'), ('superCard', 'Super'), ('dismissingCard', 'Destituir'), ('emergencyCard', 'Emergencia')], max_length=20, null=True, verbose_name='Tipo de tarjeta'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True, verbose_name='Fecha creación'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='dni',
            field=models.CharField(max_length=100, null=True, unique=True, verbose_name='DNI'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='doorNo',
            field=models.CharField(max_length=100, null=True, verbose_name='Número de puerta'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='doorRight',
            field=models.CharField(max_length=100, null=True, verbose_name='Puerta proxima'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=255, null=True, unique=True, verbose_name='Correo electrónico'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='endTime',
            field=models.DateTimeField(null=True, verbose_name='Fecha final de habilitación'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='fileImage',
            field=models.FileField(blank=True, null=True, upload_to='user_profile_api/images/', verbose_name='Imagen'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(max_length=100, null=True, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Hombre'), ('female', 'Mujer'), ('unknown', 'Sin especificar')], max_length=10, null=True, verbose_name='Género'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_active',
            field=models.BooleanField(default=True, null=True, verbose_name='¿Usuario habilitado?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_staff',
            field=models.BooleanField(default=False, null=True, verbose_name='¿Usuario administrador?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(max_length=100, null=True, verbose_name='Apellido'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_updated',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True, verbose_name='Fecha actualización'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Teléfono'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_type',
            field=models.CharField(choices=[('normal', 'Normal'), ('visitor', 'Visitante'), ('blackList', 'Bloqueado')], max_length=10, null=True, verbose_name='Tipo de usuario'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='timeType',
            field=models.CharField(default='local', max_length=10, null=True, verbose_name='Modo de hora'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='userVerifyMode',
            field=models.CharField(blank=True, choices=[('cardOrFace', 'Tarjeta o cara'), ('cardOrfaceOrPw', 'Tarjeta, cara o clave'), ('cardOrPw', 'Tarjeta o clave'), ('card', 'Tarjeta'), ('cardOrFace', 'Cara o clave'), ('face', 'Cara')], max_length=30, null=True, verbose_name='Tipo de verificación'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_device_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='ID de usuario'),
        ),
        migrations.AlterUniqueTogether(
            name='subjectschedule',
            unique_together={('horario_id', 'device')},
        ),
    ]