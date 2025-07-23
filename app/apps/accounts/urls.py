from django.urls import path

from .models import Account
from .views import AccountAPIView, AccountListApiView

app_name = "accounts"

urlpatterns = [
    path("", AccountListApiView.as_view(), name="account-list-create"),
    path("<int:pk>/", AccountAPIView.as_view(), name="account-delete"),
]
