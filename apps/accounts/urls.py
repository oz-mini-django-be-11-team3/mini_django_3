from django.urls import path

from .views import AccountDeleteAPIView, AccountListCreateApiView

app_name = "accounts"

urlpatterns = [
    path(
        "list-create/", AccountListCreateApiView.as_view(), name="account-list-create"
    ),
    path("delete/<int:pk>/", AccountDeleteAPIView.as_view(), name="account-delete"),
]
