from django.contrib import admin
from .models import Mobile,Token,Transactions

# Register your models here.
admin.site.register(Mobile)
admin.site.register(Token)
admin.site.register(Transactions)