from django.db import models


class Book(models.Model):
    user_id = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=200)
    story = models.TextField()
    date_published = models.DateTimeField()
