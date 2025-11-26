from django.contrib import admin
from .models import Profile, Recipe  # import your models

# Register models
admin.site.register(Profile)
admin.site.register(Recipe)

# Register your models here.
