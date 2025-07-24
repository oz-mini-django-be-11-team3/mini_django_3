from django.urls import path

from .views import (
    TransactionHistoryCreateView,
    TransactionHistoryDetailView,
    TransactionHistoryView,
)

app_name = "transactions"
urlpatterns = [
    path("", TransactionHistoryView.as_view(), name="transaction-list"),
    path("create/", TransactionHistoryCreateView.as_view(), name="transaction-create"),
    path(
        "<int:pk>/", TransactionHistoryDetailView.as_view(), name="transaction-detail"
    ),
]
