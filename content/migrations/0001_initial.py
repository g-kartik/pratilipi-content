# Generated by Django 4.0.1 on 2022-01-06 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveIntegerField(db_index=True)),
                ('title', models.CharField(max_length=200)),
                ('story', models.TextField()),
                ('date_published', models.DateTimeField()),
            ],
        ),
    ]