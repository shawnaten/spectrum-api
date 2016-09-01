from django.conf.urls import url

from chatbot import views

urlpatterns = [
    url(r'^sms$', views.sms, name='sms'),
]
