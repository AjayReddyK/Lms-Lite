from django.db import models

class Profile(models.Model):
  b_id=models.CharField(max_length=20)
  device=models.CharField(max_length=400)

# Create your models here.
