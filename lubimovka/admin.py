from django.contrib import admin

from .models import Employee, Organization, OrganizationEmployeeRelation


class OrganizationEmployeeRelationAdminInline(admin.TabularInline):
    model = Organization.employees.through
    extra = 0
    verbose_name_plural = (
        "Cотрудники организации"
    )
    # raw_id_fields = ("employee",)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "surname", "patronymic", "position")


class OrganizationAdmin(admin.ModelAdmin):
    inlines = (
        OrganizationEmployeeRelationAdminInline,
    )
    list_display = ("title", "address")


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Organization, OrganizationAdmin)
