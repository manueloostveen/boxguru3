from django.db import models

# Create your models here.
class Referral(models.Model):
    url = models.URLField(blank=True, null=True)
    domain = models.URLField(blank=True, null=True)
    sessionid = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.url)

#
# class Session(models.Model):
#     visitor = models.ForeignKey('Visitor', blank=True, null=True, on_delete=models.SET_NULL)
#     session_id = models.CharField(max_length=50)
#     referrals = models.ManyToManyField('Referral', blank=True)
#
#     def __str__(self):
#         return self.session_id
#
#
#
#
# class Visitor(models.Model):
#     ip = models.GenericIPAddressField(blank=True, null=True)
#
#     def __str__(self):
#         return self.ip
#
# class UniqueVisitWeek(models.Model):
#     ip = models.GenericIPAddressField()
#     week_number = models.PositiveIntegerField()
#     domain = models.URLField()
#     visit_data = models.ForeignKey('VisitData', on_delete=models.SET_NULL, null=True)
#
#     def __str__(self):
#         return self.ip + " " + str(self.week_number) + " " + str(self.domain)
#
# class UniqueVisitMonth(models.Model):
#     ip = models.GenericIPAddressField()
#     month_number = models.PositiveIntegerField()
#     domain = models.URLField()
#     visit_data = models.ForeignKey('VisitData', on_delete=models.SET_NULL, null=True)
#
#     def __str__(self):
#         return self.ip + " " + str(self.month_number) + " " + str(self.domain)
#
# class VisitData(models.Model):
#     domain = models.URLField(blank=True, null=True)
#     visits = models.PositiveIntegerField(blank=True, null=True, default=0)
#     unique_visitors = models.ManyToManyField(Visitor, blank=True)
#     unique_week_visits = models.ManyToManyField(UniqueVisitWeek, blank=True)
#     unique_month_visits = models.ManyToManyField(UniqueVisitMonth, blank=True)
#
#     def __str__(self):
#         return self.domain
#
#
# class Request(models.Model):
#     request = models.URLField()
#     visit = models.ForeignKey('BoxGuruVisit', on_delete=models.SET_NULL, null=True)
#
#
# class SearchQuery(models.Model):
#     request = models.URLField()
#     visit = models.ForeignKey('BoxGuruVisit', on_delete=models.SET_NULL, null=True)
#
#
# class BoxGuruVisit(models.Model):
#     session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
#     number_of_requests = models.PositiveIntegerField(default=0)
#     reached_referral = models.BooleanField(null=True)
#     visitor = models.GenericIPAddressField(null=True)
#
#     def __str__(self):
#         return self.visitor + 'did ' + str(self.number_of_requests) + 'requests'
#
#
# class BoxGuruVisitTotal(models.Model):
#     visits = models.PositiveIntegerField(blank=True, null=True, default=0)
#     unique_visitors = models.ManyToManyField(Visitor, blank=True)
#     unique_week_visits = models.ManyToManyField(UniqueVisitWeek, blank=True)
#     unique_month_visits = models.ManyToManyField(UniqueVisitMonth, blank=True)
#
# class WebRequest(models.Model):
#     time = models.DateTimeField(auto_now_add=True)
#     host = models.CharField(max_length=1000)
#     path = models.CharField(max_length=1000)
#     method = models.CharField(max_length=50)
#     uri = models.CharField(max_length=2000)
#     status_code = models.IntegerField()
#     user_agent = models.CharField(max_length=1000,blank=True,null=True)
#     remote_addr = models.GenericIPAddressField()
#     remote_addr_fwd = models.GenericIPAddressField(blank=True,null=True)
#     meta = models.TextField()
#     cookies = models.TextField(blank=True,null=True)
#     get = models.TextField(blank=True,null=True)
#     post = models.TextField(blank=True,null=True)
#     raw_post = models.TextField(blank=True,null=True)
#     is_secure = models.BooleanField()
#     is_ajax = models.BooleanField()
#     session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
#
# class SomeOneLanded(models.Model):
#     landed = models.BooleanField()
#     ip = models.GenericIPAddressField(null=True)
#
