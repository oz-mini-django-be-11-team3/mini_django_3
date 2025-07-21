from django.urls import path
from .views import UserRegistrationView, JWTLoginView, JWTLogoutView, UserProfileAPIView
from . import views

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("auth/login/", JWTLoginView.as_view(), name="jwt_login"),
    path("auth/logout/", JWTLogoutView.as_view(), name="jwt_logout"),
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user_profile"),
]
