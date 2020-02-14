from django.db import models

# Create your models here.

class Session(models.Model):
    visitor = models.ForeignKey('Visitor', blank=True, null=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=50)
    referrals = models.ManyToManyField('Referral', blank=True)

    def __str__(self):
        return self.session_id


class Referral(models.Model):
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return str(self.url)

class Visitor(models.Model):
    ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.ip

class VisitData(models.Model):
    domain = models.URLField(blank=True, null=True)
    visits = models.PositiveIntegerField(blank=True, null=True, default=0)
    unique_visitors = models.ManyToManyField(Visitor, blank=True)

    def __str__(self):
        return self.domain
