from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_xml, name='upload_xml'),
]

