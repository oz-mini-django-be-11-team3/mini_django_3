from rest_framework import serializers

from apps.transactions.models import TransactionHistory


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class TransactionsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = [
            "id",
            "account",
            "amount",
            "description",
            "io_type",
            "transaction_type",
            "transaction_date",
        ]
        read_only_fields = ["id", "balance_after_transaction", "transaction_date"]


class TransactionsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = ["description"]
        read_only_fields = ["id"]
