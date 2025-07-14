import logging
from celery import shared_task
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Task

logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task
def send_task_notification(user_id, task_id, message):
    try:
        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)

        logger.info(f"Sending notification to {user.email}: {message}")

        send_mail(
            subject="Task Notification",
            message=f"{message} : {task.title}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,  # Prevents crashing if email sending fails
        )
        logger.info(f"Notification email sent successfully to {user.email}")

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found.")
    except Task.DoesNotExist:
        logger.error(f"Task with ID {task_id} not found.")
    except Exception as e:
        logger.error(f"Error in sending task notification: {str(e)}")
