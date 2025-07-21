from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUserModel


@admin.register(CustomUserModel)
class CustomAdmin(UserAdmin):
    list_display = [
        "email",
        "id",
        "last_login",
        "name",
        "nickname",
        "phone_number",
        "is_staff",
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields = ("email", "nickname", "name", "phone_number")
    ordering = ("name",)

    # 사용자 수정 화면 디스플레이
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("name", "nickname", "phone_number")}),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("접속 일시", {"fields": ("last_login",)}),
    )

    # 사용자 생성 디스플레이
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "nickname",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
