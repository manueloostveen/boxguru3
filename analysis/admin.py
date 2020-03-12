from django.contrib import admin

# Register your models here.
from analysis.models import Referral


class ReferralAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(Referral, ReferralAdmin)
# admin.site.register(Visitor)
# admin.site.register(VisitData)
# admin.site.register(UniqueVisitWeek)
# admin.site.register(UniqueVisitMonth)
# admin.site.register(SomeOneLanded)
# admin.site.register(WebRequest)

# class ReferralInline(admin.TabularInline):
#     model = Referral
#     fields = [('url')]
#
#
# class WebRequestInline(admin.TabularInline):
#     model = WebRequest
#     fields = [('get')]
#     extra = 0 # extra can be used to have blank entry fields at the bottom of the list for objects
#
#     # fk_name = 'session'
#
# @admin.register(Session)
# class SessionAdmin(admin.ModelAdmin):
#     list_display = [('session_id')]
#     inlines = [
#         WebRequestInline
#     ]
