from django.urls import path, include
from rest_framework import routers
from .views import BookAPIViewSet

default_router = routers.DefaultRouter(trailing_slash=False)

default_router.register('books', BookAPIViewSet, basename='book')

app_name = 'content'

urlpatterns = [
    path('', include(default_router.urls)),
    path('django-rq/', include('django_rq.urls'))
]