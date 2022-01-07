FROM python:3.9.9-alpine3.14

MAINTAINER "G Karthik Raja"

# Set the working directory
WORKDIR /pratilipi/content

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate

