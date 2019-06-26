from django.contrib import admin
from django.urls import path, include
from .views import *

# TODO сделать нормальные url, утвердить с фронтом
urlpatterns = [
    path('payment/create', Payment.as_view()),
    path('payment/get', GetPayment.as_view()),
    path('user/create', Registration.as_view()),
    path('project/create', CreateProject.as_view()),
    path('show/projects', ProjectListView.as_view()),
    #path('test', TestView.as_view())
    path('user/project', ShowUserProjectsView.as_view()),
    path('project/topic', ShowProjectsTopicView.as_view()),
    path('project/status', ChangeProjectStatusView.as_view()),
    path('show/project', ShowProjectView.as_view()),
    path('user/authorization', AuthorizationView.as_view()),
    path('payment/yandex_callback', YandexCallbackView.as_view()),
    path('payment/rfibank_callback', RFIBankCallbackView.as_view()),
    path('payment/qiwi_callback', CheckPayment.as_view()),
]
