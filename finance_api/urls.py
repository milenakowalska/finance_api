from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    ContractsList,
    SingleContract,
    StatisticsView,
    PrognoseView,
    SavingsList,
    SingleSaving,
    RecurringSavingsList,
    SingleRecurringSaving
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
    path('contracts/', ContractsList.as_view()),
    path('contracts/<int:pk>/', SingleContract.as_view()),
    path('savings/', SavingsList.as_view()),
    path('savings/<int:pk>/', SingleSaving.as_view()),
    path('recurring-savings/', RecurringSavingsList.as_view()),
    path('recurring-savings/<int:pk>/', SingleRecurringSaving.as_view()),
    path('statistics/', StatisticsView.as_view()),
    path('prognose/', PrognoseView.as_view()),
]
