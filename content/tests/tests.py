from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.conf import settings


class ContentAPITestCase(APITestCase):

    def test_upload_csv_file(self):
        with open(settings.BASE_DIR / 'content/tests/test_content.csv', 'rb') as csv_file:
            response = self.client.post(reverse('content:book-list'), data={'csv_file': csv_file})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)