from django.contrib import admin
from dataanalysis import models

# Register your models here.
class DataanalysisAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')

admin.site.register(models.Data, DataanalysisAdmin)
