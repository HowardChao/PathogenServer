from django.db import models

def get_upload_to(project_name, pair_or_single):
    return 'tmp/%s/%d/' % (project_name, pair_or_single)

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PairedEnd(models.Model):
    file1 = models.FileField()
    file2 = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # def __str__(self):

class SingleEnd(models.Model):
    file1 = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Data(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
