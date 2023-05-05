# Generated by Django 4.1.3 on 2023-05-02 18:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core',
         '0013_remove_round_data_submit_create_at_submit_final_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='round_target',
            field=models.FileField(null=True, upload_to='round_target'),
        ),
        migrations.AddField(
            model_name='submit',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='submit',
            name='score',
            field=models.FloatField(null=True),
        ),
    ]