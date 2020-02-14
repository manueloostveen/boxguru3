from django.contrib import admin

# Register your models here.
from analysis.models import Session, Referral, Visitor, VisitData

admin.site.register(Referral)
admin.site.register(Session)
admin.site.register(Visitor)
admin.site.register(VisitData)



class ReferralInline(admin.TabularInline):
    model = Referral
    fields = ('url')


class SessionAdmin(admin.ModelAdmin):
    inlines = [ReferralInline]
    # list_filter = ('company', 'product_type', 'wall_thickness', 'color', 'tags')


