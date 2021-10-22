from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from events import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'streams', views.StreamViewSet, basename='stream')
router.register(r'slot-intervals',
                views.SlotIntervalViewSet,
                basename='slotinterval')

urlpatterns = [
    path('rtmp/on-publish/', csrf_exempt(views.on_publish), name='on-publish'),
    path('rtmp/on-publish-done/',
         csrf_exempt(views.on_publish_done),
         name='on-publish-done'),
    path('rtmp/on-update/', csrf_exempt(views.on_update), name='on-update'),
    path('streams/check/', views.streams_check_key, name='streams-check-key'),
    path('', include(router.urls))
]
