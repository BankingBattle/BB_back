# Generated by Django 4.1.3 on 2023-01-22 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_game_round'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submit',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='submits')),
                ('id_command', models.IntegerField(null=True)),
                ('round_num', models.IntegerField(null=True)),
            ],
        ),
    ]
