from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Transaction)
