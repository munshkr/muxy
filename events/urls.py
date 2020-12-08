from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from events import views

urlpatterns = [
    path('rtmp/on-publish/', csrf_exempt(views.on_publish), name='on-publish'),
    path('rtmp/on-publish-done/',
         csrf_exempt(views.on_publish_done),
         name='on-publish-done'),
    path('rtmp/on-update/', csrf_exempt(views.on_update), name='on-update'),
]
