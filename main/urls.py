from django.urls import path
from .views import chatbot_view
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # homepage
    path('create-officer/', views.create_officer, name='create_officer'),
    path('add-education/<str:army_number>/', views.add_education, name='add_education'),
    path('add-family/<str:army_number>/', views.add_family, name='add_family'),
    path('add-award/<str:army_number>/', views.add_award, name='add_award'),
    path('success/', views.success, name='success'),
    path('register/', views.create_officer, name='create_officer'),
    path('extract-officer-data/', views.extract_officer_data, name='extract_officer_data'),
    path('chatbot/', chatbot_view, name='chatbot'),
    path("export/download/<str:filename>", views.download_export, name="download_export"),
]  