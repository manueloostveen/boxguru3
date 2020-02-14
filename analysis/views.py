from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Session, Referral, Visitor, VisitData


# Create your views here.
def save_clicked_link(request):

    # Save referral in database
    clicked_link = request.GET.get('link')
    referral, referral_created = Referral.objects.get_or_create(url=clicked_link)

    # Save visitor IP in database
    client_ip = request.META['REMOTE_ADDR']
    visitor, visitor_created = Visitor.objects.get_or_create(ip=client_ip)

    # Save session in database
    session, session_created = Session.objects.get_or_create(
        visitor=visitor,
        session_id=request.COOKIES.get('sessionid'),
    )

    # Add referral to session
    session.referrals.add(referral)

    # Save data to VisitData
    visit_data, visit_data_created = VisitData.objects.get_or_create(
        domain=clicked_link.split('/')[2]
    )
    visit_data.unique_visitors.add(visitor)
    visit_data.visits += 1
    visit_data.save()


    data = {
        'is_saved': True,
    }

    return HttpResponse()
