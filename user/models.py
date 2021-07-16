from django.db import models

class Profile(models.Model):
  b_id=models.CharField(max_length=20)
  device=models.CharField(max_length=400)
  def __str__(self):
    return self.b_id
# Create your models here.
