# Generated by Django 4.1.3 on 2023-01-15 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_emaillog_emailverificationcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('name', models.CharField(max_length=63)),
                ('description', models.TextField(null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('name', models.CharField(max_length=63)),
                ('description', models.TextField(null=True)),
                ('datetime_start', models.DateTimeField()),
                ('datetime_end', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('game',
                 models.ForeignKey(
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     to='core.game')),
            ],
        ),
    ]
