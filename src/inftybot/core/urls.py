# coding: utf-8


from django.urls import path

from inftybot.core import views

app_name = 'core'
urlpatterns = [
    path('webhook', views.webhook, name='webhook')
]
