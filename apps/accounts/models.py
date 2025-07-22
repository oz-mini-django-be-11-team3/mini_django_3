from django.conf import settings
from django.db import models

from apps.common.models import CommonModel

from ..users.models import User
from .constants import ACCOUNT_TYPE_CHOICES, BANK_CODES


class Account(CommonModel):
    # 유저 정보
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accounts", verbose_name="사용자"
    )
    # 계좌번호
    account_number = models.CharField(
        max_length=50, unique=True, verbose_name="계좌번호"
    )
    # 은행 코드
    bank_code = models.CharField(
        max_length=10, choices=BANK_CODES, verbose_name="은행 코드"
    )
    # 계좌 종류
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPE_CHOICES, verbose_name="계좌 종류"
    )
    # 잔액 (소수점 포함 가능성이 있으므로 DecimalField)
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00, verbose_name="잔액"
    )

    class Meta:
        verbose_name = "계좌"
        verbose_name_plural = "계좌들"

    def __str__(self):
        return f"{self.user.nickname} - {self.get_bank_code_display()} {self.account_number}"
