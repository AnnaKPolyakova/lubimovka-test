from datetime import datetime, timedelta

import jwt as jwt
from django.db import models
from phonenumber_field import modelfields
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


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