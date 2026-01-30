"""
URL configuration for Medicine_Accounting project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
#from django import views
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from myappmedicine import views

urlpatterns = [
   
    path("", TemplateView.as_view(template_name="index.html"), name='index'),
    path('login/', TemplateView.as_view(template_name="index.html"), name='index'),
    path('list_of_medicines/', TemplateView.as_view(template_name="list_of_medicines.html"), name='list_of_medicines'),
    path('change_status/', TemplateView.as_view(template_name="change_status.html"), name='change_status'),
    path('new_batch/', TemplateView.as_view(template_name="new_batch.html"), name='new_batch'),
    path('registration/', TemplateView.as_view(template_name="reg.html"), name='reg'),
    path('new_product/', TemplateView.as_view(template_name="new_product.html"), name='new_product'),
    path('login_page/', views.login_view, name='login_page'),
    path('logout/', views.log_out_view, name='logout'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('reg_user/', views.reg_user_view, name='reg_user'),
    path('add_batch_preview/', views.add_batch_preview, name='add_batch_preview'),
    path('add_batch/', views.add_batch_view, name='add_batch'),
    path('list_view/', views.list_view, name='list_view'),
    path('change_status_preview/', views.change_status_preview, name='change_status_preview'),
    path('change_status_view/', views.change_status_view, name='change_status_view'),
    #path('admin/', admin.site.urls, name='admin'),
]
