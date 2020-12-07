from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from events import views

urlpatterns = [
    path('rtmp/on-publish/', csrf_exempt(views.on_publish), name='publish'),
    path('rtmp/on-publish-done/',
         csrf_exempt(views.on_publish_done),
         name='publish-done'),
]
