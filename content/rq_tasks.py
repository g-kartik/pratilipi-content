import io
from .serializers import  BookSerializer
import csv


def create_content(validated_data):
    csv_file = validated_data.get('csv_file')
    file_data = io.StringIO(csv_file.file.read().decode('utf-8'))
    csv_reader = csv.DictReader(file_data)
    book_serializer = BookSerializer(data=list(csv_reader), many=True)

    is_valid = True
    if book_serializer.is_valid():
        book_serializer.save()
        return book_serializer.data, is_valid
    else:
        is_valid = False
        return book_serializer.errors, is_valid
