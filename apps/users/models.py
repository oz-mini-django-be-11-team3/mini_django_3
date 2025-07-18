from django.contrib.auth.models import (AbstractUser, PermissionsMixin,
                                        UserManager)
from django.db import models

from apps.common.models import CommonModel

# email
# password => AbstractUser 상속
# name
# nickname
# phone_number
# is_active => AbstractUser 상속
# is_staff => AbstractUser 상속
# is_superuser => AbstractUser 상속
# last_login => AbstractUser 상속
# created_at => CommonModel 상속
# updated_at => CommonModel 상속


class CustomUserModel(AbstractUser, CommonModel):
    email = models.EmailField("이메일", max_length=255, unique=True)
    name = models.CharField("이름", max_length=50)  # 이름은 같을 수 있다.
    nickname = models.CharField("별명", max_length=50, unique=True)
    phone_number = models.CharField("전화번호", max_length=15, unique=True)

    is_active = models.BooleanField(default=True)  # 계정 활성화 여부
    is_staff = models.BooleanField(default=False)  # 관리자 권한 여부

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "nickname", "phone_number"]

    objects = UserManager()  # 없으면 createsuperuser 사용하는데 제한

    def __str__(self):
        return f"email : {self.email}, nickname : {self.nickname}"
