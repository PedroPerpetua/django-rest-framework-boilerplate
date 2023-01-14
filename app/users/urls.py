from django.urls import path
from rest_framework_simplejwt import views as jwt_views  # type: ignore # No stubs available
from core.utilities.types import URLPatternsList
from users import views


app_name = "users"


urlpatterns: URLPatternsList = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="login"),
    path("token_refresh/", jwt_views.TokenRefreshView.as_view(), name="token-refresh"),
    path("change_password", views.UserChangePasswordView.as_view(), name="change-password"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
