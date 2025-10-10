from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from main import views 
urlpatterns = [
     path('admin/', admin.site.urls),
     path('', include('main.urls')),  # no need to redirect anymore
     path('chat-api/', views.chat_api, name='chat_api'),  
] 


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)