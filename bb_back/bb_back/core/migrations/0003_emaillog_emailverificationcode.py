# Generated by Django 4.1.3 on 2023-01-06 21:31

import bb_back.core.constants
import bb_back.core.models.email
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_is_email_confirmed'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('email_type',
                 models.SmallIntegerField(
                     default=bb_back.core.constants.EmailTypes['NONE_EMAIL'])),
                ('receiver_email', models.CharField(max_length=63)),
                ('created_at',
                 models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='EmailVerificationCode',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('code', models.CharField(max_length=32)),
                ('expires_at',
                 models.DateTimeField(
                     default=bb_back.core.models.email.
                     get_email_verification_code_expiration_datetime)),
                ('created_at',
                 models.DateTimeField(default=django.utils.timezone.now)),
                ('user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.DO_NOTHING,
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
