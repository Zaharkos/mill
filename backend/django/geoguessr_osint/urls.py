"""
URL configuration for geoguessr_osint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from geoguessr import views as geoguessr_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',
         geoguessr_views.main_page,
         name='main-page'),

    path('registration',
         geoguessr_views.register_form,
         name='registration-page'),

    path('login',
         geoguessr_views.login_form,
         name='login-page'),

    path('logout',
         geoguessr_views.logout_view,
         name='logout'),

    path('account',
         geoguessr_views.military_request_list,
         name='account'),

    path('recognation-requests/create',
         geoguessr_views.create_recognition_request,
         name='recognation_request_create'),

    path('recognation-requests/list',
         geoguessr_views.show_recognition_requests,
         name='recognation_request_list'),

    path('recognation-requests/<str:pk>/',
         geoguessr_views.get_recognition_request,
         name='recognation_request'),

     path('user/promote',
          geoguessr_views.military_promote,
          name='request-promote'),

     path('verification/', include('verify_email.urls')),

     path('api/crypto/', include('crypto_api.urls')),

     path('recognition-request-details/<str:pk>/',
          geoguessr_views.recognition_request_details,
          name='recognition-request-details'),

     path('promote-accept/<str:pk>/',
          geoguessr_views.accept_promote,
          name='accept-promote'),

     path('promote-decline/<str:pk>/',
          geoguessr_views.decline_promote,
          name='decline-promote'),

     path('admin-panel/',
          geoguessr_views.admin_panel,
          name='admin-panel'),

     path('close-request/<str:pk>/',
          geoguessr_views.recognition_request_close,
          name='close-request'),

     path('profile/',
          geoguessr_views.profile,
          name='profile')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
