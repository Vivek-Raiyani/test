from django.urls import include, path
from . import views

app_name = "core"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]