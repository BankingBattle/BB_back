# Generated by Django 4.1.3 on 2023-02-04 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_game_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='data',
            field=models.FileField(null=True, upload_to='round_data'),
        ),
    ]
