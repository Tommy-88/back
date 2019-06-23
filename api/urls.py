from django.contrib import admin
from django.urls import path, include
from .views import *

# TODO сделать нормальные url, утвердить с фронтом
urlpatterns = [
    path('hello', Payment.as_view()),
    path('user/create', Registration.as_view()),
    path('project/create', CreateProject.as_view()),
    path('show/projects', ProjectListView.as_view()),
    #path('test', TestView.as_view())
    path('user/project', ShowUserProjectsView.as_view()),
    path('project/topic', ShowProjectsTopicView.as_view()),
    path('project/status', ChangeProjectStatusView.as_view()),
    path('show/project', ShowProjectView.as_view())
]
