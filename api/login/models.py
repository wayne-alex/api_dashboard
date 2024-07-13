import uuid

from django.db import models


class Mobile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account_sid = models.UUIDField(default=uuid.uuid4, editable=False)
    account_type = models.CharField(max_length=10, default='Trial')
    account_balance = models.IntegerField(default=100)
    user_name = models.CharField(max_length=20, default='default')
    phone_number = models.IntegerField(null=True, blank=True)
    sni = models.CharField(max_length=10, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.account_sid.__str__()


class Transactions(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=20)


class Token(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=20)
    Token = models.UUIDField(editable=False)
