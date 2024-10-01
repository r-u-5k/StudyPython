from django.db import models

# Create your models here.
class Test(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True)
    number = models.IntegerField(null=False, default=None)
