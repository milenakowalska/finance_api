from django.urls import path
from rest_framework.schemas import get_schema_view
from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    InfoView
)
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Finance API')

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('', schema_view)
]