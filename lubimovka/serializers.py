from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User, Organization, Employee
from django.db.models import Q


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    # Убедитесь, что пароль содержит не менее 8 символов, не более 128,
    # и так же что он не может быть прочитан клиентской стороной
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        # Перечислить все поля, которые могут быть включены в запрос
        # или ответ, включая поля, явно указанные выше.
        fields = ['email', 'password']

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return User.objects.create_user(**validated_data)


class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'work_phone_number', 'personal_phone_number', 'fax')
        model = Employee


class OrganizationGetSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'title', 'employees']
        model = Organization

    def get_employees(self, obj):
        request = self.context.get("request")
        search = request.query_params.get("search")
        if search is not None:
            return EmployeesSerializer(
                obj.employees.filter(
                    Q(name__icontains=search)
                    | Q(work_phone_number__icontains=search)
                    | Q(fax__icontains=search)
                    | Q(personal_phone_number__icontains=search)
                    | Q(surname__icontains=search)
                    | Q(patronymic__icontains=search)
                    | Q(position__icontains=search)
                ).distinct()[:5],
                many=True,
            ).data
        return EmployeesSerializer(
            obj.employees.distinct()[:5],
            many=True,
        ).data


class OrganizationSerializer(serializers.ModelSerializer):

    employees = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Employee.objects.all(),
        default=serializers.CurrentUserDefault(),
        many=True
    )

    class Meta:
        fields = ['title', 'address', 'description', 'employees']
        model = Organization


class AccessToEditSerializer(serializers.Serializer):
    organization = serializers.IntegerField(min_value=1)
    user = serializers.ListField(
        child=serializers.IntegerField(min_value=1,max_value=100)
    )


class ListUsersAccessToEditSerializer(serializers.Serializer):
    organization = serializers.IntegerField(min_value=1)