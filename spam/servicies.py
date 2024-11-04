from config.settings import CACHE_ENABLED
from django.core.cache import cache
from spam.models import Mailing, Message, Recipient


def get_mailing_from_cache():
    """Получает данные из кэша, если кэш пуст, получает данные из бд"""
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailing_list"
    mailings = cache.get(key)
    if mailings is not None:
        return mailings
    mailings = Mailing.objects.all()
    cache.set(key, mailings)
    return mailings


def get_message_from_cache():
    """Получает данные из кэша, если кэш пуст, получает данные из бд"""
    if not CACHE_ENABLED:
        return Message.objects.all()
    key = "message_list"
    messages = cache.get(key)
    if messages is not None:
        return messages
    messages = Message.objects.all()
    cache.set(key, messages)
    return messages


def get_recipient_from_cache():
    """Получает данные из кэша, если кэш пуст, получает данные из бд"""
    if not CACHE_ENABLED:
        return Recipient.objects.all()
    key = "recipient_list"
    recipients = cache.get(key)
    if recipients is not None:
        return recipients
    recipients = Recipient.objects.all()
    cache.set(key, recipients)
    return recipients


def get_products_by_category(category_name):
    """Получает продукты по имени категории из кэша или базы данных."""
    key = f"products_by_category_{category_name}"
    products = cache.get(key)

    if products is not None:
        return products

    products = list(Mailing.objects.filter(category__name=category_name))
    cache.set(key, products)

    return products
