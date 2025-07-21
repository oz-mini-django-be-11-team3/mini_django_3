from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from apps.common.models import CommonModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


# 상속 #
# PermissionsMixin -> is_superuser, groups, user_permissions
# AbstractUser -> is_active, is_staff, is_superuser
# AbstractBaseUser -> password, last_login
# CommonModel -> create_at, updated_at

# + email(username 대신 사용), name, nickname, phone_number


class CustomUserModel(AbstractUser, CommonModel):
    email = models.EmailField(
        "이메일",
        max_length=255,
        unique=True,
        help_text="* 필수 기재 항목입니다.",
        error_messages={
            "unique": "이미 가입된 이메일 주소입니다.",
        },
    )

    # AbstractUser.username Overriding, or username unique 때문에 에러
    username = models.CharField(
        "이름",
    )

    name = models.CharField(
        "사용자 이름",
        max_length=50,
        help_text="* 필수 기재 항목입니다.",
    )  # 이름은 같을 수 있다.
    nickname = models.CharField(
        "닉네임",
        max_length=50,
        unique=True,
        help_text="* 필수 기재 항목입니다.",
        error_messages={
            "unique": "중복이 불가능합니다.",
        },
    )
    phone_number = models.CharField("전화번호", max_length=15, blank=True, null=True)

    is_active = models.BooleanField("스태프 여부", default=True)  # 계정 활성화 여부
    is_staff = models.BooleanField(
        "계정 활성화 여부", default=False
    )  # 관리자 페이지 권한 여부

    USERNAME_FIELD = "email"  # 식별용
    REQUIRED_FIELDS = ["name", "nickname"]

    # AbstractUser의 UserManager() 대신 사용. 없으면 create_(super)user() 사용 오류
    objects = CustomUserManager()

    def __str__(self):
        return f"email : {self.email}, nickname : {self.nickname}"

    # 관리자 페이지에 표시되는 이름
    class Meta:
        verbose_name = "회원"
        verbose_name_plural = "회원목록"
