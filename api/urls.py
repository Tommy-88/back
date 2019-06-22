from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('hello', Payment.as_view()),
    path('user/create', Registration.as_view()),
    path('project/create', CreateProject.as_view()),
    path('show/projects', ProjectListView.as_view()),
    #path('test', TestView.as_view())
    path('user/project', ShowUserProjectsView.as_view()),
    path('project/topic', ShowProjectsTopicView.as_view())
]
