from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Employee, Organization

User = get_user_model


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализация регистрации пользователя и создания нового."""

    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmployeesInOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "work_phone_number",
            "personal_phone_number",
            "fax",
        )
        model = Employee


class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Employee

    def validate(self, data):
        if self.context["request"].method in ("POST", "PUT"):
            fields = ["work_phone_number", "personal_phone_number", "fax"]
            for field in fields:
                if field in self.context["request"].data:
                    return data
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один номер телефона."
            )
        if self.context["request"].method == "PATCH":
            employee = get_object_or_404(
                Employee,
                id=self.context["request"].parser_context["kwargs"]["pk"],
            )
            fields = ["work_phone_number", "personal_phone_number", "fax"]
            phone_numbers = {
                "work_phone_number": employee.work_phone_number,
                "personal_phone_number": employee.personal_phone_number,
                "fax": employee.fax,
            }
            for field in fields:
                if field in self.context["request"].data:
                    phone_numbers[field] = self.context["request"].data[field]
            if list(phone_numbers.values()) == ["", "", ""]:
                raise serializers.ValidationError(
                    "Необходимо указать хотя бы один номер телефона."
                )
        return data


class OrganizationGetSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "title", "employees"]
        model = Organization

    def get_employees(self, obj):
        request = self.context.get("request")
        search = request.query_params.get("search")
        if search is not None:
            return EmployeesInOrganizationSerializer(
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
        return EmployeesInOrganizationSerializer(
            obj.employees.distinct()[:5],
            many=True,
        ).data


class OrganizationSerializer(serializers.ModelSerializer):

    employees = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Employee.objects.all(),
        default=serializers.CurrentUserDefault(),
        many=True,
    )

    class Meta:
        fields = ["title", "address", "description", "employees"]
        model = Organization


class AccessToEditSerializer(serializers.Serializer):
    user = serializers.ListField(child=serializers.EmailField())
