from core.models.base_model import BaseModel
from django.db import models

class User(BaseModel):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    age = models.IntegerField()