from apps.common.models import CommonModel
from django.db import models

# from apps.accounts.models import Account

# 거래 타입
TRANSACTION_TYPE = [
    ("DEPOSIT", "입금"),
    ("WITHDRAW", "출금"),
]

# 거래 종류
TRANSACTION_METHOD = [
    ("ATM", "ATM 거래"),
    ("TRANSFER", "계좌이체"),
    ("AUTOMATIC_TRANSFER", "자동이체"),
    ("CARD", "카드결제"),
    ("INTEREST", "이자"),
]


# transaction_date -> created_at datetime
# transaction_update -> updated_at datetime
class Transaction(CommonModel):
    id = models.BigAutoField(primary_key=True)  # id bigint
    # account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions') #account_id bigint nn
    amount = models.DecimalField(
        max_digits=15, decimal_places=2
    )  # amount decimal(15,2)
    balance_after_transaction = models.DecimalField(
        max_digits=15, decimal_places=2
    )  # balance_after_transaction decimal(15,2)
    description = models.CharField(max_length=255)  # description varchar(255)
    io_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE
    )  # io_type enum(TRANSACTION_IO_TYPE_CHOICES)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_METHOD
    )  # transaction_type enum(TRANSACTION_METHOD_CHOICES)
