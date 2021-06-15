from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class FaceData(models.Model):
    user = models.OneToOneField(User,primary_key=True,on_delete = models.CASCADE,related_name="facedata")
    count = models.IntegerField(default=0,blank=False)
    encodings = models.TextField(default="[]")

    def __str__(self):
        return self.user.username+"' data"


