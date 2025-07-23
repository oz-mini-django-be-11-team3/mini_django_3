from django.urls import path

from . import views
from .views import (JWTLoginView, JWTLogoutView, UserProfileAPIView,
                    UsersAPIView)

urlpatterns = [
    path("", UsersAPIView.as_view(), name="user_signin"),
    # <int:pk>
    path("me/", UserProfileAPIView.as_view(), name="user_profile"),
    path("auth/login/", JWTLoginView.as_view(), name="jwt_login"),
    path("auth/logout/", JWTLogoutView.as_view(), name="jwt_logout"),
]
