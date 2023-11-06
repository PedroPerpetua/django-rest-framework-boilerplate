from django.urls import path
from extensions.utilities.types import URLPatternsList
from users import views


app_name = "users"


urlpatterns: URLPatternsList = [
    path("whoami", views.UserWhoamiView.as_view(), name="whoami"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("login/refresh/", views.UserLoginRefreshView.as_view(), name="login-refresh"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("change_password", views.UserChangePasswordView.as_view(), name="change-password"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
