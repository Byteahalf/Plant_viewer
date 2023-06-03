# Generated by Django 3.1.1 on 2020-10-24 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='component',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('device', models.CharField(max_length=20)),
                ('time', models.FloatField()),
                ('fan', models.BooleanField()),
                ('light', models.BooleanField()),
                ('water', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='plantInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('device', models.CharField(max_length=20)),
                ('time', models.FloatField()),
                ('dirt_temperature', models.FloatField()),
                ('air_temperature', models.FloatField()),
                ('humidity', models.FloatField()),
                ('carbon_dioxide', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='pwd',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='userDevice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('device', models.CharField(max_length=20, unique=True)),
                ('user', models.IntegerField()),
                ('name', models.CharField(max_length=40)),
            ],
        ),
    ]
