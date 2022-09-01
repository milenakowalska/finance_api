from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
)
from rest_framework_swagger.views import get_swagger_view
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

schema_view = get_swagger_view(title='Finance API')

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('', schema_view),
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'api_schema'}
        ), name='swagger-ui'),
    path('api_schema/', get_schema_view(
        title='Finance API',
        description='Documentatio for the Django Finance API'
    ), name='api_schema'),
]

## either / or docs/ - check which is better