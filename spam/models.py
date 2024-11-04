import logging

from config import settings
from django.core.mail import BadHeaderError, send_mail
from django.db import models
from django.utils import timezone
from users.models import CustomUser
from utils.logger import setup_logging

setup_logging()


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["full_name"]
        permissions = [
            ("can_view_all_recipients", "can view all recipients"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]
        permissions = [
            ("can_view_all_messages", "can view all messages"),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
    ]

    first_send_time = models.DateTimeField(null=True, blank=True, help_text="укажите время в формате 2023-10-01 12:00")
    end_time = models.DateTimeField(null=True, blank=True, help_text="укажите время в формате 2023-10-01 12:00")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Создана")
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"Рассылка {self.pk} - {self.status}"

    def send_mailing(self):
        """Отправка сообщений всем получателям и логирование попыток отправки"""
        user_stats, created = UserMailingStatistics.objects.get_or_create(user=self.owner)
        if self.is_blocked:
            logging.info(f"Рассылка {self.pk} заблокирована.")
            return

        if self.status != "Создана":
            logging.info(f"Начало выполнения задачи: {self.status}")
            return

        if self.status != "Запущена":
            self.status = "Запущена"
            self.start_datetime = timezone.now()
            self.save()

            recipients = self.recipients.all()
            success_count = 0
            for recipient in recipients:
                logging.info(f"Начало выполнения задачи: {recipient.email}")
                try:
                    send_mail(
                        subject=self.message.subject,
                        message=self.message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )

                    MailingAttempt.objects.create(
                        mailing=self,
                        status="Успешно",
                        server_response="Письмо отправлено успешно.",
                        attempt_datetime=timezone.now(),
                    )

                    success_count += 1
                    user_stats.update_statistics(success=True)

                except BadHeaderError as e:
                    logging.error(f"Ошибка отправки письма: {e}")
                    MailingAttempt.objects.create(
                        mailing=self,
                        status="Не успешно",
                        server_response=str(e),
                        attempt_datetime=timezone.now(),
                    )
                    user_stats.update_statistics(success=False)

                except Exception as e:
                    logging.error(f"Ошибка отправки письма: {e}")
                    MailingAttempt.objects.create(
                        mailing=self,
                        status="Не успешно",
                        server_response=str(e),
                        attempt_datetime=timezone.now(),
                    )
                    user_stats.update_statistics(success=False)

            if success_count == len(recipients):
                self.status = "Завершена"
            self.save()

    def block_mailing(self):
        self.is_blocked = True
        self.save()
        logging.info(f"Рассылка {self.pk} заблокирована пользователем {self.owner}")

    def unblock_mailing(self):
        self.is_blocked = False
        self.save()
        logging.info(f"Рассылка {self.pk} разблокирована пользователем {self.owner}")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all_mailings", "can view all mailings"),
            ("can_disable_mailings", "can disable mailings"),
        ]


class MailingAttempt(models.Model):
    ATTEMPT_STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]

    attempt_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ATTEMPT_STATUS_CHOICES)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"Попытка: {self.status} at {self.attempt_datetime}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытка рассылок"
        permissions = [
            ("can_view_all_mailings_attempts", "can view all mailings attempts"),
        ]


class UserMailingStatistics(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_mailings = models.PositiveIntegerField(default=0)
    successful_mailings = models.PositiveIntegerField(default=0)
    failed_mailings = models.PositiveIntegerField(default=0)

    def update_statistics(self, success):
        self.total_mailings += 1
        if success:
            self.successful_mailings += 1
        else:
            self.failed_mailings += 1
        self.save()
