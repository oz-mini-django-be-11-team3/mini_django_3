from django.conf import settings
from django.db import models

from .constants import ACCOUNT_TYPE, BANK_CODES


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=10, choices=BANK_CODES)
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPE)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.account_number}"
