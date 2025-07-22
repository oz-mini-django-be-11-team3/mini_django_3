from django.db import models

from apps.accounts.models import Account
from apps.common.models import CommonModel

# 거래 타입
TRANSACTION_IO_TYPE_CHOICES = [
    ("DEPOSIT", "입금"),
    ("WITHDRAW", "출금"),
]

# 거래 종류
TRANSACTION_METHOD_CHOICES = [
    ("ATM", "ATM 거래"),
    ("TRANSFER", "계좌이체"),
    ("AUTOMATIC_TRANSFER", "자동이체"),
    ("CARD", "카드결제"),
    ("INTEREST", "이자"),
]


# transaction_date -> created_at datetime
# transaction_update -> updated_at datetime
class TransactionHistory(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="계좌 정보",
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="거래 금액"
    )
    balance_after_transaction = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="거래 후 잔액"
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="거래 내역")

    # TRANSACTION_INPUT/OUTPUT
    io_type = models.CharField(
        max_length=10, choices=TRANSACTION_IO_TYPE_CHOICES, verbose_name="입출금 타입"
    )

    # TRANSACTION_METHOD
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_METHOD_CHOICES, verbose_name="거래 타입"
    )

    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="거래 일시")
    transaction_update = models.DateTimeField(
        auto_now=True, verbose_name="거래 내역 수정 일시"
    )

    class Meta:
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 내역들"

    # 모델 필드에 choices 옵션을 부여하면 런타임에 자동으로 get_FIELD_NAME_display()
    def __str__(self):
        return f"[{self.account.account_number}] {self.get_io_type_display()} {self.amount} - {self.description}"
