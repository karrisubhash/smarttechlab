from django.urls import path
from . import views

urlpatterns = [
    path('', views.experiment_list, name='experiment_list'),
    path('<slug:slug>/', views.run_experiment, name='run_experiment'),


]
