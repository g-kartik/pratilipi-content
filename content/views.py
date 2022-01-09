import json

import django_rq
import requests
from django.db.models import Case, When
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from rest_framework.decorators import action

from . import rq_tasks
from .exceptions import ServiceUnavailable
from .models import Book
from .serializers import (BookSerializer, ContentCSVSerializer, ContentCSVStatusSerializer,
                          ContentCSVResponseSerializer, ContentCSVStatusResponseSerializer)
from environ import Env
from itertools import chain

env = Env()


@method_decorator(name='destroy', decorator=extend_schema(operation_id="Method deletes a book"))
@method_decorator(name='partial_update', decorator=extend_schema(operation_id="Method partially updates the "
                                                                                    "details of a book"))
@method_decorator(name='update', decorator=extend_schema(operation_id="Method updates the details of a book"))
@method_decorator(name='retrieve', decorator=extend_schema(operation_id="Method retrieves the details of a book"))
@method_decorator(name='list', decorator=extend_schema(operation_id="Method returns a list of books"))
@method_decorator(name='create', decorator=extend_schema(operation_id="Method creates a book",
                                                         responses={'200': ContentCSVResponseSerializer}))
class BookAPIViewSet(ModelViewSet):

    def get_queryset(self):
        queryset = Book.objects.all()
        if self.action == 'list':
            user_interaction_response = requests.get(f"{env('USER_INTERACTION_URL')}/interactions/top_contents")
            content_data = json.loads(user_interaction_response.content)
            if user_interaction_response.status_code == 200:
                content_ids = content_data['content_ids']
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(content_ids)])
                interacted_qs = queryset.filter(pk__in=content_ids).order_by(preserved)
                non_interacted_qs = queryset.exclude(pk__in=content_ids).order_by('id')
                return list(chain(interacted_qs, non_interacted_qs))
            else:
                raise ServiceUnavailable()
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContentCSVSerializer
        else:
            return BookSerializer

    def perform_create(self, serializer):
        job = django_rq.enqueue(rq_tasks.create_content, serializer.validated_data)
        return job.id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = self.perform_create(serializer)
        return Response(status=status.HTTP_202_ACCEPTED, data={'detail': {"Task has been queued"}, 'job_id': job_id})

    @extend_schema(operation_id="Method returns the status of the content upload job", description="Given the job id "
                   "of the content upload task, it returns the status of the job along with some message",
                   request=ContentCSVStatusSerializer, responses={'200': ContentCSVStatusResponseSerializer})
    @action(methods=['POST'], detail=False)
    def status(self, request):
        serializer = ContentCSVStatusSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = self._get_rq_response(queue="default", job_id=serializer.validated_data['job_id'])
            serializer = ContentCSVStatusResponseSerializer(data=response)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data)

    @staticmethod
    def _get_rq_response(queue, job_id):
        queue = django_rq.get_queue(queue)
        job = queue.fetch_job(job_id)
        if job is None or job.is_finished:
            response = {"state": "Finished"}
        elif job.is_queued:
            response = {"state": "Queued"}
        elif job.is_failed:
            response = {"state": "Failed", "message": job.exc_info}
        else:
            response = {"state": "Started"}
            if 'status' in job.meta:
                response['message'] = job.meta['status']
        return response