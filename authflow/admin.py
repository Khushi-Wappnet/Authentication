# filepath: [admin.py](http://_vscodecontentref_/7)
from django.contrib import admin
from .models import CustomUser, Role, Permission, RolePermission

admin.site.register(CustomUser)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)