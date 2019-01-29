from django.db import models
from django.db.models.signals import pre_init
import uuid

def analysis_code_generator():
    return uuid.uuid1().hex

class NewsletterUser(models.Model):

    email = models.EmailField()
    data_added = models.DateTimeField(auto_now_add=True)
    analysis_code = models.CharField(
        max_length=32, default=analysis_code_generator)
    def __str__(self):
        return self.email



