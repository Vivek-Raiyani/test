from django.urls import include, path

from .views import *

app_name = "user_app"

urlpatterns = [
    path('login/', login_view, name="login"),
    path('signup/', signup_view, name="signup"),
    path('logout/', logout_view, name="logout"),
    path('forgot-password/', forgot_password_view, name="forgot_password"),
    path('reset-password/<str:token>/', reset_password_view, name="reset_password"),
]