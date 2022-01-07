from rest_framework import serializers
from .models import Book
import requests
import json


class BookListSerializer(serializers.ListSerializer):

    def validate(self, data):
        user_ids = {obj['user_id'] for obj in data}
        user_response = requests.post("http://127.0.0.1:8000/users/verify", data={'user_ids': user_ids})
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