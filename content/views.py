import json

import django_rq
import requests
from django.db.models import Case, When
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import rq_tasks
from .exceptions import ServiceUnavailable
from .models import Book
from .serializers import BookSerializer, ContentCSVSerializer


class BookAPIViewSet(ModelViewSet):

    def get_queryset(self):
        queryset = Book.objects.all()
        if self.action == 'list':
            user_interaction_response = requests.get("http://localhost:5000/interactions/top_contents")
            content_data = json.loads(user_interaction_response.content)
            if user_interaction_response.status_code == 200:
                content_ids = content_data['content_ids']
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(content_ids)])
                interacted_qs = queryset.filter(pk__in=content_ids).order_by(preserved)
                non_interacted_qs = queryset.exclude(pk__in=content_ids).order_by('id')
                return interacted_qs.union(non_interacted_qs)
            else:
                raise ServiceUnavailable()
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContentCSVSerializer
        else:
            return BookSerializer

    def perform_create(self, serializer):
        django_rq.enqueue(rq_tasks.create_content, serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_202_ACCEPTED, data={'detail': {"Task has been queued"}})