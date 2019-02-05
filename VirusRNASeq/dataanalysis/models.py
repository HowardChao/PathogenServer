from django.db import models

class Post()

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PairedEnd(models.Model):
    file1 = models.FileField()
    file2 = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class SingleEnd(models.Model):
    file1 = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)