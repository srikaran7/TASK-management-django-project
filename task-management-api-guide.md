# Building a Task Management API from Scratch

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Database Models](#database-models)
5. [Authentication System](#authentication-system)
6. [API Endpoints](#api-endpoints)
7. [Task Notifications](#task-notifications)
8. [Docker Setup](#docker-setup)
9. [Testing](#testing)
10. [Deployment](#deployment)

## Project Overview
This guide will help you build a Task Management API using Django and Django REST Framework. The API will include features like user authentication, project management, task management, and email notifications.

## Prerequisites
Before starting, ensure you have the following installed:
- Python 3.11 or higher
- Git
- Docker and Docker Compose
- A code editor (VS Code recommended)
- PostgreSQL (optional, SQLite will be used by default)

## Project Setup

### 1. Create Project Structure
```bash
# Create project directory
mkdir task-management-api
cd task-management-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install required packages
pip install django
pip install djangorestframework
pip install djoser
pip install drf-spectacular
pip install django-celery-beat
pip install django-celery-results
pip install redis
pip install gunicorn
pip install django-environ
```

### 2. Create Django Project
```bash
django-admin startproject core .
python manage.py startapp accounts
python manage.py startapp projects
python manage.py startapp tasks
```

### 3. Configure Settings
Create a `.env` file in the root directory:
```
DEBUG=True
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

Update `core/settings.py` with the following configurations:
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'djoser',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
    
    # Local apps
    'accounts',
    'projects',
    'tasks',
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## Database Models

### 1. Create Custom User Model
In `accounts/models.py`:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']
```

### 2. Create Project Model
In `projects/models.py`:
```python
from django.db import models
import uuid

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    members = models.ManyToManyField('accounts.User', related_name='project_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3. Create Task Model
In `tasks/models.py`:
```python
from django.db import models
import uuid

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    assigned_to = models.ManyToManyField('accounts.User', related_name='assigned_tasks')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Authentication System

### 1. Configure Djoser
In `core/settings.py`:
```python
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SERIALIZERS': {
        'user_create': 'accounts.serializers.UserCreateSerializer',
        'user': 'accounts.serializers.UserSerializer',
    },
}
```

### 2. Create User Serializers
In `accounts/serializers.py`:
```python
from rest_framework import serializers
from .models import User

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name')
```

## API Endpoints

### 1. Project Views
In `projects/views.py`:
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

### 2. Task Views
In `tasks/views.py`:
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user)
```

## Task Notifications

### 1. Configure Celery
Create `core/celery.py`:
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 2. Create Task Notification
In `tasks/tasks.py`:
```python
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_task_notification(user_email, task_title):
    subject = 'New Task Assignment'
    message = f'You have been assigned to the task: {task_title}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
```

## Docker Setup

### 1. Create Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 2. Create docker-compose.yml
```yaml
version: '3'

services:
  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - celery_worker
      - celery_beat

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A core worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A core beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
```

## Testing

### 1. Create Test Files
In `projects/tests.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Project

class ProjectTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            owner=self.user
        )

    def test_project_creation(self):
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.owner, self.user)
```

## Deployment

### 1. Production Settings
Create `core/settings_prod.py`:
```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Configure database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Deployment Steps
1. Set up a production server
2. Install required software (Python, PostgreSQL, Redis)
3. Configure environment variables
4. Run migrations
5. Collect static files
6. Set up Gunicorn
7. Configure Nginx
8. Set up SSL certificate

## Running the Project

1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies
4. Run migrations
5. Create superuser
6. Start the development server

```bash
# Clone repository
git clone <repository-url>
cd task-management-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## API Documentation

Access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Next Steps

1. Add more test cases
2. Implement frontend
3. Add more features
4. Improve documentation
5. Set up CI/CD
6. Add monitoring
7. Implement caching
8. Add rate limiting

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/) 