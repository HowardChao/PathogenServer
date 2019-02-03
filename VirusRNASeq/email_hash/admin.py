from django.contrib import admin
from email_hash import models

# Register your models here.
class NeswletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'data_added')

admin.site.register(models.NewsletterUser, NeswletterAdmin)