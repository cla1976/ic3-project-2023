# Generated by Django 4.1.7 on 2023-04-26 06:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Career',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_career', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CareerSubjectYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=50)),
                ('career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile_api.career')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device', models.CharField(max_length=50)),
                ('date_purchased', models.DateField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_synchronized', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_device_id', models.IntegerField(blank=True, unique=True)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('gender', models.CharField(choices=[('male', 'Hombre'), ('female', 'Mujer'), ('unknown', 'Sin especificar')], max_length=10)),
                ('userVerifyMode', models.CharField(blank=True, choices=[('cardOrFace', 'Tarjeta o cara'), ('cardOrfaceOrPw', 'Tarjeta, cara o clave'), ('cardOrPw', 'Tarjeta o clave'), ('card', 'Tarjeta'), ('cardOrFace', 'Cara o clave'), ('face', 'Cara')], max_length=30)),
                ('doorRight', models.CharField(max_length=100)),
                ('doorNo', models.CharField(max_length=100)),
                ('planTemplateNo', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('profile_type', models.CharField(choices=[('normal', 'Normal'), ('visitor', 'Visitante'), ('blackList', 'Bloqueado')], max_length=10)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('dni', models.CharField(max_length=100, null=True, unique=True)),
                ('address', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('emergency_phone', models.CharField(max_length=100, null=True)),
                ('beginTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('fileImage', models.FileField(blank=True, upload_to='user_profile_api/images/')),
                ('card', models.CharField(blank=True, max_length=20)),
                ('cardType', models.CharField(blank=True, choices=[('normalCard', 'Normal'), ('patrolCard', 'Mantenimiento'), ('hijackCard', 'Hijack'), ('superCard', 'Super'), ('dismissingCard', 'Destituir'), ('emergencyCard', 'Emergencia')], max_length=20)),
                ('timeType', models.CharField(default='local', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SubjectSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('day', models.CharField(max_length=20)),
                ('career_subject_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile_api.careersubjectyear')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_profile_api.device')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='devices', to='user_profile_api.userprofile'),
        ),
        migrations.AddField(
            model_name='careersubjectyear',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile_api.subject'),
        ),
    ]
