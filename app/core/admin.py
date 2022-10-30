from django.contrib import admin


class AdminSite(admin.AdminSite):
    pass


admin_site = AdminSite()
