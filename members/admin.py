from django.contrib import admin
from .models import *


# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "joined_date",)


admin.site.register(Member, MemberAdmin)
admin.site.register(Action)
admin.site.register(PorteFeuille)
