from django.contrib import admin

# Register your models here.
from professions_list.models import Profession, Skill

admin.site.register(Profession)
admin.site.register(Skill)