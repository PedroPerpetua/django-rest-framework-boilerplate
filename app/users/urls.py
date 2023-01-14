from django.urls import path
from core.utilities.types import URLPatternsList
from users import views


app_name = "users"


urlpatterns: URLPatternsList = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
]
