
# Simple Task Management API

This is a backend API for a task management application built using Django and Django Rest Framework (DRF). The project allows users to create and manage tasks and projects, assign members to projects, and track task statuses. It also includes user authentication and notifications through emails when tasks are assigned or updated.

## Features

- User authentication (Sign up, login)
- Project management (Create, update, delete projects)
- Task management (Create, update, delete tasks)
- Assigning members to projects and tasks
- Email notifications for task assignments and updates
- Celery for asynchronous task processing

## Technologies

- Django
- Django Rest Framework (DRF)
- Celery
- Redis
- Docker
- PostgreSQL

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Docker**: To run the project in containers.
- **Docker Compose**: For orchestrating multi-container Docker applications.

## Setup Instructions

Follow these steps to run the Task Management API on your local machine.

### 1. Clone the Repository

Clone this repository to your local machine using Git:

```bash
git clone https://github.com/TarekSaleh99/task-management-api.git
cd task-management-api
```

### 2. Set up Docker Containers

1. **Build and run the containers**:

   Run the following command in your terminal:

   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Docker images
   - Start the containers for the web service, Redis, Celery worker, and Celery beat.

2. **Run migrations**:

   Open a new terminal window and run the following command to apply the migrations:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create a superuser**:

   To create an admin user, run the following command:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

   Follow the prompts to create your superuser.

### 3. Run the API

Once your containers are up and running, the API will be accessible at:

- **API**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin`

### 4. Using the API

The Task Management API is organized into several key endpoints:

- **API-Documentation:**
  - `http://127.0.0.1:8000/api/docs/`
  
- **Notifications**: Notifications are sent via email when a task is assigned or updated.


## Docker Configuration

### `docker-compose.yml`

This file defines the services required to run the project:

- **web**: The main web service, runs the Django application using `gunicorn`.
- **redis**: A Redis service, used as a message broker for Celery.
- **celery_worker**: A Celery worker, processes asynchronous tasks.
- **celery_beat**: A Celery Beat service, schedules periodic tasks.

### `Dockerfile`

This file specifies how to build the Docker image for the web service:

- It uses the official Python 3.11 image.
- Installs dependencies from `requirements.txt`.
- Copies the project files into the container.
- Runs the Celery worker or beat based on the command given.

### 6. Environment Variables

Ensure you have the following environment variables set up in your `.env` file or directly in your Docker configuration:

```env
# Email settings for task notifications
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587

# Celery and Redis configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

You can modify these values based on your email service and other configurations.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
