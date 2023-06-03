from os import device_encoding
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import AutoField, BooleanField, CharField, FloatField, IntegerField, TimeField

# Create your models here.

class pwd(Model):
    user_id = AutoField(primary_key=True)
    user = CharField(max_length=20,unique=True)
    password = CharField(max_length=20)

class userDevice(Model):
    id = AutoField(primary_key=True)
    device = CharField(max_length=20,unique=True)
    user = IntegerField()
    name = CharField(max_length=40)

class plantInfo(Model):
    id = AutoField(primary_key=True)
    device = CharField(max_length=20)
    time = FloatField()
    dirt_temperature = FloatField()
    air_temperature = FloatField()
    humidity = FloatField()
    carbon_dioxide = FloatField()

class component(Model):
    id = AutoField(primary_key=True)
    device = CharField(max_length=20)
    time = FloatField()
    fan = BooleanField()
    light = BooleanField()
    water = BooleanField()