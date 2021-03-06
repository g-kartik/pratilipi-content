from rest_framework import serializers
from .models import Book
import requests
import json

from environ import Env

env = Env()


class BookListSerializer(serializers.ListSerializer):

    def validate(self, data):
        user_ids = {obj['user_id'] for obj in data}
        user_response = requests.post(f"{env('USER_URL')}/users/verify", data={'user_ids': user_ids})
        invalid_user_ids = json.loads(user_response.content)['invalid_user_ids']
        if invalid_user_ids:
            raise serializers.ValidationError({"invalid_user_ids": invalid_user_ids})
        return data


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['id', 'user_id', 'title', 'story', 'date_published']
        list_serializer_class = BookListSerializer
        extra_kwargs = {
            "user_id":
                {"write_only": True},
            "date_published":
                {"write_only": True}
        }

    def update(self, instance, validated_data):
        validated_data.pop('user_id', None)
        return super(BookSerializer, self).update(instance, validated_data)


class ContentCSVSerializer(serializers.Serializer):
    csv_file = serializers.FileField(allow_empty_file=False, write_only=True)

    def validate_csv_file(self, file):
        if not file.name.split('.')[-1] == 'csv':
            raise serializers.ValidationError('please upload a valid .csv file')
        return file


class ContentCSVResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(max_length=100)
    job_id = serializers.CharField(max_length=36)


class ContentCSVStatusSerializer(serializers.Serializer):
    job_id = serializers.CharField(max_length=36)


class ContentCSVStatusResponseSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=[
        "Queued", "Started", "Finished", "Failed"])
    message = serializers.CharField(allow_blank=True, default="")
    data = BookSerializer(many=True, default=[])