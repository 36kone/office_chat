from django.db import models

from core.models.base_model import BaseModel


class User(BaseModel):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
