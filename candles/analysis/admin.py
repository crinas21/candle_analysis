from django.contrib import admin
from .models import User, History
from django.contrib.auth.admin import UserAdmin

admin.site.register(History)
admin.site.register(User, UserAdmin)
