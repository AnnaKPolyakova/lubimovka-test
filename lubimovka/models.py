from django.db import models
from phonenumber_field import modelfields
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class UnconfirmedUser(models.Model):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    confirmation_code = models.CharField(
        verbose_name='confirmation code',
        max_length=30,
    )

    def __str__(self):
        return f'{self.email} '


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    bio = models.TextField(blank=True)
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.email


class Employee(models.Model):
    name = models.CharField(
        max_length=40,
        verbose_name="Имя",
        help_text="Не более 40 символов",
    )
    surname = models.CharField(
        max_length=40,
        verbose_name="Фамилия",
        help_text="Не более 40 символов",
    )
    patronymic = models.CharField(
        max_length=40,
        verbose_name="Отчество",
        help_text="Не более 40 символов",
    )
    position = models.CharField(
        max_length=40,
        verbose_name="Должность",
        help_text="Не более 40 символов",
    )
    work_phone_number = modelfields.PhoneNumberField(
        verbose_name="Рабочий номер телефона"
    )
    personal_phone_number = modelfields.PhoneNumberField(
        unique=True,
        verbose_name="Личный номер телефона"
    )
    fax = modelfields.PhoneNumberField(
        verbose_name="Факс"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f'{self.name} {self.surname} {self.patronymic}, должность: ' \
               f'{self.position} '

    def clean(self):
        if (
                self.work_phone_number is None and
                self.personal_phone_number is None and
                self.fax is None
        ):
            raise ValidationError(
                "Необходимо указать хотя бы один номер телефона."
            )


class Organization(models.Model):
    title = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Название",
        help_text="Не более 40 символов",
    )
    address = models.CharField(
        max_length=40,
        verbose_name="Адрес",
        help_text="Не более 40 символов",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Краткое описание",
    )
    employees = models.ManyToManyField(
        Employee,
        through="OrganizationEmployeeRelation"
    )

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"


class OrganizationEmployeeRelation(models.Model):
    employee = models.ForeignKey(
        Employee,
        verbose_name="Сотрудник",
        on_delete=models.SET_NULL,
        null=True,
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name="Организация",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = "Сотрудник в организации"
        verbose_name_plural = "Сотрудники в организации"
        unique_together = ('employee', 'organization')

    def __str__(self):
        return self.employee
