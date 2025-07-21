from django.urls import path

from . import views
from .views import (JWTLoginView, JWTLogoutView, UserProfileAPIView,
                    UserRegistrationView)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("auth/login/", JWTLoginView.as_view(), name="jwt_login"),
    path("auth/logout/", JWTLogoutView.as_view(), name="jwt_logout"),
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user_profile"),
]
