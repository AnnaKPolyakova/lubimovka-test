from django.contrib import admin

from .models import Employee, Organization


class OrganizationEmployeeRelationAdminInline(admin.TabularInline):
    model = Organization.employees.through
    extra = 0
    verbose_name_plural = "Cотрудники организации"


class OrganizationUserRelationAdminInline(admin.TabularInline):
    model = Organization.access_to_edit.through
    extra = 0
    verbose_name_plural = "Пользователи с доступом к редактированию"


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "surname", "patronymic", "position")


class OrganizationAdmin(admin.ModelAdmin):
    inlines = (
        OrganizationEmployeeRelationAdminInline,
        OrganizationUserRelationAdminInline,
    )
    list_display = ("title", "address")


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Organization, OrganizationAdmin)
