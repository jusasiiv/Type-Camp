from django.urls import path
from trainer import views

urlpatterns = [
    path("", views.practice, name="practice"),
    path("chart/", views.chart, name="chart"),
    path("progress/", views.progress, name="progress"),
]
