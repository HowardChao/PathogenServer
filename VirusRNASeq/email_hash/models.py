from django.db import models
from django.contrib.auth.models import User
import uuid

def analysis_code_generator():
    return uuid.uuid1().hex

def project_name_generator():
    return "Project" + uuid.uuid1().hex

class NewsletterUser(models.Model):
    project_name = models.CharField(
        max_length=100, default=project_name_generator)
    email = models.EmailField()
    data_added = models.DateTimeField(auto_now_add=True)
    analysis_code = models.CharField(max_length=32)
    def __str__(self):
        return self.email



